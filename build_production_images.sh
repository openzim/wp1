#!/bin/bash
set -e

docker build -f web.Dockerfile -t openzim/wp1bot-web .
docker build -f workers.Dockerfile -t openzim/wp1bot-workers .
docker build -f frontend.Dockerfile -t openzim/wp1bot-frontend .
docker push openzim/wp1bot-web:latest
docker push openzim/wp1bot-workers:latest
docker push openzim/wp1bot-frontend:latest
