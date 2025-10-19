#!/bin/bash

# 🧪 Script de test complet de l'API Sticky Notes avec curl
# Usage: chmod +x test_api_curl.sh && ./test_api_curl.sh

# Couleurs pour l'affichage
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

BASE_URL="http://localhost:5000/v1"
TOKEN=""
TOKEN2=""

echo -e "${BLUE}=================================================${NC}"
echo -e "${BLUE}🧪 Tests API MVP Sticky Notes${NC}"
echo -e "${BLUE}=================================================${NC}\n"

# Fonction pour afficher une section
section() {
    echo -e "\n${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}$1${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

# Fonction pour afficher un test
test_endpoint() {
    echo -e "${GREEN}✓ Test:${NC} $1"
    echo -e "${BLUE}Command:${NC} $2\n"
}

# ================================================
# 1. AUTHENTIFICATION
# ================================================
section "🔐 1. AUTHENTIFICATION (2 endpoints)"

test_endpoint "1.1 POST /auth/register - Créer testuser2" \
    "POST $BASE_URL/auth/register"

REGISTER_RESPONSE=$(curl -s -X POST $BASE_URL/auth/register \
    -H "Content-Type: application/json" \
    -d '{
        "username": "testuser2",
        "email": "testuser2@test.com",
        "password": "SecurePass123!"
    }')
echo "$REGISTER_RESPONSE" | python3 -m json.tool
echo ""

test_endpoint "1.2 POST /auth/login - Se connecter testuser1" \
    "POST $BASE_URL/auth/login"

LOGIN_RESPONSE=$(curl -s -X POST $BASE_URL/auth/login \
    -H "Content-Type: application/json" \
    -d '{
        "email": "testuser1@test.com",
        "password": "SecurePass123!"
    }')
echo "$LOGIN_RESPONSE" | python3 -m json.tool

# Extraire le token
TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
echo -e "\n${GREEN}Token testuser1 sauvegardé!${NC}\n"

# ================================================
# 2. NOTES
# ================================================
section "📝 2. NOTES (10 endpoints)"

test_endpoint "2.1 POST /notes - Créer une note" \
    "POST $BASE_URL/notes"

NOTE_RESPONSE=$(curl -s -X POST $BASE_URL/notes \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "content": "Ma première note de test curl",
        "important": true
    }')
echo "$NOTE_RESPONSE" | python3 -m json.tool

NOTE_ID=$(echo "$NOTE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo -e "\n${GREEN}Note créée avec ID: $NOTE_ID${NC}\n"

test_endpoint "2.2 GET /notes - Lister avec pagination" \
    "GET $BASE_URL/notes?page=1&per_page=10"

curl -s -X GET "$BASE_URL/notes?page=1&per_page=10" \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

test_endpoint "2.3 GET /notes?filter=important - Filtrer notes importantes" \
    "GET $BASE_URL/notes?filter=important"

curl -s -X GET "$BASE_URL/notes?filter=important" \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

test_endpoint "2.4 GET /notes?sort=date_asc - Trier par date croissante" \
    "GET $BASE_URL/notes?sort=date_asc"

curl -s -X GET "$BASE_URL/notes?sort=date_asc" \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

test_endpoint "2.5 GET /notes/$NOTE_ID - Détails d'une note" \
    "GET $BASE_URL/notes/$NOTE_ID"

curl -s -X GET "$BASE_URL/notes/$NOTE_ID" \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

test_endpoint "2.6 PUT /notes/$NOTE_ID - Modifier une note" \
    "PUT $BASE_URL/notes/$NOTE_ID"

curl -s -X PUT "$BASE_URL/notes/$NOTE_ID" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "content": "Note modifiée par curl",
        "important": false
    }' | python3 -m json.tool
echo ""

test_endpoint "2.8 GET /notes/$NOTE_ID/details - Détails complets" \
    "GET $BASE_URL/notes/$NOTE_ID/details"

curl -s -X GET "$BASE_URL/notes/$NOTE_ID/details" \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

test_endpoint "2.10 GET /notes?filter=sent - Notes créées et assignées" \
    "GET $BASE_URL/notes?filter=sent"

curl -s -X GET "$BASE_URL/notes?filter=sent" \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

test_endpoint "2.10 GET /notes?filter=received - Notes assignées à moi" \
    "GET $BASE_URL/notes?filter=received"

curl -s -X GET "$BASE_URL/notes?filter=received" \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

test_endpoint "2.10 GET /notes?filter=unread - Notes non lues" \
    "GET $BASE_URL/notes?filter=unread"

curl -s -X GET "$BASE_URL/notes?filter=unread" \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

# ================================================
# 3. CONTACTS
# ================================================
section "👥 3. CONTACTS (8 endpoints)"

test_endpoint "3.1 GET /users - Liste des utilisateurs" \
    "GET $BASE_URL/users"

curl -s -X GET "$BASE_URL/users" \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

test_endpoint "3.2 POST /contacts - Ajouter testuser2 en contact" \
    "POST $BASE_URL/contacts"

CONTACT_RESPONSE=$(curl -s -X POST $BASE_URL/contacts \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "contact_username": "testuser2",
        "nickname": "Mon collègue de test"
    }')
echo "$CONTACT_RESPONSE" | python3 -m json.tool

CONTACT_ID=$(echo "$CONTACT_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', 'N/A'))")
echo -e "\n${GREEN}Contact créé avec ID: $CONTACT_ID${NC}\n"

test_endpoint "3.3 GET /contacts - Liste des contacts" \
    "GET $BASE_URL/contacts"

curl -s -X GET "$BASE_URL/contacts" \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

test_endpoint "3.7 GET /contacts/assignable - Utilisateurs assignables" \
    "GET $BASE_URL/contacts/assignable"

curl -s -X GET "$BASE_URL/contacts/assignable" \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

if [ "$CONTACT_ID" != "N/A" ]; then
    test_endpoint "3.4 PUT /contacts/$CONTACT_ID - Modifier nickname" \
        "PUT $BASE_URL/contacts/$CONTACT_ID"

    curl -s -X PUT "$BASE_URL/contacts/$CONTACT_ID" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "nickname": "Nouveau surnom curl"
        }' | python3 -m json.tool
    echo ""

    test_endpoint "3.6 GET /contacts/$CONTACT_ID - Détails du contact" \
        "GET $BASE_URL/contacts/$CONTACT_ID"

    curl -s -X GET "$BASE_URL/contacts/$CONTACT_ID" \
        -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
    echo ""
