class Course:

    def __init__(self, id, teacherid, lectures, mindays, students, doublelectures):
        self._id = id
        self._teacherId = teacherid
        self._lectures = lectures
        self._minDays = mindays
        self._students = students
        self._doubleLectures = doublelectures

    def getId(self):
        return self._id

    def setId(self, value):
        self._id = value

    Id = property(getId, setId)

    def getTeacherId(self):
        return self._teacherId

    def setTeacherId(self, value):
        self._teacherId = value

    TeacherId = property(getTeacherId, setTeacherId)

    def getLectures(self):
        return self._lectures

    def setLectures(self, value):
        self._lectures = value

    Lectures = property(getLectures, setLectures)

    def getMinDays(self):
        return self._minDays

    def setMinDays(self, value):
        self._minDays = value

    MinDays = property(getMinDays, setMinDays)

    def getStudents(self):
        return self._students

    def setStudents(self, value):
        self._students = value

    Students = property(getStudents, setStudents)

    def getDoubleLectures(self):
        return self._doubleLectures

    def setDoubleLectures(self, value):
        self._doubleLectures = value

    DoubleLectures = property(getDoubleLectures, setDoubleLectures)