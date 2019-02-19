#!/bin/bash

LANG="en_US.UTF-8"
export LANG

PDIR=/data/project/enwp10

FILE=$PDIR/Logs/`date +%Y-%m-%d.%H:%M.txt`

cd $PDIR/backend

export
hostname
pwd
date

echo "Releases"
time ./download.pl --releases

echo "Reviews"
time ./download.pl --reviews

echo "Update Catholicism project with new bot"
../lucky/venv/bin/python3 ../lucky/update_catholicism.py

echo "Update all projects, except Catholicism"
time ./download.pl --all --exclude=Catholicism

echo "Global table"
time ./mktable.pl --purge --mode global

date
