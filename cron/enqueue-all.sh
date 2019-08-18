export PATH=/usr/local/bin:$PATH
cd /usr/src/app
flock -n /run/lock/enqueue-all.cron.lock -c "python enqueue-all.py"
