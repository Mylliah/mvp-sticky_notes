#!/bin/bash

# Script complet pour réinitialiser et alimenter la base de données
# Usage: ./reset_and_seed.sh

echo "🔄 Réinitialisation complète de la base de données..."
echo ""

# 1. Supprimer toutes les tables
echo "1️⃣  Suppression des tables existantes..."
docker compose exec backend python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.drop_all(); print('✅ Tables supprimées')"

# 2. Appliquer les migrations
echo ""
echo "2️⃣  Application des migrations..."
docker compose exec backend flask db upgrade

# 3. Générer les données de test
echo ""
echo "3️⃣  Génération des données de test..."
docker compose exec backend python seed_data.py

echo ""
echo "🎉 Base de données réinitialisée et prête pour le développement !"
echo ""
