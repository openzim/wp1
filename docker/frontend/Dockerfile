# build stage
FROM node:lts-alpine as build-stage
WORKDIR /app
COPY wp1-frontend/ .
RUN yarn install --production && yarn run build

# production stage
FROM nginx:stable-alpine as production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY docker/frontend/gzip.conf /etc/nginx/conf.d/
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
