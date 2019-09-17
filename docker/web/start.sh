#!/bin/sh
export RQ_USER=$(head -n 1 app/rq-credentials.txt)
export RQ_PASS=$(tail -n 1 app/rq-credentials.txt)

cd app
gunicorn -b 0.0.0.0:6555 'wp1.web.app:create_app()'
