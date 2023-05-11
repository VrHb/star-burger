#!/bin/bash

set -e 

echo "Pulling changes from repository ..."
git pull origin main

echo "Activating virtual environment ..."
source ./env/bin/activate

echo "Instaling js packets ..."
npm ci --dev

echo "Configure frontend ..."
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"

echo "Installing python libs ..."
pip install -r requirements.txt

echo "Making db operations ..."
python manage.py makemigrations --dry-run --check
python manage.py migrate --no-input

echo "Collecting static files ..."
python manage.py collectstatic --no-input

echo "Restarting app unit ..."
sudo systemctl restart star-burger.service

echo "Telling rollbar about deploy ..."
CODE_REVISION="$(git rev-parse --short HEAD)"
source .env
curl -H "X-Rollbar-Access-Token: $ROLLBAR_TOKEN" -H "Content-Type: application/json" -X POST 'https://api.rollbar.com/api/1/deploy' -d '{"environment": "'$ENVIRONMENT'", "payload": {"environment": "'$ENVIRONMENT'", "code_version": "'$(git rev-parse HEAD)'", "server": {"root": "file://users/VrHb/Documents/VrHb/star-burger/", "branch": "main"}}, "revision": "'$CODE_REVISION'", "rollbar_name": "star-burger", "local_username": "'$USER'", "comment": "Deployed", "status": "succeeded"}'

echo ""
echo "All done!"
