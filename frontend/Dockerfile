FROM node:17.6.0

WORKDIR /usr/app

COPY . .

RUN npm ci --include=dev

RUN ./node_modules/.bin/parcel watch bundles-src/index.js --dist-dir bundles --public-url="./"
