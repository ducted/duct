import time
import uuid
import json
from base64 import b64encode

from duct import utils

class OpenTSDBClient(object):
    """Twisted ElasticSearch API
    """
    def __init__(self, url='http://localhost:4242', user=None, password=None):
        self.url = url.rstrip('/')
        self.user = user
        self.password = password

    def _request(self, path, data=None, method='POST'):
        headers = {}
        if self.user:
            authorization = b64encode('%s:%s' % (self.user, self.password)).decode()
            headers['Authorization'] = ['Basic ' + authorization]

        return utils.HTTPRequest().getJson(
            self.url + path, method, headers=headers, data=data.encode())

    def put(self, data):
        return self._request('/api/put', json.dumps(data))
