class period_removable_lectures:

    def __init__(self, day, period, removable_lectures, removable_lectures_wcfa):
        self.day = day
        self.period = period
        # Potential Removable Lectures
        self.removable_lectures = removable_lectures
        self.removable_lectures_wcfa = removable_lectures_wcfa
        self.removable_lectures_count = len(removable_lectures)
        self.removable_lectures_wcfa_count = len(removable_lectures_wcfa)
