import json
import os
from redteamcore import Resource
from redteamcore import MBOX_CONNECTOR
from redteamcore import MBoxResouceConnector
from redteamcore import log as FRTLogger
class ResourceWithCache(Resource):

    def __init__(self, location, cache_location=None, tlsverify=True, resource_connector=None, transform_cls=None):

        super(ResourceWithCache, self).__init__(location, tlsverify, resource_connector, transform_cls)

        if cache_location:
            if self.connector_type == MBOX_CONNECTOR:
                self.cache = Resource(cache_location,
                                      resource_connector=MBoxResouceConnector(cache_location,
                                                                              tlsverify=tlsverify))
            else:
                self.cache = Resource(cache_location)
            if not os.path.isdir(self.cache_path):
                os.makedirs(self.cache_path)
        else:
            self.cache = None


    def configure_cache(self, cachepath):
        self.cache = Resource(cachepath)

    def delete_cache(self):
        FRTLogger.debug("Resource - deleting cache at %s", self.location)
        if self.cache:
            self.cache.delete()

    @property
    def location(self):
        if self.cache:
            return self.cache.location
        return self.connector.location

    @property
    def cache_path(self):
        if self.cache:
            return self.cache.filepath
        return ''

    def update(self):
        if self.cache:
            self.cache.delete()

        data = self.connector.open()

        if self.cache:
            self.cache.write(data)
        return data

    def read(self):
        data = None
        if self.cache and self.cache.exists:
            FRTLogger.debug("Resource - reading from cache %s", self.cache.location)
            data = self.cache.data
        else:
            data = self.update()
            FRTLogger.debug("Resource - reading from source %s", self.location)

        if isinstance(data, str):
            try:
                return json.loads(data)
            except ValueError:
                pass
        return data
