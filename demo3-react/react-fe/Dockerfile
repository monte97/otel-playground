# Stage 1: Build the React app
FROM node:20-alpine AS build

WORKDIR /app

# Copy only the React app folder
COPY react-fe-app/package.json ./
RUN npm install

COPY react-fe-app ./
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Copy build output from previous stage
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
