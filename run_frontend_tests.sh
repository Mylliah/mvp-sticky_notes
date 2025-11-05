#!/bin/bash

# Script pour lancer les tests frontend avec Docker Compose

set -e

echo "=================================================="
echo "🧪 LANCEMENT DES TESTS FRONTEND"
echo "=================================================="
echo ""

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd "$(dirname "$0")"

# Vérifier que Docker est en cours d'exécution
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker n'est pas en cours d'exécution"
    exit 1
fi

echo -e "${BLUE}📦 Installation des dépendances de test...${NC}"
docker compose exec -T frontend npm install

echo ""
echo -e "${BLUE}🧪 Exécution des tests unitaires...${NC}"
docker compose exec -T frontend npm test -- --run

echo ""
echo -e "${BLUE}📊 Génération du rapport de couverture...${NC}"
docker compose exec -T frontend npm run test:coverage -- --run

echo ""
echo -e "${GREEN}✅ Tests frontend terminés !${NC}"
echo ""
echo "📁 Rapport de couverture disponible dans: frontend/coverage/"
echo "=================================================="
