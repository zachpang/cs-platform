# syntax=docker/dockerfile:1

# dev
FROM node:16.8.0-buster-slim as dev

RUN npm install -g npm@latest

WORKDIR /app

COPY package*.json .
RUN npm install

COPY . .

# build
FROM dev as build-stage
RUN npm run build

# prod
FROM nginx:1.20.1 as prod
COPY --from=build-stage /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
