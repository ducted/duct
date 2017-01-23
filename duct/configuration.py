"""
.. module:: configuration
   :platform: Unix
   :synopsis: Configuration file parser

.. moduleauthor:: Colin Alston <colin@imcol.in>
"""

import os
import yaml
import itertools
import copy

from twisted.python import log

class ConfigurationError(Exception):
    pass

class ConfigFile(object):
    def __init__(self, path):
        if os.path.exists(path):
            with open(path, 'rt') as conf:
                self.raw_config = yaml.load(conf)
        else:
            raise Exception("Configuration file '%s' not found" % path)

        self.known_items = {
            'sources': list,
            'outputs': list,
            'interval': (float, int,),
            'ttl': (float, int,),
            'blueprint': list,
            'ssh_key': str,
            'ssh_user': str,
            'toolbox': dict
        }

        self._parse_config()

    def _validate_type(self, item, type):
        if not isinstance(type, tuple):
            type = (type, )
        
        parse = False
        for t in type:
            try:
                assert(isinstance(self.raw_config.get(item, t()), type))
                parse = True
            except AssertionError as e:
                pass
                
        if not parse:
            raise ConfigurationError("%s must be one of type %s" % (
                                     item, repr(type)))

    def _validate_config(self):
        for k,v in self.known_items.items():
            self._validate_type(k, v)

    def _parse_config(self):
        self._merge_includes()

        self._validate_config()

        self._build_blueprints()

    def _merge_includes(self):
        both = lambda i1, i2, t: isinstance(i1, t) and isinstance(i2, t)

        paths = self.raw_config.get('include_path', [])
        if not isinstance(paths, list):
            paths = [paths]

        for ipath in paths:
            if os.path.exists(ipath):
                files = [
                    os.path.join(ipath, f) for f in os.listdir(ipath)
                        if (f.endswith('.yml') or f.endswith('.yaml'))
                ]

                for f in files:
                    with open(f, 'rt') as yaml_path:
                        conf = yaml.load(yaml_path)
                        for k,v in conf.items():
                            if k in self.raw_config:
                                if both(v, self.raw_config[k], dict):
                                    # Merge dicts
                                    for k2, v2 in v.items():
                                        self.raw_config[k][k2] = v2

                                elif both(v, self.raw_config[k], list):
                                    # Extend lists
                                    self.raw_config[k].extend(v)
                                else:
                                    # Overwrite
                                    self.raw_config[k] = v
                            else:
                                self.raw_config[k] = v
                        log.msg(
                            'Loadded additional configuration from %s' % f)
            else:
                log.msg(
                    'Config Error: include_path %s does not exist' % ipath)

    def _build_blueprints(self):
        # Turn toolboxes into a dict
        toolboxes = self.raw_config.get('toolbox', {})
        blueprints = self.raw_config.get('blueprint', [])

        if blueprints:
            # Make sure raw config stubs exist if we have any blueprints
            if not 'sources' in self.raw_config:
                self.raw_config['sources'] = []

        for blueprint in blueprints:
            tbs = blueprint['toolbox']
            # Listify it so we can inherit multiple toolboxes
            if not isinstance(toolboxes, list):
                tbs = [tbs]

            tbs = [toolboxes[t] for t in tbs] 

            # Compute a dot product of all the config settings vectors
            inversions = []
            for k, v in blueprint.get('sets', {}).items():
                inversions.append([(k, j) for j in v])
                
            for options in itertools.product(*inversions):
                for toolbox in tbs:
                    for source in toolbox.get('sources', []):
                        # Make a copy of the source dict
                        mysource = copy.copy(source)

                        # Merge toolbox defaults
                        for k, v in toolbox.get('defaults', {}).items():
                            mysource[k] = v

                        # Merge blueprint defaults
                        for k, v in blueprint.get('defaults', {}).items():
                            mysource[k] = v

                        # Merge set permutation
                        for k, v in options:
                            mysource[k] = v

                        # Bolt it into our real config file
                        self.raw_config['sources'].append(mysource)

        # Free a tiny bit of memory
        if 'toolbox' in self.raw_config:
            del self.raw_config['toolbox']

        if 'blueprint' in self.raw_config:
            del self.raw_config['blueprint']

    def get(self, item, default=None):
        return self.raw_config.get(item, default)

    def __getitem__(self, item):
        return self.raw_config[item]
