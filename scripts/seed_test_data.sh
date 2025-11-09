#!/bin/bash

# Script pour alimenter la base de données avec des données de test
# Usage: ./seed_test_data.sh [--reset]

echo "🌱 Génération des données de test pour le développement frontend"
echo ""

# Vérifier si le flag --reset est passé
RESET_FLAG=""
if [ "$1" = "--reset" ]; then
    RESET_FLAG="--reset"
    echo "⚠️  Mode RESET activé - toutes les données existantes seront supprimées"
    read -p "Continuer ? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Annulé."
        exit 1
    fi
fi

# Exécuter le script de seed dans le container backend
docker compose exec backend python seed_data.py $RESET_FLAG

echo ""
echo "✅ Terminé !"
echo ""
echo "💡 Vous pouvez maintenant vous connecter au frontend avec:"
echo "   Email: alice@test.com"
echo "   Mot de passe: password123"
echo ""
