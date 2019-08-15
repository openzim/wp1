#!/bin/sh

# Run cron
echo "Starting crond in the background"
cron

# Run the workers
echo "Starting supervisord in the foreground"
supervisord -c /usr/src/app/supervisord.conf -n
