# build stage
FROM node:lts-alpine as build-stage
WORKDIR /app
# corepack fetches the pnpm version pinned in package.json; the notice it
# prints about that is noise in a build log.
ENV COREPACK_ENABLE_DOWNLOAD_PROMPT=0
RUN corepack enable
COPY wp1-frontend/ .
RUN pnpm install --frozen-lockfile && pnpm run build

# production stage
FROM nginx:stable-alpine as production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY docker/frontend/gzip.conf /etc/nginx/conf.d/
COPY docker/frontend/default.conf /etc/nginx/conf.d/
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
