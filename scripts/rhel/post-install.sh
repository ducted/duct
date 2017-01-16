#!/bin/bash

if [ ! -d /etc/duct ]; 
then
    mkdir -p /etc/duct
    mkdir /etc/duct/conf.d
    cat >/etc/duct/duct.yml <<EOL
# Default event TTL
ttl: 60.0
# De-queue interval
interval: 1.0

outputs:
    - output: duct.outputs.logger.Logger

# Sources
sources:
    - service: load
      source: duct.sources.linux.basic.LoadAverage
      interval: 10.0

    - service: cpu
      source: duct.sources.linux.basic.CPU
      interval: 10.0
      critical: {
        cpu: "> 0.8"
      }

    - service: memory
      source: duct.sources.linux.basic.Memory
      interval: 10.0

include_path: /etc/duct/conf.d
EOL
fi

if [ ! -d /var/lib/duct ];
then
    mkdir -p /var/lib/duct
fi

chkconfig --add duct
service duct status >/dev/null 2>&1

if [ "$?" -gt "0" ];
then
    service duct start 2>&1
else
    service duct restart 2>&1
fi 

exit 0
