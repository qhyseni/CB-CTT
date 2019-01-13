class course:

    def __init__(self, id, teacher_id, lectures, min_days, students, double_lectures):
        self.id = id
        self.teacher_id = teacher_id
        self.lectures = lectures
        self.min_days = min_days
        self.students = students
        self.double_lectures = double_lectures

    # id = property()
    #
    # teacher_id = property()
    #
    # lectures = property()
    #
    # min_days = property()
    #
    # students = property()
    #
    # double_lectures = property()