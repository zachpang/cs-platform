# syntax=docker/dockerfile:1

# build stage
FROM node:16.8.0-buster-slim as build-stage

RUN npm install -g npm@latest

WORKDIR /app

COPY package*.json .
RUN npm install

COPY . .

RUN npm run build

# production stage
FROM nginx:1.20.1

COPY --from=build-stage /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
