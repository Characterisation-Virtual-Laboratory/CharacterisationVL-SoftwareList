#!/bin/bash

# Example on how to execute.
# listModules-massive.sh massive_modules.csv
OUTPUT=$1

#List the modules and output to temp file
module avail -l &> /tmp/modules.txt
#Remove the first 12 lines of the output, not relevant software modules, then remove the 'default' text.
sed '1,12d' /tmp/modules.txt | sed 's/default/       /' &> /tmp/modulesb.txt

echo "software,version,date_last_modified" > $OUTPUT

#Split the software and version number by the "/" delimiter, then print it (software,version,date_modified)
awk -F/ '{st = index($0,"/");print $1 "  " substr($0,st+1)}' < /tmp/modulesb.txt | awk '{print $1"," $2","$3}' >> $OUTPUT

