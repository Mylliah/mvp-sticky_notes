#!/bin/bash

# Script pour exécuter TOUS les tests du projet avec Docker Compose
# et générer un rapport de score complet

set -e

echo "=================================================="
echo "🧪 LANCEMENT DE TOUS LES TESTS - MVP STICKY NOTES"
echo "=================================================="
echo ""

# Couleurs pour l'output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Créer un fichier de résultats
RESULTS_FILE="test_results_$(date +%Y%m%d_%H%M%S).txt"
echo "📝 Résultats sauvegardés dans: $RESULTS_FILE"
echo ""

# Fonction pour afficher les résultats
log_result() {
    echo "$1" | tee -a "$RESULTS_FILE"
}

log_result "=================================================="
log_result "RAPPORT DE TESTS - $(date)"
log_result "=================================================="
log_result ""

# S'assurer que les conteneurs sont démarrés
echo -e "${BLUE}🚀 Démarrage des conteneurs Docker...${NC}"
docker compose up -d db backend
echo ""

# Attendre que la DB soit prête
echo -e "${BLUE}⏳ Attente de la base de données...${NC}"
sleep 10
echo ""

# ============================================
# TESTS BACKEND
# ============================================
log_result "============================================"
log_result "📦 TESTS BACKEND (Python/Flask)"
log_result "============================================"
log_result ""

echo -e "${YELLOW}🔍 Analyse de la structure des tests...${NC}"
echo ""

# Compter les fichiers de tests
TOTAL_TEST_FILES=$(docker compose exec -T backend find tests -name "test_*.py" | wc -l)
log_result "Nombre total de fichiers de tests: $TOTAL_TEST_FILES"
log_result ""

# Catégories de tests
log_result "📂 Structure des tests:"
log_result "  - Tests unitaires (models/): $(docker compose exec -T backend find tests/models -name "test_*.py" 2>/dev/null | wc -l) fichiers"
log_result "  - Tests d'intégration (routes/): $(docker compose exec -T backend find tests/routes -name "test_*.py" 2>/dev/null | wc -l) fichiers"
log_result "  - Tests E2E: $(docker compose exec -T backend find tests/e2e -name "test_*.py" 2>/dev/null | wc -l) fichiers"
log_result "  - Tests de sécurité: $(docker compose exec -T backend find tests -maxdepth 1 -name "test_*.py" 2>/dev/null | wc -l) fichiers"
log_result ""

# ============================================
# EXÉCUTION DES TESTS UNITAIRES
# ============================================
echo -e "${GREEN}✨ Exécution des tests UNITAIRES (models/)...${NC}"
log_result "--------------------------------------------"
log_result "🧩 TESTS UNITAIRES (Models)"
log_result "--------------------------------------------"

if docker compose exec -T backend pytest tests/models/ -v --tb=short 2>&1 | tee -a "$RESULTS_FILE"; then
    log_result "✅ Tests unitaires: SUCCÈS"
else
    log_result "❌ Tests unitaires: ÉCHEC"
fi
log_result ""

# ============================================
# EXÉCUTION DES TESTS D'INTÉGRATION
# ============================================
echo -e "${GREEN}✨ Exécution des tests D'INTÉGRATION (routes/)...${NC}"
log_result "--------------------------------------------"
log_result "🔗 TESTS D'INTÉGRATION (Routes/API)"
log_result "--------------------------------------------"

if docker compose exec -T backend pytest tests/routes/ -v --tb=short 2>&1 | tee -a "$RESULTS_FILE"; then
    log_result "✅ Tests d'intégration: SUCCÈS"
else
    log_result "❌ Tests d'intégration: ÉCHEC"
fi
log_result ""

# ============================================
# EXÉCUTION DES TESTS E2E
# ============================================
echo -e "${GREEN}✨ Exécution des tests E2E (end-to-end)...${NC}"
log_result "--------------------------------------------"
log_result "🌐 TESTS E2E (Workflows complets)"
log_result "--------------------------------------------"

if docker compose exec -T backend pytest tests/e2e/ -v --tb=short 2>&1 | tee -a "$RESULTS_FILE"; then
    log_result "✅ Tests E2E: SUCCÈS"
else
    log_result "❌ Tests E2E: ÉCHEC"
fi
log_result ""

