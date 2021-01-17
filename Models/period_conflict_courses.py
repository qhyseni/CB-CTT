class period_conflict_courses:

    def __init__(self, day, period, conflict_courses, conflict_courses_wcfa):
        self.day = day
        self.period = period
        # Potential Removable Lectures
        self.conflict_courses = conflict_courses
        self.conflict_courses_wcfa = conflict_courses_wcfa
        self.conflict_courses_count = len(conflict_courses)
        self.conflict_courses_wcfa_count = len(conflict_courses_wcfa)
