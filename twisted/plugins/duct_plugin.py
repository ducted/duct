import yaml

from zope.interface import implementer
 
from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
 
import duct


class Options(usage.Options):
    optParameters = [
        ["config", "c", "duct.yml", "Config file"],
    ]
 

@implementer(IServiceMaker, IPlugin)
class DuctServiceMaker(object):
    tapname = "duct"
    description = "A monitoring and data-moving-around-places agent"
    options = Options
 
    def makeService(self, options):
        config = yaml.load(open(options['config']))
        return duct.makeService(config)
 
serviceMaker = DuctServiceMaker()
