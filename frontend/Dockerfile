FROM node:16 AS build-stage

WORKDIR /app

# 安装依赖
COPY package*.json ./
RUN npm install

# 复制项目文件并构建
COPY . .
RUN npm run build

# 生产环境
FROM nginx:stable-alpine AS production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
