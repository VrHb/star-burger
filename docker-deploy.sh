#!/bin/bash

set -e

echo "Pulling changes from repository ..."
git pull origin main

echo "Run docker containers ..."
docker-compose build && docker-compose up -d

echo "Copy static files from container ..."
docker cp web-frontend:/usr/app/bundles staticfiles
docker cp web-backend:/usr/src/app/staticfiles staticfiles
