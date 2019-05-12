from random import randint
import random
import math

class operators:

    ###################### Removal operators #############################################

    def worst_courses_removal(schedule, destroy_limit, xmldata, penalties, selection_probability):
        print('worst_courses_removal')
        lectures_removed = []

        sorted_course_penalties = sorted(penalties.items(), key=lambda kv: kv[1], reverse=True)
        while destroy_limit > 0:
            courses_count = len(sorted_course_penalties)
            upsilon = random.random()
            index_for_removal = math.floor(courses_count * (upsilon ** selection_probability))
            a = sorted_course_penalties[index_for_removal]
            del sorted_course_penalties[index_for_removal]

            for i in range(xmldata.days):
                for j in range(xmldata.periods):
                    for k in range(len(xmldata.rooms)):
                        lecture = schedule[i][j][k]
                        if lecture == a[0]:
                            lectures_removed.append(lecture)
                            schedule[i][j][k] = ""
                            destroy_limit -= 1

        return schedule, lectures_removed

    def worst_curricula_removal(schedule, destroy_limit, xmldata, penalties, selection_probability):
        print('worst_curricula_removal')
        lectures_removed = []

        sorted_curriculum_penalties = sorted(penalties.items(), key=lambda kv: kv[1], reverse=True)
        while destroy_limit > 0:
            curricula_count = len(sorted_curriculum_penalties)
            upsilon = random.random()
            index_for_removal = math.floor(curricula_count * (upsilon ** selection_probability))
            a = sorted_curriculum_penalties[index_for_removal]
            del sorted_curriculum_penalties[index_for_removal]

            for i in range(xmldata.days):
                for j in range(xmldata.periods):
                    for k in range(len(xmldata.rooms)):
                        lecture = schedule[i][j][k]
                        if lecture != "":
                            curriculum = next((x for x in xmldata.curricula if x.id == a[0]), None)
                            course = next((c for c in curriculum.courses if c == lecture), None)
                            if course is not None:
                                lectures_removed.append(lecture)
                                schedule[i][j][k] = ""
                                destroy_limit -= 1

        return schedule, lectures_removed

    # The random destroy operator removes lectures from the schedule at random.
    def random_lecture_removal(schedule, destroy_limit, xmldata):
        print('random_lecture_removal')
        lectures_removed = []

        while destroy_limit > 0:
            day = randint(0, xmldata.days- 1)
            period = randint(0, xmldata.periods - 1)
            room = randint(0, len(xmldata.rooms) - 1)
            if schedule[day][period][room] != "":
                lectures_removed.append(schedule[day][period][room])
                schedule[day][period][room] = ""
                destroy_limit -= 1

        return schedule, lectures_removed

    # The random period destroy operator repetitively selects a day-period pair at random and
    # removes all its scheduled lectures
    def random_dayperiod_removal(schedule, destroy_limit, xmldata):
        print('random_dayperiod_removal')
        lectures_removed = []

        while destroy_limit > 0:
            day = randint(0, xmldata.days - 1)
            period = randint(0, xmldata.periods - 1)
            rooms_count = len(xmldata.rooms)
            for k in range(rooms_count):
                if destroy_limit == 0:
                    break
                if schedule[day][period][k] != "":
                    lectures_removed.append(schedule[day][period][k])
                    schedule[day][period][k] = ""
                    destroy_limit -= 1

        return schedule, lectures_removed

    # The roomday destroy operator repetitively removes all lectures that are assigned to a randomly
    # selected room on a randomly selected day.
    def random_roomday_removal(schedule, destroy_limit, xmldata):
        print('random_roomday_removal')
        lectures_removed = []

        while destroy_limit > 0:
            day = randint(0, xmldata.days - 1)
            room = randint(0, len(xmldata.rooms) - 1)

            for j in range(xmldata.periods):
                if destroy_limit == 0:
                    break
                if schedule[day][j][room] != "":
                    lectures_removed.append(schedule[day][j][room])
                    schedule[day][j][room] = ""
                    destroy_limit -= 1

        return schedule, lectures_removed

    # The teacher operator is used to ease restrictions regarding teacher conflicts. Teachers are
    # randomly selected and all of their lectures are removed from the schedule.
    def random_teacher_removal(schedule, destroy_limit, xmldata):
        print('random_teacher_removal')
        lectures_removed = []

        teachers = list(set([o.teacher_id for o in xmldata.courses]))

        while destroy_limit > 0:

            rand_teacher = random.choice(teachers)
            rooms_count = len(xmldata.rooms)

            for i in range(xmldata.days):
                for j in range(xmldata.periods):
                    for k in range(rooms_count):
                        lecture = schedule[i][j][k]
                        if lecture != "":
                            course = next((c for c in xmldata.courses if c.id == lecture), None)
                            if course is not None and course.teacher_id == rand_teacher:
                                lectures_removed.append(lecture)
                                schedule[i][j][k] = ""
                                destroy_limit -= 1

        return schedule, lectures_removed

    ###################### End of Removal operators #############################################

    ###################### Repair operators #############################################

    def repair_operator(schedule, lectures_removed):
        return schedule


    ###################### End of Repair operators #############################################
