from random import randint
import random
import math

class operators:

    ###################### Removal operators #############################################

    def worst_courses_removal(schedule, destroy_limit, xmldata, penalties, selection_probability):
        lectures_removed = []

        sorted_course_penalties = sorted(penalties.items(), key=lambda kv: kv[1], reverse=True)
        courses_count = len(sorted_course_penalties)
        while destroy_limit > 0:
            upsilon = random.random()
            index_for_removal = math.floor(courses_count * (upsilon ** selection_probability))
            a = sorted_course_penalties[index_for_removal]
            del sorted_course_penalties[index_for_removal]

            for i in range(xmldata.days()):
                for j in range(xmldata.periods()):
                    for k in range(len(xmldata.rooms)):
                        lecture = schedule[i][j][k]
                        if lecture != 0 and lecture[1] == a[0]:
                            lectures_removed.append(lecture)
                            schedule[i][j][k] = 0
            destroy_limit -= 1

        return schedule, lectures_removed

    def worst_curricula_removal(schedule, destroy_limit, xmldata, penalties, selection_probability):
        lectures_removed = []

        sorted_curriculum_penalties = sorted(penalties.items(), key=lambda kv: kv[1], reverse=True)
        curricula_count = len(sorted_curriculum_penalties)
        while destroy_limit > 0:
            upsilon = random.random()
            index_for_removal = math.floor(curricula_count * (upsilon ** selection_probability))
            a = sorted_curriculum_penalties[index_for_removal]
            del sorted_curriculum_penalties[index_for_removal]

            for i in range(xmldata.days()):
                for j in range(xmldata.periods()):
                    for k in range(len(xmldata.rooms())):
                        lecture = schedule[i][j][k]
                        if lecture != 0 and lecture[0] == a[0]:
                            lectures_removed.append(lecture)
                            schedule[i][j][k] = 0
            destroy_limit -= 1

        return schedule, lectures_removed

    # The random destroy operator removes lectures from the schedule at random.
    def random_lecture_removal(schedule, destroy_limit, xmldata, penalties, selection_probability):
        lectures_removed = []

        while destroy_limit > 0:
            day = randint(0, xmldata.days() - 1)
            period = randint(0, xmldata.periods() - 1)
            room = randint(0, len(xmldata.rooms()) - 1)
            if schedule[day][period][room] != 0:
                lectures_removed.append(schedule[day][period][room])
                schedule[day][period][room] = 0
                destroy_limit -= 1

        return schedule, lectures_removed

    # The random period destroy operator repetitively selects a day-period pair at random and
    # removes all its scheduled lectures
    def random_dayperiod_removal(schedule, destroy_limit, xmldata, penalties, selection_probability):
        lectures_removed = []

        while destroy_limit > 0:
            day = randint(0, xmldata.days() - 1)
            period = randint(0, xmldata.periods() - 1)
            rooms_count = len(xmldata.rooms())
            for k in range(rooms_count):
                if destroy_limit == 0:
                    break
                if schedule[day][period][k] != 0:
                    lectures_removed.append(schedule[day][period][k])
                    schedule[day][period][k] = 0
                    destroy_limit -= 1

        return schedule, lectures_removed

    # The roomday destroy operator repetitively removes all lectures that are assigned to a randomly
    # selected room on a randomly selected day.
    def random_roomday_removal(schedule, destroy_limit, xmldata, penalties, selection_probability):
        lectures_removed = []

        while destroy_limit > 0:
            day = randint(0, xmldata.Days - 1)
            room = randint(0, len(xmldata.Rooms) - 1)

            for j in range(xmldata.PeriodsPerDay):
                if destroy_limit == 0:
                    break
                if schedule[day][j][room] != 0:
                    lectures_removed.append(schedule[day][j][room])
                    schedule[day][j][room] = 0
                    destroy_limit -= 1

        return schedule, lectures_removed

    # The teacher operator is used to ease restrictions regarding teacher conflicts. Teachers are
    # randomly selected and all of their lectures are removed from the schedule.
    def random_teacher_removal(schedule, destroy_limit, xmldata, penalties, selection_probability):
        lectures_removed = []

        teachers = list(set([o.TeacherId for o in xmldata.Courses]))

        while destroy_limit > 0:

            rand_teacher = random.choice(teachers)
            rooms_count = len(xmldata.Rooms)

            for i in range(xmldata.Days):
                for j in range(xmldata.PeriodsPerDay):
                    for k in range(rooms_count):
                        lecture = schedule[i][j][k]
                        if lecture != 0 and lecture[2] == rand_teacher:
                            lectures_removed.append(lecture)
                            schedule[i][j][k] = 0

                destroy_limit -= 1

        return schedule, lectures_removed

    ###################### End of Removal operators #############################################

