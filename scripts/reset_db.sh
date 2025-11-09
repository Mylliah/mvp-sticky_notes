#!/bin/bash

# Script de nettoyage de la base de données de test
# Recrée les tables pour repartir à zéro

echo "🧹 Nettoyage de la base de données..."

# Redémarrer les containers pour reset la DB SQLite
cd /home/mynh/mvp-sticky_notes
docker compose down
docker compose up -d

echo "⏳ Attente du démarrage de l'API..."
sleep 5

# Vérifier que l'API répond
if curl -s http://localhost:5000/health | grep -q "ok"; then
    echo "✅ API prête !"
else
    echo "❌ API non disponible"
    exit 1
fi

echo "🎉 Base de données nettoyée et prête pour les tests"
