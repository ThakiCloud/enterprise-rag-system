#!/bin/bash

# Simple deployment script for Enterprise RAG System

set -e

echo "🚀 Starting Enterprise RAG System deployment..."

# Check if required environment variables are set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Error: OPENAI_API_KEY environment variable is required"
    exit 1
fi

# Build and start services
echo "📦 Building and starting services..."
cd infrastructure
docker-compose down --remove-orphans 2>/dev/null || true
docker-compose build --no-cache
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
if curl -f http://localhost:8000/health/ >/dev/null 2>&1; then
    echo "✅ Backend service is healthy"
else
    echo "❌ Backend service is not responding"
    docker-compose logs backend
    exit 1
fi

if curl -f http://localhost:8501/ >/dev/null 2>&1; then
    echo "✅ UI service is healthy"
else
    echo "❌ UI service is not responding"
    docker-compose logs ui
    exit 1
fi

echo "🎉 Deployment successful!"
echo "📍 Backend: http://localhost:8000"
echo "📍 Frontend: http://localhost:8501"
echo "📖 API Docs: http://localhost:8000/docs" 