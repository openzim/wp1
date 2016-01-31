#!/bin/sh

jsub -l h_rt=30:00:00 -l h_vmem=2000m -N 'enwp10-upload' \
       -j y  -b y /data/project/enwp10/bin/upload-logged.sh  > /dev/null

#    -M cbm -m bae \