# ============================================
# EXÉCUTION DES TESTS DE SÉCURITÉ
# ============================================
echo -e "${GREEN}✨ Exécution des tests DE SÉCURITÉ...${NC}"
log_result "--------------------------------------------"
log_result "🔒 TESTS DE SÉCURITÉ"
log_result "--------------------------------------------"

if docker compose exec -T backend pytest tests/test_security_isolation.py tests/test_decorators_edge_cases.py tests/test_email_validation.py tests/test_unique_constraints.py -v --tb=short 2>&1 | tee -a "$RESULTS_FILE"; then
    log_result "✅ Tests de sécurité: SUCCÈS"
else
    log_result "❌ Tests de sécurité: ÉCHEC"
fi
log_result ""

# ============================================
# RAPPORT DE COUVERTURE
# ============================================
echo -e "${BLUE}📊 Génération du rapport de couverture...${NC}"
log_result "============================================"
log_result "📊 COUVERTURE DE CODE"
log_result "============================================"

docker compose exec -T backend pytest tests/ --cov=app --cov-report=term-missing --cov-report=html 2>&1 | tee -a "$RESULTS_FILE"
log_result ""

# ============================================
# TESTS COMPLETS (Tous ensemble)
# ============================================
echo -e "${YELLOW}🎯 Exécution de TOUS les tests ensemble...${NC}"
log_result "============================================"
log_result "🎯 SUITE COMPLÈTE DE TESTS"
log_result "============================================"

if docker compose exec -T backend pytest tests/ -v --tb=short --maxfail=5 2>&1 | tee -a "$RESULTS_FILE"; then
    TEST_STATUS="✅ TOUS LES TESTS PASSENT"
    TEST_COLOR="${GREEN}"
else
    TEST_STATUS="❌ CERTAINS TESTS ÉCHOUENT"
    TEST_COLOR="${RED}"
fi

log_result ""
log_result "============================================"
log_result "$TEST_STATUS"
log_result "============================================"
log_result ""

# ============================================
# CALCUL DU SCORE FINAL
# ============================================
echo -e "${BLUE}📈 Calcul du score final...${NC}"
log_result "============================================"
log_result "🏆 SCORE FINAL"
log_result "============================================"

# Extraire les statistiques
TOTAL_TESTS=$(grep -oP '\d+(?= passed)' "$RESULTS_FILE" | tail -1)
FAILED_TESTS=$(grep -oP '\d+(?= failed)' "$RESULTS_FILE" | tail -1 || echo "0")
COVERAGE=$(grep -oP 'TOTAL.*\K\d+(?=%)' "$RESULTS_FILE" | tail -1 || echo "0")

log_result ""
log_result "📊 Statistiques:"
log_result "  - Tests réussis: ${TOTAL_TESTS:-0}"
log_result "  - Tests échoués: ${FAILED_TESTS:-0}"
log_result "  - Couverture de code: ${COVERAGE:-0}%"
log_result ""

# Calcul du score (sur 100)
if [ -n "$TOTAL_TESTS" ] && [ "$TOTAL_TESTS" -gt 0 ]; then
    SUCCESS_RATE=$(echo "scale=2; (${TOTAL_TESTS} - ${FAILED_TESTS}) * 100 / ${TOTAL_TESTS}" | bc)
    FINAL_SCORE=$(echo "scale=2; (${SUCCESS_RATE} * 0.7) + (${COVERAGE:-0} * 0.3)" | bc)
    
    log_result "🎯 Taux de réussite: ${SUCCESS_RATE}%"
    log_result ""
    log_result "╔════════════════════════════════════╗"
    log_result "║   SCORE FINAL: ${FINAL_SCORE}/100   ║"
    log_result "╚════════════════════════════════════╝"
else
    log_result "❌ Impossible de calculer le score"
fi

log_result ""
log_result "============================================"
log_result "📁 Fichiers générés:"
log_result "  - Rapport texte: $RESULTS_FILE"
log_result "  - Couverture HTML: backend/htmlcov/index.html"
log_result "============================================"

echo ""
echo -e "${TEST_COLOR}$TEST_STATUS${NC}"
echo ""
echo -e "${BLUE}✅ Rapport complet généré: $RESULTS_FILE${NC}"
echo -e "${BLUE}📊 Couverture HTML disponible: backend/htmlcov/index.html${NC}"
echo ""
echo "=================================================="
echo "🎉 ANALYSE TERMINÉE"
echo "=================================================="
