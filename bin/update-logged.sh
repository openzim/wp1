#!/bin/bash

LANG="en_US.UTF-8"
export LANG

PDIR=/data/project/enwp10

FILE=$PDIR/Logs/update.`date +%Y-%m-%d_%H:%M.txt`

UPDATE=$PDIR/bin/update-all.sh

cd $PDIR/bin

/bin/date >> $FILE

$UPDATE >> $FILE 2>&1 

cd $PDIR/Logs

/bin/date >> $FILE

gzip -9 $FILE
