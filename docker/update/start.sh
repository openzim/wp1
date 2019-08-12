#!/bin/sh

# Update Cron
echo "Install Cron to daily schedule update jobs"
{ \
  echo "#!/bin/sh" ; \
  echo "/usr/bin/flock -w 0 /dev/shm/cron.lock python /usr/src/app/enqueue-all.py >>/dev/shm/schedule_updates.log 2>&1" ; \
} > /etc/cron.daily/schedule_updates && chmod +x /etc/cron.daily/schedule_updates

# Run the workers
echo "Starting supervisord in the foreground"
supervisord -c /usr/src/app/supervisord.conf -n
