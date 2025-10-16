#!/bin/bash
# Start Layer 3 production scraper

echo "Starting Layer 3 production scraper..."
docker exec -d n8n-scraper-app python /app/scripts/layer3_production_scraper.py --all

echo "✅ Layer 3 scraper started in background"
echo "Check progress with: docker logs -f n8n-scraper-app --tail 50"




