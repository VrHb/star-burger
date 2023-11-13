#!/bin/bash

set -e

echo "Pulling changes from repository ..."
git pull origin main

echo "Run docker images ..."
docker-compose -f docker-compose.prod.yml build

echo "Build frontend ..."
docker run star-burger-front --name=web-frontend

echo "Start backend container ..."
docker-compose -f docker-compose.prod.yml up -d back

echo "Copy static files from container ..."
docker exec -it web-backend python manage.py collectstatic
docker cp -a web-backend:/usr/src/app/staticfiles/. staticfiles
docker cp -a web-frontend:/usr/src/app/bundles/. staticfiles
cp -r assets/* staticfiles

echo "Done!"
