#!/bin/bash
# slfn-business-os-deploy.sh - One-click deployment script

# 1. Stop and remove all containers/volumes
docker compose down -v --rmi all

# 2. Build and start fresh containers
docker compose up -d --build

# 3. Wait for services to initialize
sleep 15

# 6. Verify backend health
if curl -s http://localhost:8081/docs >/dev/null 2>&1; then
  echo "✅ Backend API is running"
else
  echo "❌ Backend API not responding"
  exit 1
fi

# 7. Verify frontend is accessible
if curl -s http://localhost:3002/ > /dev/null; then
  echo "✅ Frontend is running"
else
  echo "❌ Frontend not running"
  exit 1
fi

# 7. Test auth flow (simulated)
echo "✅ System ready: Backend API available at http://localhost:8081"
echo "🔒 Auth endpoints: /api/v1/auth/register, /api/v1/auth/login"
echo "🚀 SLFN Business OS is ready for use!"