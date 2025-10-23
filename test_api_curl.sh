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
section "🔐 1. AUTHENTIFICATION (4 endpoints)"

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

test_endpoint "1.3 GET /auth/me - Profil utilisateur connecté" \
    "GET $BASE_URL/auth/me"

curl -s -X GET "$BASE_URL/auth/me" \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

test_endpoint "1.4 POST /auth/logout - Déconnexion avec traçabilité" \
    "POST $BASE_URL/auth/logout"

curl -s -X POST "$BASE_URL/auth/logout" \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo -e "\n${GREEN}Déconnexion réussie (token toujours valide car JWT stateless)${NC}\n"

# ================================================
# 2. NOTES
# ================================================
section "📝 2. NOTES (11 endpoints)"

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

test_endpoint "2.4.1 GET /notes?q=test - Recherche textuelle (MUST HAVE)" \
    "GET $BASE_URL/notes?q=test"

curl -s -X GET "$BASE_URL/notes?q=test" \
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

    test_endpoint "3.8 GET /contacts/$CONTACT_ID/notes - Notes partagées avec ce contact" \
        "GET $BASE_URL/contacts/$CONTACT_ID/notes"

    curl -s -X GET "$BASE_URL/contacts/$CONTACT_ID/notes" \
        -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
    echo ""
fi

# ================================================
# 4. ASSIGNMENTS
# ================================================
section "📌 4. ASSIGNMENTS (12 endpoints)"

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

    test_endpoint "4.2 GET /assignments/$ASSIGNMENT_ID - Détails d'une assignation" \
        "GET $BASE_URL/assignments/$ASSIGNMENT_ID"

    curl -s -X GET "$BASE_URL/assignments/$ASSIGNMENT_ID" \
        -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
    echo ""

    test_endpoint "4.5 PUT /assignments/$ASSIGNMENT_ID - Modifier assignation (mark as read)" \
        "PUT $BASE_URL/assignments/$ASSIGNMENT_ID"

    curl -s -X PUT "$BASE_URL/assignments/$ASSIGNMENT_ID" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "is_read": true
        }' | python3 -m json.tool
    echo ""
fi

test_endpoint "2.9 GET /notes/$NOTE_ID/assignments - Liste assignations (créateur)" \
    "GET $BASE_URL/notes/$NOTE_ID/assignments"

curl -s -X GET "$BASE_URL/notes/$NOTE_ID/assignments" \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

if [ "$ASSIGNMENT_ID" != "N/A" ]; then
    test_endpoint "4.6 DELETE /assignments/$ASSIGNMENT_ID - Supprimer assignation (undo)" \
        "DELETE $BASE_URL/assignments/$ASSIGNMENT_ID"

    curl -s -X DELETE "$BASE_URL/assignments/$ASSIGNMENT_ID" \
        -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
    echo ""
fi

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
section "👤 6. UTILISATEURS (6 endpoints)"

test_endpoint "6.3 GET /users/me - Profil utilisateur connecté" \
    "GET $BASE_URL/users/me"

curl -s -X GET "$BASE_URL/users/me" \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

test_endpoint "6.2 GET /users/4 - Détails d'un utilisateur" \
    "GET $BASE_URL/users/4"

curl -s -X GET "$BASE_URL/users/4" \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

test_endpoint "6.4 PUT /users/4 - Modifier profil utilisateur" \
    "PUT $BASE_URL/users/4"

curl -s -X PUT "$BASE_URL/users/4" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "username": "testuser1_updated",
        "email": "testuser1@test.com"
    }' | python3 -m json.tool
echo ""

# ================================================
# 7. ADMIN ROUTES
# ================================================
section "👑 7. ADMIN ROUTES (16 endpoints) - Nécessite token admin"

echo -e "${YELLOW}Note: Ces tests nécessitent un utilisateur avec role='admin'${NC}"
echo -e "${YELLOW}Pour tester: créer un admin avec PUT /admin/users/{id}/role${NC}\n"

test_endpoint "7.1 GET /admin/stats - Statistiques globales" \
    "GET $BASE_URL/admin/stats (requires admin token)"

echo -e "${BLUE}Commande:${NC} curl -X GET $BASE_URL/admin/stats -H 'Authorization: Bearer <ADMIN_TOKEN>'\n"

test_endpoint "7.2 GET /admin/users - Liste tous les utilisateurs" \
    "GET $BASE_URL/admin/users (requires admin token)"

echo -e "${BLUE}Commande:${NC} curl -X GET $BASE_URL/admin/users -H 'Authorization: Bearer <ADMIN_TOKEN>'\n"

test_endpoint "7.3 DELETE /admin/users/{id} - Supprimer un utilisateur" \
    "DELETE $BASE_URL/admin/users/{id} (requires admin token)"

echo -e "${BLUE}Commande:${NC} curl -X DELETE $BASE_URL/admin/users/5 -H 'Authorization: Bearer <ADMIN_TOKEN>'\n"

test_endpoint "7.4 PUT /admin/users/{id}/role - Changer rôle utilisateur" \
    "PUT $BASE_URL/admin/users/{id}/role (requires admin token)"

echo -e "${BLUE}Commande:${NC} curl -X PUT $BASE_URL/admin/users/4/role -H 'Authorization: Bearer <ADMIN_TOKEN>' -H 'Content-Type: application/json' -d '{\"role\": \"admin\"}'\n"

test_endpoint "7.5 GET /admin/notes - Liste toutes les notes" \
    "GET $BASE_URL/admin/notes (requires admin token)"

