export PATH=/usr/local/bin:$PATH
cd /usr/src/app
supervisorctl -c supervisord.conf restart wp1-upload:*
flock -n /run/lock/enqueue-all.cron.lock -c "python enqueue-all.py"
