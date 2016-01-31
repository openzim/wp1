#!/bin/sh


jsub -l h_rt=30:00:00 -l h_vmem=2000m -N 'enwp10-update' \
     -j y -b y /data/project/enwp10/bin/update-logged.sh >/dev/null 2>/dev/null

#     -m bae -M cbm \
