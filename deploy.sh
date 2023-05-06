#!/bin/bash

set -e 

echo "Pulling changes from repository ..."
git pull origin main

echo "Creating .env file ..."
ENVFILE=".env"
touch $ENVFILE

echo "Generating django secret key ..."
SECRET_KEY=`openssl rand -base64 48`
echo SECRET_KEY=\"$SECRET_KEY\" >> $ENVFILE

echo "Disable debug settings ..."
echo DEBUG=0 >> $ENVFILE

echo "Create static files env value for collectstatic ..."
echo STATIC_DIR_NAME=staticfiles >> $ENVFILE

echo "Add host to ALLOWED_HOSTS env ..."
echo "ALLOWED_HOSTS=$1" >> $ENVFILE

echo "Creating virtual environment ..."
python -m venv env
source ./env/bin/activate

echo "Installing js packet managers ..."
sudo apt install nodejs
sudo apt install npm

echo "Instaling js packets ..."
npm ci --dev

echo "Configure frontend ..."
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"

echo "Installing python libs ..."
pip install -r requirements.txt

echo "Making db operations ..."
python manage.py makemigrations
python manage.py migrate

echo "Collecting static files ..."
python manage.py collectstatic

echo "Restarting app unit ..."
sudo systemctl restart star-burger.service


echo "Telling rollbar about deploy ..."
source .env
curl -H "X-Rollbar-Access-Token: $ROLLBAR_TOKEN" -H "Content-Type: application/json" -X POST 'https://api.rollbar.com/api/1/deploy' -d '{"environment": "$ENVIRONMENT", "revision": "dc1f74dee5", "rollbar_name": star-burger, "local_username": $USER, "comment": "Deployed", "status": "succeeded"}'

echo "All done!"