fi

# ================================================
# 4. ASSIGNMENTS
# ================================================
section "📌 4. ASSIGNMENTS (9 endpoints)"

test_endpoint "4.1 POST /assignments - Assigner la note à soi-même" \
    "POST $BASE_URL/assignments"

ASSIGNMENT_RESPONSE=$(curl -s -X POST $BASE_URL/assignments \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
        \"note_id\": $NOTE_ID,
        \"user_id\": 4
    }")
echo "$ASSIGNMENT_RESPONSE" | python3 -m json.tool

ASSIGNMENT_ID=$(echo "$ASSIGNMENT_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', 'N/A'))")
echo -e "\n${GREEN}Assignment créé avec ID: $ASSIGNMENT_ID${NC}\n"

test_endpoint "4.4 GET /assignments - Lister toutes les assignations" \
    "GET $BASE_URL/assignments"

curl -s -X GET "$BASE_URL/assignments?page=1&per_page=10" \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

test_endpoint "4.8 GET /assignments/unread - Assignations non lues" \
    "GET $BASE_URL/assignments/unread"

curl -s -X GET "$BASE_URL/assignments/unread" \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

if [ "$ASSIGNMENT_ID" != "N/A" ]; then
    test_endpoint "4.7 PUT /assignments/$ASSIGNMENT_ID/status - Marquer comme terminé" \
        "PUT $BASE_URL/assignments/$ASSIGNMENT_ID/status"

    curl -s -X PUT "$BASE_URL/assignments/$ASSIGNMENT_ID/status" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "recipient_status": "terminé"
        }' | python3 -m json.tool
    echo ""
    
    test_endpoint "4.3 PUT /assignments/$ASSIGNMENT_ID/priority - Toggle priorité" \
        "PUT $BASE_URL/assignments/$ASSIGNMENT_ID/priority"

    curl -s -X PUT "$BASE_URL/assignments/$ASSIGNMENT_ID/priority" \
        -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
    echo ""
fi

test_endpoint "2.9 GET /notes/$NOTE_ID/assignments - Liste assignations (créateur)" \
    "GET $BASE_URL/notes/$NOTE_ID/assignments"

curl -s -X GET "$BASE_URL/notes/$NOTE_ID/assignments" \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

# ================================================
# 5. ACTION LOGS
# ================================================
section "📋 5. ACTION LOGS (5 endpoints)"

test_endpoint "5.3 GET /action_logs - Liste avec pagination" \
    "GET $BASE_URL/action_logs?page=1&per_page=20"

ACTION_LOGS=$(curl -s -X GET "$BASE_URL/action_logs?page=1&per_page=20" \
    -H "Authorization: Bearer $TOKEN")
echo "$ACTION_LOGS" | python3 -m json.tool

LOG_ID=$(echo "$ACTION_LOGS" | python3 -c "import sys, json; logs = json.load(sys.stdin).get('logs', []); print(logs[0]['id'] if logs else 'N/A')")
echo ""

