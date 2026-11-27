FROM node:27.0.0-alpha.0.1.0-alpine3.24 AS builder

WORKDIR /web

COPY package.json ./
COPY package-lock.json* ./

RUN --mount=type=cache,target=/root/.npm npm ci

COPY . .

RUN npm run build

FROM nginxinc/nginx-unprivileged:stable-alpine AS production

COPY --from=builder /web/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]