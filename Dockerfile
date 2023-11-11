FROM python:3.11.4-slim-buster

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip install --no-cache-dir -U pip

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py makemigrations --dry-run --check

RUN python manage.py migrate --no-input

