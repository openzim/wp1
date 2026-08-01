FROM node:lts-alpine

WORKDIR /app

# corepack fetches the pnpm version pinned in package.json; the notice it
# prints about that is noise in a build log.
ENV COREPACK_ENABLE_DOWNLOAD_PROMPT=0
RUN corepack enable

COPY wp1-frontend/package.json wp1-frontend/pnpm-lock.yaml wp1-frontend/pnpm-workspace.yaml ./

RUN pnpm install --frozen-lockfile


EXPOSE 5173

CMD ["pnpm", "dev", "--host", "0.0.0.0"]
