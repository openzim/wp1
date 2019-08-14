#!/bin/sh
USER=$(head -n 1 app/rq-credentials.txt)
PASS=$(tail -n 1 app/rq-credentials.txt)

rq-dashboard --username $USER --password $PASS -H redis