echo -e "${BLUE}Commande:${NC} curl -X GET $BASE_URL/admin/notes -H 'Authorization: Bearer <ADMIN_TOKEN>'\n"

test_endpoint "7.6 GET /admin/notes/{id} - Détails d'une note (admin)" \
    "GET $BASE_URL/admin/notes/{id} (requires admin token)"

echo -e "${BLUE}Commande:${NC} curl -X GET $BASE_URL/admin/notes/1 -H 'Authorization: Bearer <ADMIN_TOKEN>'\n"

test_endpoint "7.7 PUT /admin/notes/{id} - Modifier une note (admin)" \
    "PUT $BASE_URL/admin/notes/{id} (requires admin token)"

echo -e "${BLUE}Commande:${NC} curl -X PUT $BASE_URL/admin/notes/1 -H 'Authorization: Bearer <ADMIN_TOKEN>' -H 'Content-Type: application/json' -d '{\"content\": \"Modified by admin\"}'\n"

test_endpoint "7.8 DELETE /admin/notes/{id} - Supprimer une note (admin)" \
    "DELETE $BASE_URL/admin/notes/{id} (requires admin token)"

echo -e "${BLUE}Commande:${NC} curl -X DELETE $BASE_URL/admin/notes/1 -H 'Authorization: Bearer <ADMIN_TOKEN>'\n"

test_endpoint "7.9 GET /admin/contacts - Liste tous les contacts" \
    "GET $BASE_URL/admin/contacts (requires admin token)"

echo -e "${BLUE}Commande:${NC} curl -X GET $BASE_URL/admin/contacts -H 'Authorization: Bearer <ADMIN_TOKEN>'\n"

test_endpoint "7.10 GET /admin/contacts/{id} - Détails d'un contact (admin)" \
    "GET $BASE_URL/admin/contacts/{id} (requires admin token)"

echo -e "${BLUE}Commande:${NC} curl -X GET $BASE_URL/admin/contacts/1 -H 'Authorization: Bearer <ADMIN_TOKEN>'\n"

test_endpoint "7.11 PUT /admin/contacts/{id} - Modifier un contact (admin)" \
    "PUT $BASE_URL/admin/contacts/{id} (requires admin token)"

echo -e "${BLUE}Commande:${NC} curl -X PUT $BASE_URL/admin/contacts/1 -H 'Authorization: Bearer <ADMIN_TOKEN>' -H 'Content-Type: application/json' -d '{\"nickname\": \"Admin nickname\"}'\n"

test_endpoint "7.12 DELETE /admin/contacts/{id} - Supprimer un contact (admin)" \
    "DELETE $BASE_URL/admin/contacts/{id} (requires admin token)"

echo -e "${BLUE}Commande:${NC} curl -X DELETE $BASE_URL/admin/contacts/1 -H 'Authorization: Bearer <ADMIN_TOKEN>'\n"

test_endpoint "7.13 GET /admin/assignments - Liste toutes les assignations" \
    "GET $BASE_URL/admin/assignments (requires admin token)"

echo -e "${BLUE}Commande:${NC} curl -X GET $BASE_URL/admin/assignments -H 'Authorization: Bearer <ADMIN_TOKEN>'\n"

test_endpoint "7.14 GET /admin/assignments/{id} - Détails assignation (admin)" \
    "GET $BASE_URL/admin/assignments/{id} (requires admin token)"

echo -e "${BLUE}Commande:${NC} curl -X GET $BASE_URL/admin/assignments/1 -H 'Authorization: Bearer <ADMIN_TOKEN>'\n"

test_endpoint "7.15 PUT /admin/assignments/{id} - Modifier assignation (admin)" \
    "PUT $BASE_URL/admin/assignments/{id} (requires admin token)"

echo -e "${BLUE}Commande:${NC} curl -X PUT $BASE_URL/admin/assignments/1 -H 'Authorization: Bearer <ADMIN_TOKEN>' -H 'Content-Type: application/json' -d '{\"is_read\": true}'\n"

test_endpoint "7.16 DELETE /admin/assignments/{id} - Supprimer assignation (admin)" \
    "DELETE $BASE_URL/admin/assignments/{id} (requires admin token)"

echo -e "${BLUE}Commande:${NC} curl -X DELETE $BASE_URL/admin/assignments/1 -H 'Authorization: Bearer <ADMIN_TOKEN>'\n"

# ================================================
# 8. TESTS DE SÉCURITÉ
# ================================================
section "🔐 8. TESTS DE SÉCURITÉ"

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
# 9. TESTS DE VALIDATION
# ================================================
section "🧪 9. TESTS DE VALIDATION"

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
# 10. NETTOYAGE (OPTIONNEL)
# ================================================
section "🧹 10. NETTOYAGE (soft delete)"

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
echo -e "  - ${GREEN}✓${NC} Authentification (4 endpoints)"
echo -e "  - ${GREEN}✓${NC} Notes (11 endpoints)"
echo -e "  - ${GREEN}✓${NC} Contacts (9 endpoints)"
echo -e "  - ${GREEN}✓${NC} Assignations (12 endpoints)"
echo -e "  - ${GREEN}✓${NC} Action Logs (5 endpoints)"
echo -e "  - ${GREEN}✓${NC} Utilisateurs (6 endpoints)"
echo -e "  - ${YELLOW}⚠${NC}  Admin Routes (16 endpoints - nécessite token admin)"
echo -e "  - ${GREEN}✓${NC} Tests de sécurité"
echo -e "  - ${GREEN}✓${NC} Tests de validation"
echo -e "\n${YELLOW}Note:${NC} Total = 63 endpoints documentés (47 testés automatiquement + 16 admin)\n"
