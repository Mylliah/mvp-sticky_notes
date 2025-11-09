#!/bin/bash

echo "🔍 Recherche des services locaux à tuer..."

# Tuer Flask
FLASK_PIDS=$(ps aux | grep -E "flask run" | grep mynh | grep -v grep | awk '{print $2}')
if [ -n "$FLASK_PIDS" ]; then
    echo "🔪 Arrêt de Flask (PIDs: $FLASK_PIDS)"
    kill -9 $FLASK_PIDS 2>/dev/null
else
    echo "✅ Aucun Flask local trouvé"
fi

# Tuer Vite/npm sur ports 3000/3001
VITE_PIDS=$(ps aux | grep -E "vite.*300[01]" | grep mynh | grep -v grep | awk '{print $2}')
if [ -n "$VITE_PIDS" ]; then
    echo "🔪 Arrêt de Vite (PIDs: $VITE_PIDS)"
    kill -9 $VITE_PIDS 2>/dev/null
else
    echo "✅ Aucun Vite local trouvé"
fi

# Attendre un peu
sleep 1

# Vérifier les ports
echo ""
echo "📊 Vérification des ports..."
PORT_5000=$(ss -tlnp 2>/dev/null | grep ":5000" | grep -v docker-proxy)
PORT_3001=$(ss -tlnp 2>/dev/null | grep ":3001" | grep -v docker-proxy)

if [ -n "$PORT_5000" ]; then
    echo "⚠️  Port 5000 encore occupé (non-Docker):"
    echo "$PORT_5000"
else
    echo "✅ Port 5000 libre (ou Docker)"
fi

if [ -n "$PORT_3001" ]; then
    echo "✅ Port 3001: Docker frontend"
else
    echo "⚠️  Port 3001 libre"
fi

echo ""
echo "🐳 État des conteneurs Docker:"
docker compose ps

echo ""
echo "✅ Nettoyage terminé ! Rechargez votre navigateur avec Ctrl+Shift+R"
