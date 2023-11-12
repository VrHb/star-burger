#!/bin/bash

set -e

echo "Pulling changes from repository ..."
git pull origin main

echo "Run docker containers ..."
docker-compose -f docker-compose.prod.yml up -d --build

echo "Copy static files from container ..."
docker-compose run back python manage.py collectstatic
docker cp -a web-backend:/usr/src/app/staticfiles/. staticfiles
docker cp -a web-frontend:/usr/src/app/bundles/. staticfiles
cp -r assets/* staticfiles
docker stop web-frontend

echo "Done!"
