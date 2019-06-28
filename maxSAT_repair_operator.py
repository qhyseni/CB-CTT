import subprocess
import os
from configs import configs
import uuid
import sys
from subprocess import Popen, PIPE, STDOUT
import time


class maxSAT:

    def solve(instance_data, lectures):

        partial_temp_filename = '/tmp/partial' + str(uuid.uuid4())
        try:
            os.remove(partial_temp_filename)
        except OSError:
            pass
        with open(partial_temp_filename, 'a+') as f:
            print('')

            for lecture_data in lectures:
                f.write(lecture_data)

        print('maxSAT process START')
        with open('my-stdout.txt', 'w') as logfile:
            process = subprocess.Popen(
                ['java', '-jar',
                 configs.jar_path,
                 configs.datasets_dir + configs.instance_name,
                 partial_temp_filename,
                 configs.cbctt_dir + configs.output_name,
                 configs.sbps_path,
                 configs.maxsat_timeout], stdout=logfile)
            # sys.stdout.flush()
            # rc = process.communicate()
        # sys.stdout.flush()

            rc = process.wait()
            logfile.flush()

            time.sleep(2)
            # print('rc:'+str(rc))
            print('maxSAT process END')

        print('maxSAT Output file read START')
        schedule = [[["" for k in range(len(instance_data.rooms))] for j in range(instance_data.periods_per_day)] for i in
                    range(instance_data.days)]
        with open(configs.cbctt_dir + configs.output_name, "r") as content:
            for line in content:
                values = line.rstrip('\n').split(' ')
                if values != ['']:
                    day = int(values[2])
                    period = int(values[3])
                    room = instance_data.rooms.index(next((i for i in instance_data.rooms if i.id == values[1]), None))
                    schedule[day][period][room] = values[0]

        print('maxSAT Output file read END')
        return schedule



