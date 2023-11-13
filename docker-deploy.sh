#!/bin/bash

set -e

echo "Pulling changes from repository ..."
git pull origin main

echo "Run docker containers ..."
docker-compose -f docker-compose.prod.yml --build up -d

echo "Copy static files from container ..."
docker exec -it web-backend python manage.py collectstatic
docker cp -a web-backend:/usr/src/app/staticfiles/. staticfiles
docker cp -a web-frontend:/usr/src/app/bundles/. staticfiles

echo "Done!"
