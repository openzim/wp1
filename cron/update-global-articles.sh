#!/bin/bash

export PATH=/usr/local/bin:$PATH
cd /usr/src/app

exec 200>/run/lock/update-global-articles.cron.lock
flock -n 200 || exit 1

supervisorctl -c supervisord.conf stop wp1-update:*
python update-global-articles.py
supervisorctl -c supervisord.conf start wp1-update:*
