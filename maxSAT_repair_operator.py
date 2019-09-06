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
            # print('')

            for lecture_data in lectures:
                f.write(lecture_data)

        output_file = configs.cbctt_dir + configs.output_name + str(uuid.uuid4())

        # print(configs.instance_name)
        with open('my-stdout.txt', 'w') as logfile:
            print('maxSAT process START')
            process = subprocess.Popen(
                ['java', '-jar',
                 configs.jar_path,
                 configs.datasets_dir + configs.instance_name,
                 partial_temp_filename,
                 output_file,
                 configs.sbps_path,
                 configs.maxsat_timeout
                 ], stdout=logfile, stderr=logfile)

            try:
                rc = process.communicate(timeout=30)
            except:
                process.kill()
                print("timeout timeout timeout timeout timeout timeout timeout")

            process.kill()

        # sys.stdout.flush()

            # rc = process.wait()
            logfile.flush()

            # print('rc:'+str(rc))
            print('maxSAT process END')

        if os.path.exists(output_file):
            # print('maxSAT Output file read START')
            schedule = [[["" for k in range(len(instance_data.rooms))] for j in range(instance_data.periods_per_day)] for i in
                        range(instance_data.days)]
            with open(output_file, "r") as content:
                for line in content:
                    values = line.rstrip('\n').split(' ')
                    if values != ['']:
                        day = int(values[2])
                        period = int(values[3])
                        room = instance_data.rooms.index(next((i for i in instance_data.rooms if i.id == values[1]), None))
                        schedule[day][period][room] = values[0]

            os.remove(output_file)

        # print('maxSAT Output file read END')
            return schedule
        else:
            return None



