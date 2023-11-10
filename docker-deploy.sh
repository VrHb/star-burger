#!/bin/bash

set -e

echo "Pulling changes from repository ..."
git pull origin main

echo "Run docker containers ..."
docker-compose build && docker-compose up -d

echo "Copy static files from container ..."
docker cp -a web-frontend:/usr/app/bundles staticfiles
docker cp -a web-backend:/usr/src/app/staticfiles staticfiles

echo "Restart backend ..."
docker restart web-backend

echo "Done!"