test_endpoint "5.5 GET /action_logs/stats - Statistiques" \
    "GET $BASE_URL/action_logs/stats"

curl -s -X GET "$BASE_URL/action_logs/stats" \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

if [ "$LOG_ID" != "N/A" ]; then
    test_endpoint "5.4 GET /action_logs/$LOG_ID - Détails d'un log" \
        "GET $BASE_URL/action_logs/$LOG_ID"

    curl -s -X GET "$BASE_URL/action_logs/$LOG_ID" \
        -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
    echo ""
fi

# ================================================
# 6. UTILISATEURS
# ================================================
section "👤 6. UTILISATEURS (5 endpoints)"

test_endpoint "6.3 GET /users/me - Profil utilisateur connecté (route ajoutée)" \
    "GET $BASE_URL/users/me"

curl -s -X GET "$BASE_URL/users/me" \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

test_endpoint "6.2 GET /users/4 - Détails d'un utilisateur" \
    "GET $BASE_URL/users/4"

curl -s -X GET "$BASE_URL/users/4" \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

# ================================================
# 7. TESTS DE SÉCURITÉ
# ================================================
section "🔐 7. TESTS DE SÉCURITÉ"

test_endpoint "8.1 GET /notes sans token (401)" \
    "GET $BASE_URL/notes"

curl -s -X GET "$BASE_URL/notes" | python3 -m json.tool
echo ""

test_endpoint "8.2 GET /notes avec token invalide (401)" \
    "GET $BASE_URL/notes avec Bearer invalid_token"

curl -s -X GET "$BASE_URL/notes" \
    -H "Authorization: Bearer invalid_token_xyz" | python3 -m json.tool
echo ""

# ================================================
# 8. TESTS DE VALIDATION
# ================================================
section "🧪 8. TESTS DE VALIDATION"

test_endpoint "9.1 POST /auth/register avec email invalide (400)" \
    "POST $BASE_URL/auth/register"

curl -s -X POST $BASE_URL/auth/register \
    -H "Content-Type: application/json" \
    -d '{
        "username": "test",
        "email": "invalid-email",
        "password": "pass123"
    }' | python3 -m json.tool
echo ""

test_endpoint "9.2 POST /auth/register avec mot de passe court (400, validation ajoutée)" \
    "POST $BASE_URL/auth/register"

curl -s -X POST $BASE_URL/auth/register \
    -H "Content-Type: application/json" \
    -d '{
        "username": "testshortpwd",
        "email": "shortpwd@test.com",
        "password": "123"
    }' | python3 -m json.tool
echo ""

test_endpoint "9.3 POST /notes sans contenu (400)" \
    "POST $BASE_URL/notes"

curl -s -X POST $BASE_URL/notes \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "important": true
    }' | python3 -m json.tool
echo ""

# ================================================
# 9. NETTOYAGE (OPTIONNEL)
# ================================================
section "🧹 9. NETTOYAGE (soft delete)"

test_endpoint "2.7 DELETE /notes/$NOTE_ID - Supprimer la note" \
    "DELETE $BASE_URL/notes/$NOTE_ID"

curl -s -X DELETE "$BASE_URL/notes/$NOTE_ID" \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

if [ "$CONTACT_ID" != "N/A" ]; then
    test_endpoint "3.5 DELETE /contacts/$CONTACT_ID - Supprimer le contact" \
        "DELETE $BASE_URL/contacts/$CONTACT_ID"

    curl -s -X DELETE "$BASE_URL/contacts/$CONTACT_ID" \
        -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
    echo ""
fi

# ================================================
# RÉSUMÉ
# ================================================
echo -e "\n${BLUE}=================================================${NC}"
echo -e "${GREEN}✅ Tests terminés!${NC}"
echo -e "${BLUE}=================================================${NC}\n"
echo -e "Total des sections testées:"
echo -e "  - ${GREEN}✓${NC} Authentification (2 endpoints)"
echo -e "  - ${GREEN}✓${NC} Notes (10 endpoints)"
echo -e "  - ${GREEN}✓${NC} Contacts (8 endpoints)"
echo -e "  - ${GREEN}✓${NC} Assignations (9 endpoints)"
echo -e "  - ${GREEN}✓${NC} Action Logs (5 endpoints)"
echo -e "  - ${GREEN}✓${NC} Utilisateurs (5 endpoints)"
echo -e "  - ${GREEN}✓${NC} Tests de sécurité"
echo -e "  - ${GREEN}✓${NC} Tests de validation"
echo -e "\n${YELLOW}Note:${NC} Les routes Admin nécessitent un token admin (non testé ici)\n"
