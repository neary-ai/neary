# Build stage
FROM node:lts-alpine as build-stage

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
COPY .env.docker .env

RUN npm run build

# Production stage
FROM nginx:stable-alpine as production-stage

COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf.template

EXPOSE 80

CMD /bin/sh -c "envsubst '\$BACKEND_SERVICE_ENDPOINT' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf && exec nginx -g 'daemon off;'"