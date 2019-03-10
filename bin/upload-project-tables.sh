#!/bin/bash

LANG="en_US.UTF-8"
export LANG

PDIR=/data/project/enwp10

FILE=$PDIR/Logs/upload.`date +%Y-%m-%d.%H:%M.txt`

cd $PDIR/backend

export PERL5LIB=.

pwd
hostname
export

echo "PID $$"

echo "@@ copy_tables --project"
time ./copy_tables.pl --project

echo "@@ copy_tables --global"
time ./copy_tables.pl --global

echo "@@ copy_tables --custom"
time ./copy_tables.pl --custom

echo "@@ copy_count"
time ./copy_count.pl --global

# Disabled 5-25-2011 due to high replag, CBM
# Re-enabled 6-3-2011
# Disabled 7-12-2012 due to high replag, CBM
echo "@@ copy_logs"
time ./copy_logs.pl --all
