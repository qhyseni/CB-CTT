import collections
import json
from redteamcore import Resource

class TransformableDict(collections.MutableMapping):
    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.update(dict(*args, **kwargs))  # use the free update to set keys

    def __getitem__(self, key):
        return self.store[self.__keytransform__(key)]

    def __setitem__(self, key, value):
        self.store[self.__keytransform__(key)] = value

    def __delitem__(self, key):
        del self.store[self.__keytransform__(key)]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __keytransform__(self, key):
        return key

    def json(self):
        return json.dumps(dict(self), indent=4, sort_keys=True)

    def xml(self):
        pass

    def html(self):
        pass



class SaveableLoadableDict(TransformableDict, Resource):

    def __init__(self, *args, **kwargs):

        TransformableDict.__init__(self, *args, **kwargs)
        try:
            location = kwargs.pop('location')
            try:
                logger = kwargs.pop('logger')
            except KeyError:
                logger = None
            Resource.__init__(self, location, logger=logger, transform_cls=JSONTransformableDictEncoder)

        except KeyError:
            pass

        try:
            self.name = kwargs['name']
        except KeyError:
            pass

    def __setitem__(self, key, value):
        self.store[self.__keytransform__(key)] = value

        if self.__keytransform__(key) == 'name':
            self.name = value

    # pylint: disable=E0202,W0221
    def write(self):
        if self.location.endswith('.json'):
            Resource.write(self, dict(self))
        elif self.location.endswith('.html'):
            Resource.write(self, self.html())
        elif self.location.endswith('.xml'):
            Resource.write(self, self.xml())

class JSONTransformableDictEncoder(json.JSONEncoder):
    def default(self, obj): # pylint: disable=E0202,W0221
        if isinstance(obj, TransformableDict):
            return dict(obj)
        return json.JSONEncoder.default(self, obj)
