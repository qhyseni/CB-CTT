import subprocess
import os
import uuid
from Experiments.configs import configs
from Experiments.statistics import statistics


class maxSAT:

    def solve(schedule, instance_data, lectures_removed):
        print("Max-SAT Operator")
        statistics.maxsat_count += 1

        Uc = []
        # prepare formatted input for max-SAT tool
        rows = []

        for i in range(instance_data.days):
            for j in range(instance_data.periods_per_day):
                for k in range(instance_data.rooms_count):
                    if schedule[i][j][k] != -1:
                        row = instance_data.courses_ids[schedule[i][j][k]] + " " + instance_data.rooms[k].id + " " + str(i) + " " + str(
                            j) + '\n'
                        rows.append(row)

        for lecture in lectures_removed:
            row = instance_data.courses_ids[lecture] + " " + "-1" + " " + "-1" + " " + "-1" + '\n'
            rows.append(row)

        # write formatted input to a file to be used by the next process (max-SAT)
        # partial_temp_filename = 'C:/Users/vlere/AppData/Local/Temp/partial' + str(uuid.uuid4())
        partial_temp_filename = '/tmp/partial' + str(uuid.uuid4())
        try:
            os.remove(partial_temp_filename)
        except OSError:
            pass
        # with open(partial_temp_filename, 'w+') as f:
        with open(partial_temp_filename, 'a+') as f:

            for row in rows:
                f.write(row)

        # file where the output will be written to
        # output_file = 'C:/Users/vlere/AppData/Local/Temp/output' + str(uuid.uuid4()) + '.txt'
        output_file = configs.cbctt_dir + configs.output_name + str(uuid.uuid4())

        # start process to execute Max-SAT
        with open('my-stdout.txt', 'w+') as logfile:
            process = subprocess.Popen(
                [
                    # 'cmd', 'java', '-jar',
                'java', '-jar',
                 configs.jar_path,
                 configs.datasets_dir + configs.instance_name,
                 partial_temp_filename,
                 output_file,
                 configs.sbps_path,
                 configs.maxsat_timeout
                 ], stdout=logfile, stderr=logfile)

            try:
                rc = process.communicate(timeout=(int(configs.maxsat_timeout)/1000)+10)
            except:
                process.kill()
                print("TIMEOUT...TIMEOUT...TIMEOUT...TIMEOUT...TIMEOUT...TIMEOUT...")

            process.kill()

        # sys.stdout.flush()

            # rc = process.wait()
            logfile.flush()

        if os.path.exists(output_file):
            schedule = [[[-1 for k in range(len(instance_data.rooms))] for j in range(instance_data.periods_per_day)] for i in
                        range(instance_data.days)]
            with open(output_file, "r") as content:
                for line in content:
                    values = line.rstrip('\n').split(' ')
                    if values != ['']:
                        day = int(values[2])
                        period = int(values[3])
                        room = instance_data.rooms.index(next((i for i in instance_data.rooms if i.id == values[1]), None))
                        schedule[day][period][room] = instance_data.courses_ids.index(values[0])

            os.remove(output_file)

            return schedule, Uc
        else:
            return None, Uc



