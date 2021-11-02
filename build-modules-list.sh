#!/bin/bash

#Output the list of modules
./opt/modules-to-google/listModules-massive.sh /opt/modules-to-google/massive_modules.csv

source /opt/modules-to-google/bin/activate
modules-to-google --config /opt/modules-to-google/etc/config.yml
