#!/bin/bash

echo "🔥 NETTOYAGE BRUTAL ET DÉFINITIF"
echo "=================================="
echo ""

# 1. Arrêter TOUS les conteneurs Docker
echo "1️⃣  Arrêt des conteneurs Docker..."
docker compose down
sleep 2

# 2. Tuer TOUS les Flask
echo "2️⃣  Arrêt de TOUS les Flask locaux..."
pkill -9 -f "flask run"
sleep 1

# 3. Tuer TOUS les processus Python du projet
echo "3️⃣  Arrêt des processus Python du projet..."
pkill -9 -f "python.*mvp-sticky"
pkill -9 -f "wsgi"
sleep 1

# 4. Vérifier qu'il ne reste rien
echo "4️⃣  Vérification..."
FLASK_COUNT=$(ps aux | grep -E "flask run" | grep -v grep | wc -l)
if [ "$FLASK_COUNT" -gt 0 ]; then
    echo "⚠️  Il reste $FLASK_COUNT processus Flask!"
    ps aux | grep -E "flask run" | grep -v grep
else
    echo "✅ Aucun Flask local"
fi

# 5. Relancer Docker proprement
echo ""
echo "5️⃣  Redémarrage propre de Docker..."
docker compose up -d

echo ""
echo "6️⃣  Attente du démarrage (10s)..."
sleep 10

# 7. Vérification finale
echo ""
echo "7️⃣  État final:"
docker compose ps
echo ""
echo "Port 5000:"
ss -tlnp 2>/dev/null | grep ":5000"
echo ""

echo "=================================="
echo "✅ NETTOYAGE TERMINÉ"
echo ""
echo "👉 Maintenant:"
echo "   1. Fermez TOUS les terminaux VS Code sauf celui-ci"
echo "   2. Rechargez le navigateur avec Ctrl+Shift+R"
echo "   3. Connectez-vous"
echo ""
echo "🔍 Pour vérifier la DB:"
echo "   docker compose exec db psql -U app -d appdb -c 'SELECT username FROM users;'"
echo "=================================="
