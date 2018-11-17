class Curriculum:

    def __init__(self, id, courses):
        self._id = id
        self._courses = courses

    def getId(self):
        return self._id

    def setId(self, value):
        self._id = value

    Id = property(getId, setId)

    def getCourses(self):
        return self._courses

    def setCourses(self, value):
        self._courses = value

    Courses = property(getCourses, setCourses)
