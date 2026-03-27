#!/bin/bash

# 1. Καθάρισμα παλιών διεργασιών (για να μην σου λέει "Port already in use")
echo "🧹 Καθαρίζω παλιά ports..."
fuser -k 8000/tcp 5173/tcp 2>/dev/null

# 2. Ενεργοποίηση Backend στο background
echo "🚀 Ξεκινάω το Backend (FastAPI)..."
cd backend
source venv/bin/activate
uvicorn main:app --reload & 
BACKEND_PID=$!

# 3. Αναμονή για να προλάβει να σηκωθεί το API
sleep 2

# 4. Ενεργοποίηση Frontend με εντολή για αυτόματο άνοιγμα browser
echo "⚛️ Ξεκινάω το Frontend (React/Vite)..."
cd ../frontend
export npm_config_cache=/tmp/sdi2300069_npm_cache

# Η παράμετρος --open λέει στο Vite να ανοίξει τον browser
npm run dev -- --open