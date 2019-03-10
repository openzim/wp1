#!/bin/bash

LANG="en_US.UTF-8"
export LANG

PDIR=/data/project/enwp10

FILE=$PDIR/Logs/`date +%Y-%m-%d.%H:%M.txt`

cd $PDIR/backend

export PERL5LIB=.

export
hostname
pwd
date

echo "Releases"
time ./download.pl --releases

echo "Reviews"
time ./download.pl --reviews

echo "Update 22 beta projects with new bot"
../lucky/venv/bin/python3 ../lucky/update.py --all --includefile=../project_list_22.txt

echo "Update all projects, except 22 beta projects"
time ./download.pl --all --excludefile ../project_list_22.txt

echo "Global table"
time ./mktable.pl --purge --mode global

date
