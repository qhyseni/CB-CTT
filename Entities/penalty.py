class penalty:

    def __init__(self, type):
        self._type = type

    def get_room_capacity_penalty (self):
        if self._type == 'UD2':
            return 1
        elif self._type == 'UD4':
            return 1

    room_capacity_penalty = property(get_room_capacity_penalty)

    def get_min_wdays_penalty (self):
        if self._type == 'UD2':
            return 5
        elif self._type == 'UD4':
            return 1

    min_wdays_penalty = property(get_min_wdays_penalty)

    def get_windows_penalty (self):
        if self._type == 'UD2':
            return None
        elif self._type == 'UD4':
            return 1

    windows_penalty = property(get_windows_penalty)

    def get_minmax_load_penalty(self):
        if self._type == 'UD2':
            return None
        elif self._type == 'UD4':
            return 1

    minmax_load_penalty = property(get_minmax_load_penalty)

    def get_double_lectures_penalty(self):
        if self._type == 'UD2':
            return None
        elif self._type == 'UD4':
            return 1

    double_lectures_penalty = property(get_double_lectures_penalty)

    def get_isolated_lectures_penalty(self):
        if self._type == 'UD2':
            return 2
        elif self._type == 'UD4':
            return None

    isolated_lectures_penalty = property(get_isolated_lectures_penalty)

    def get_room_stability_penalty(self):
        if self._type == 'UD2':
            return 1
        elif self._type == 'UD4':
            return None

    room_stability_penalty = property(get_room_stability_penalty)