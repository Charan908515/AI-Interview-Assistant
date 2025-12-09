
# Stage 1: Build the React App
FROM node:18-alpine AS build
WORKDIR /app

# Install dependencies
COPY package*.json ./
 RUN npm install

# Copy source code
COPY . .

# Build for production
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Copy the nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy the built files from build stage
COPY --from=build /app/build /usr/share/nginx/html

# Copy build output from Vite
#COPY --from=build /app/dist /usr/share/nginx/html/

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
