#!/bin/sh

cd app
gunicorn -b 0.0.0.0:6555 'wp1.web.app:create_app()'
