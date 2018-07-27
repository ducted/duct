"""
.. module:: prometheus
   :synopsis: Prometheus output

.. moduleauthor:: Colin Alston <colin@imcol.in>
"""


import json
import base64

from twisted.internet import defer
from twisted.internet import reactor, endpoints
from twisted.web.server import Site
from twisted.web.resource import Resource

from duct.objects import Output

from duct.utils import HTTPRequest

class PrometheusResource(Resource):
    isLeaf = True
    addSlash = False

    def __init__(self, output):
        Resource.__init__(self)
        self.output = output

    def render_metrics(self):
        content = ""
        for k,v in self.output.metric_table.items():
            # Need better handling of float/int values
            content += "%s %s\n" % (k, v)
        return content

    def render_GET(self, request):
        if request.path == "/" + self.output.metric_path:
            return self.render_metrics()

        body = """<html><head><title>Duct</title></head>
                  <body><h1>Duct</h1><p>"<a href="/%s">Metrics</a></p>
                  </body></html>""" % self.output.metric_path

        return body

class Prometheus(Output):
    """Prometheus output

    **Configuration arguments:**

    :param port: Listening port (default: 9100)
    :type port: int.
    :param metric_path: Metrics path (default: metrics)
    :type metric_path: str.
    :param prefix: Prometheus metric prefix (default: duct_)
    :type prefix: str.
    """
    def __init__(self, *a):
        Output.__init__(self, *a)

        self.port = int(self.config.get('port', 9100))
        self.metric_path = self.config.get('metric_path', 'metrics')
        self.prefix = self.config.get('prefix', 'duct_')
        
        self.metric_table = {}

    def createClient(self):
        self.resource = PrometheusResource(self)
        site = Site(self.resource)
        endpoint = endpoints.TCP4ServerEndpoint(reactor, self.port)
        endpoint.listen(site)

    def eventsReceived(self, events):
        for event in events:
            metric_name = self.prefix + event.service.replace('.', '_')
            if event.attributes:
                metric_name += "{%s}" % ','.join(
                    ['%s=%s' % (k, v) for k, v in event.attributes.items()]
                )
            self.metric_table[metric_name] = event.metric
