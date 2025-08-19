#!/bin/bash

echo "🚀 Starting Call Center Analytics Platform"
echo "=========================================="
echo ""
echo "This will start:"
echo "  📊 n8n workflow engine on port 5678"
echo "  🌐 Streamlit app on port 8504"
echo ""
echo "n8n will start first, then Streamlit will wait for it to be ready"
echo ""

# Stop any existing containers
echo "🧹 Cleaning up existing containers..."
docker-compose down 2>/dev/null || true
docker rm -f callcenter_n8n callcenter_streamlit 2>/dev/null || true

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up --build -d

echo ""
echo "⏳ Waiting for services to start..."

# Wait for n8n to be ready
echo "📊 Waiting for n8n to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:5678 >/dev/null 2>&1; then
        echo "✅ n8n is ready!"
        break
    fi
    echo "   Attempt $i/30 - n8n starting..."
    sleep 2
done

# Wait for Streamlit to be ready
echo "🌐 Waiting for Streamlit to be ready..."
for i in {1..20}; do
    if curl -s http://localhost:8504/_stcore/health >/dev/null 2>&1; then
        echo "✅ Streamlit is ready!"
        break
    fi
    echo "   Attempt $i/20 - Streamlit starting..."
    sleep 2
done

echo ""
echo "🎉 Call Center Analytics Platform is ready!"
echo "=========================================="
echo ""
echo "🌐 Access your apps:"
echo "   📊 n8n:       http://localhost:5678"
echo "   🔍 Streamlit: http://localhost:8504"
echo ""
echo "📋 Quick commands:"
echo "   View logs:    docker-compose logs -f"
echo "   Stop all:     docker-compose down"
echo "   Restart:      docker-compose restart"
echo ""

# Open browser automatically
if command -v xdg-open > /dev/null; then
    echo "🌐 Opening Streamlit app in browser..."
    xdg-open http://localhost:8504
elif command -v open > /dev/null; then
    echo "🌐 Opening Streamlit app in browser..."
    open http://localhost:8504
fi

echo "✨ Ready to research companies!"
echo ""
echo "To stop the platform: docker-compose down"
