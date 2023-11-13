FROM node:17.6.0

WORKDIR /usr/src/app

COPY . .

RUN npm ci --include=dev

RUN ./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"

