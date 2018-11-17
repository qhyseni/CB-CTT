from redteamcore import Resource
from redteamcore import MBoxResouceConnector
class MBoxResource(Resource):
    def __init__(self, location, tlsverify=True):
        resource_connector = MBoxResouceConnector(location, tlsverify=True)
        super(MBoxResource, self).__init__(location, tlsverify=tlsverify, resource_connector=resource_connector)
