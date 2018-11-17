class Room:

    def __init__(self, id, size, building):
        self._id = id
        self._size = size
        self._building = building

    def getId(self):
        return self._id

    def setId(self, value):
        self._id = value

    Id = property(getId, setId)


    def getSize(self):
        return self._size

    def setSize(self, value):
        self._size = value

    Size = property(getSize, setSize)


    def getBuilding(self):
        return self._building

    def setBuilding(self, value):
        self._building = value

    Building = property(getBuilding, setBuilding)