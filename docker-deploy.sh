#!/bin/bash

set -e

echo "Pulling changes from repository ..."
git pull origin main

echo "Activating virtual environment ..."
source ./env/bin/activate

echo "Run docker containers ..."
docker-compose buld && docker-compose up -d

echo "Copy static files from container ..."
docker cp web-frontend:/usr/app/bundles staticfiles
docker cp web-backend:/usr/src/app/staticfiles staticfiles
