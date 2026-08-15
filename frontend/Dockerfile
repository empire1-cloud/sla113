FROM node:20-slim AS build

WORKDIR /app

COPY package.json yarn.lock* ./
RUN yarn install --frozen-lockfile || yarn install

COPY . .

# Production API origin is intentionally sourced from frontend/.env.production.
# Do not inject the frontend's own custom domain here: that causes auth requests
# such as /api/auth/signup to hit nginx/static hosting instead of FastAPI.
RUN yarn build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
