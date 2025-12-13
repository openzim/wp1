FROM node:lts-alpine

WORKDIR /app

RUN corepack enable

COPY wp1-frontend/package.json wp1-frontend/yarn.lock ./

RUN yarn install


EXPOSE 5173

CMD ["yarn", "dev", "--host", "0.0.0.0"]
