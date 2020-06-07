class penalty:

    def __init__(self, type):
        self._type = type

    def get_room_capacity_penalty (self):
        if self._type == 'UD2':
            return 1
        elif self._type == 'UD4':
            return 1

    P_CAP = property(get_room_capacity_penalty)

    def get_min_wdays_penalty (self):
        if self._type == 'UD2':
            return 5
        elif self._type == 'UD4':
            return 1

    P_DAYS = property(get_min_wdays_penalty)

    def get_windows_penalty (self):
        if self._type == 'UD2':
            return None
        elif self._type == 'UD4':
            return 1

    P_WIND = property(get_windows_penalty)

    def get_minmax_load_penalty(self):
        if self._type == 'UD2':
            return None
        elif self._type == 'UD4':
            return 1

    P_LOAD = property(get_minmax_load_penalty)

    def get_double_lectures_penalty(self):
        if self._type == 'UD2':
            return None
        elif self._type == 'UD4':
            return 1

    P_DOUBLE = property(get_double_lectures_penalty)

    def get_isolated_lectures_penalty(self):
        if self._type == 'UD2':
            return 2
        elif self._type == 'UD4':
            return None

    P_COMP = property(get_isolated_lectures_penalty)

    def get_room_stability_penalty(self):
        if self._type == 'UD2':
            return 1
        elif self._type == 'UD4':
            return None

    P_STAB = property(get_room_stability_penalty)