import subprocess
import os


class maxSAT:

    def solve(instance_data, lectures):

        try:
            os.remove('/tmp/partial')
        except OSError:
            pass
        with open('/tmp/partial', 'a+') as f:
            print('')

            for lecture_data in lectures:
                f.write(lecture_data)

        subprocess.check_output(
            ['java', '-jar',
             '/home/administrator/Downloads/cb-ctt.jar',
             '/home/administrator/Documents/thesis/datasets/comp01.ectt',
             '/tmp/partial',
             '/home/administrator/Documents/thesis/cb-ctt/output.txt',
             '/home/administrator/Documents/thesis/cb-ctt/Open-LinSBPS_static', '1000'])

        schedule = [[["" for k in range(len(instance_data.rooms))] for j in range(instance_data.periods)] for i in
                    range(instance_data.days)]
        with open('/home/administrator/Documents/thesis/cb-ctt/output.txt', "r") as content:
            for line in content:
                values = line.rstrip('\n').split(' ')
                if values != ['']:
                    day = int(values[2])
                    period = int(values[3])
                    room = instance_data.rooms.index(next((i for i in instance_data.rooms if i.id == values[1]), None))
                    schedule[day][period][room] = values[0]

        return schedule



