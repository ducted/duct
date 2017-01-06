#!/bin/bash

if [ ! -d /etc/duct ]; 
then
    mkdir -p /etc/duct
    cat >/etc/duct/duct.yml <<EOL
# Default event TTL
ttl: 60.0
# De-queue interval
interval: 1.0

# TCP Output
outputs:
    - output: duct.outputs.riemann.RiemannTCP
      server: 127.0.0.1
      port: 5555

# Sources
sources:
    - service: load
      source: duct.sources.linux.basic.LoadAverage
      interval: 2.0

    - service: cpu
      source: duct.sources.linux.basic.CPU
      interval: 2.0
      critical: {
        cpu: "> 0.8"
      }

    - service: memory
      source: duct.sources.linux.basic.Memory
      interval: 2.0
EOL
fi

if [ ! -d /var/lib/duct ];
then
    mkdir -p /var/lib/duct
fi

update-rc.d duct defaults
service duct status >/dev/null 2>&1

if [ "$?" -gt "0" ];
then
    service duct start 2>&1
else
    service duct restart 2>&1
fi 

exit 0
