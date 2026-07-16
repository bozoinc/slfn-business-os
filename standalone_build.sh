#!/bin/bash
# Standalone frontend build script for SLFN Business OS

set -euo pipefail

FRONTEND_DIR="/home/bozo/projects/slfn-business-os/frontend"
BACKEND_DIR="/home/bozo/projects/slfn-business-os/backend"

# Step 1: Check current directory and files
echo "=== STEP 1: Directory Check ==="
pwd
cd "$FRONTEND_DIR"
ls -la

# Step 2: Ensure nginx.conf is correct
echo -e "\n=== STEP 2: nginx.conf ==="
if [ ! -f "nginx.conf" ]; then
    echo "Creating nginx.conf..."
    cat > nginx.conf << 'EOF'
server {
    listen 80;
    server_name localhost;

    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF
    echo "Created new nginx.conf"
else
    echo "nginx.conf exists, checking structure..."
    head -10 nginx.conf
fi

# Step 3: Update frontend Dockerfile
echo -e "\n=== STEP 3: Updating Dockerfile ==="
cat > Dockerfile << 'EOF'
FROM node:18-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

# Create proper nginx.conf
RUN mkdir -p /etc/nginx/conf.d/ && \
    echo 'server {' > /etc/nginx/conf.d/default.conf && \
    echo '    listen 80;' >> /etc/nginx/conf.d/default.conf && \
    echo '    server_name localhost;' >> /etc/nginx/conf.d/default.conf && \
    echo '' >> /etc/nginx/conf.d/default.conf && \
    echo '    location / {' >> /etc/nginx/conf.d/default.conf && \
    echo '        root /usr/share/nginx/html;' >> /etc/nginx/conf.d/default.conf && \
    echo '        index index.html;' >> /etc/nginx/conf.d/default.conf && \
    echo '        try_files $uri $uri/ /index.html;' >> /etc/nginx/conf.d/default.conf && \
    echo '    }' >> /etc/nginx/conf.d/default.conf && \
    echo '' >> /etc/nginx/conf.d/default.conf && \
    echo '    location /api/ {' >> /etc/nginx/conf.d/default.conf && \
    echo '        proxy_pass http://backend:8000;' >> /etc/nginx/conf.d/default.conf && \
    echo '        proxy_set_header Host $host;' >> /etc/nginx/conf.d/default.conf && \
    echo '        proxy_set_header X-Real-IP $remote_addr;' >> /etc/nginx/conf.d/default.conf && \
    echo '    }' >> /etc/nginx/conf.d/default.conf && \
    echo '}' >> /etc/nginx/conf.d/default.conf

RUN npm run build

FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY --from=build /etc/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
EOF

# Step 4: Clear existing docker resources
echo -e "\n=== STEP 4: Clearing Docker Resources ==="
if docker ps -a | grep -q slfn-business-os; then
    echo "Stopping and removing existing slfn-business-os containers..."
    docker compose down -v 2>/dev/null || docker stop $(docker ps -a | grep slfn-business-os | awk '{print $1}') 2>/dev/null || true
    docker rm -f $(docker ps -a | grep slfn-business-os | awk '{print $1}') 2>/dev/null || true
fi

# Step 5: Update and build
echo -e "\n=== STEP 5: Update and Build ==="
docker compose up -d --build

# Step 6: Check status
echo -e "\n=== STEP 6: Status Check ==="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Step 7: Check logs
echo -e "\n=== STEP 7: Frontend Logs ==="
docker logs slfn-business-os-frontend

# Step 8: Test access
echo -e "\n=== STEP 8: Access Test ==="
sleep 5
docker logs slfn-business-os-frontend

if curl -s http://localhost:3002/ > /dev/null 2>&1; then
    echo "✅ Frontend is accessible!"
    echo "UI should be available at: http://localhost:3002/"
else
    echo "❌ Frontend is not accessible yet"
    echo "Let's check logs..."
    docker logs slfn-business-os-frontend
    echo "\nLet's also check if the container is running:"
    docker ps slfn-business-os-frontend
fi