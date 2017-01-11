import time
import json
import datetime

from twisted.internet import reactor, defer, task
from twisted.python import log

try:
    from OpenSSL import SSL
    from twisted.internet import ssl
except:
    SSL=None

from duct.objects import Output
from duct.protocol.opentsdb import OpenTSDBClient

from duct.outputs import opentsdb

class Bosun(opentsdb.OpenTSDB):
    """Bosun HTTP API output

    **Configuration arguments:**

    :param url: URL (default: http://localhost:4242)
    :type url: str
    :param maxsize: Maximum queue backlog size (default: 250000, 0 disables)
    :type maxsize: int
    :param maxrate: Maximum rate of documents added to index (default: 100)
    :type maxrate: int
    :param interval: Queue check interval in seconds (default: 1.0)
    :type interval: int
    :param user: Optional basic auth username
    :type user: str
    :param password: Optional basic auth password
    :type password: str
    :param debug: Log tracebacks from OpenTSDB
    :type debug: str
    """
    def __init__(self, *a):
        OpenTSDB.__init__(self, *a)

