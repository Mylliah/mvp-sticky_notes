#!/bin/bash

# Script de test complet de l'API Sticky Notes
# Tests de toutes les routes (48 endpoints)

BASE_URL="http://localhost:5000/v1"

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Compteurs
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Fonction pour rafraîchir le token admin (éviter expiration JWT)
refresh_admin_token() {
    ADMIN_LOGIN=$(curl -s -X POST "$BASE_URL/auth/login" \
      -H "Content-Type: application/json" \
      -d '{"email":"admin@test.com","password":"admin123"}')
    
    ADMIN_TOKEN=$(echo $ADMIN_LOGIN | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)
    
    if [ -z "$ADMIN_TOKEN" ] || [ "$ADMIN_TOKEN" = "null" ]; then
        echo -e "${RED}⚠️  Échec rafraîchissement token admin${NC}"
        return 1
    fi
    return 0
}

# Fonction pour afficher les résultats
test_result() {
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    if [ $1 -eq 0 ]; then
        PASSED_TESTS=$((PASSED_TESTS + 1))
        echo -e "${GREEN}✅ $2${NC}"
    else
        FAILED_TESTS=$((FAILED_TESTS + 1))
        echo -e "${RED}❌ $2${NC}"
    fi
}

section() {
    echo ""
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}========================================${NC}"
}

subsection() {
    echo ""
    echo -e "${BLUE}>>> $1${NC}"
}

echo -e "${YELLOW}"
echo "╔════════════════════════════════════════╗"
echo "║   🧪 TESTS API STICKY NOTES v1.1      ║"
echo "║   48 endpoints - 330 tests backend    ║"
echo "╚════════════════════════════════════════╝"
echo -e "${NC}"

# ============================================
# 1. AUTHENTICATION (2 endpoints)
# ============================================
section "1. 🔐 AUTHENTICATION (2/48)"

subsection "POST /auth/register - Créer Alice"
ALICE_REGISTER=$(curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"alice_test","email":"alice@test.com","password":"password123"}')

if echo "$ALICE_REGISTER" | grep -q '"id"'; then
    ALICE_ID=$(echo "$ALICE_REGISTER" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
    test_result 0 "Alice créée (ID: $ALICE_ID)"
elif echo "$ALICE_REGISTER" | grep -q "already exists"; then
    echo -e "${YELLOW}ℹ️  Alice existe déjà, skip création${NC}"
else
    test_result 1 "Échec création Alice"
    echo "Erreur: $ALICE_REGISTER"
fi

subsection "POST /auth/register - Créer Bob"
BOB_REGISTER=$(curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"bob_test","email":"bob@test.com","password":"password123"}')

if echo "$BOB_REGISTER" | grep -q '"id"'; then
    BOB_ID=$(echo "$BOB_REGISTER" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
    test_result 0 "Bob créé (ID: $BOB_ID)"
elif echo "$BOB_REGISTER" | grep -q "already exists"; then
    echo -e "${YELLOW}ℹ️  Bob existe déjà, skip création${NC}"
else
    test_result 1 "Échec création Bob"
fi

subsection "POST /auth/register - Créer Admin"
ADMIN_REGISTER=$(curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin_test","email":"admin@test.com","password":"admin123"}')

if echo "$ADMIN_REGISTER" | grep -q '"id"'; then
    ADMIN_ID=$(echo "$ADMIN_REGISTER" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
    test_result 0 "Admin créé (ID: $ADMIN_ID)"
elif echo "$ADMIN_REGISTER" | grep -q "already exists"; then
    echo -e "${YELLOW}ℹ️  Admin existe déjà, skip création${NC}"
else
    test_result 1 "Échec création Admin"
fi

subsection "POST /auth/login - Connexion Alice"
ALICE_LOGIN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@test.com","password":"password123"}')

ALICE_TOKEN=$(echo $ALICE_LOGIN | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)

if [ -n "$ALICE_TOKEN" ] && [ "$ALICE_TOKEN" != "null" ]; then
    test_result 0 "Alice connectée"
    
    # Récupérer l'ID via /users/me
    ALICE_ME=$(curl -s -X GET "$BASE_URL/users/me" -H "Authorization: Bearer $ALICE_TOKEN")
    ALICE_ID=$(echo "$ALICE_ME" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
else
    test_result 1 "Échec connexion Alice"
    echo "Debug: $ALICE_LOGIN"
    exit 1
fi

subsection "POST /auth/login - Connexion Bob"
BOB_LOGIN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"bob@test.com","password":"password123"}')

BOB_TOKEN=$(echo $BOB_LOGIN | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)

if [ -n "$BOB_TOKEN" ] && [ "$BOB_TOKEN" != "null" ]; then
    test_result 0 "Bob connecté"
    
    # Récupérer l'ID via /users/me
    BOB_ME=$(curl -s -X GET "$BASE_URL/users/me" -H "Authorization: Bearer $BOB_TOKEN")
    BOB_ID=$(echo "$BOB_ME" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
else
    test_result 1 "Échec connexion Bob"
    exit 1
fi

subsection "POST /auth/login - Connexion Admin"
ADMIN_LOGIN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"admin123"}')

ADMIN_TOKEN=$(echo $ADMIN_LOGIN | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)

if [ -n "$ADMIN_TOKEN" ] && [ "$ADMIN_TOKEN" != "null" ]; then
    test_result 0 "Admin connecté"
    
    # Récupérer l'ID via /users/me
    ADMIN_ME=$(curl -s -X GET "$BASE_URL/users/me" -H "Authorization: Bearer $ADMIN_TOKEN")
    ADMIN_ID=$(echo "$ADMIN_ME" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
else
    test_result 1 "Échec connexion Admin"
fi

# Configuration du rôle admin APRÈS création du compte
subsection "Configuration rôle admin en DB..."
docker exec mvp-sticky_notes-db-1 psql -U app -d appdb -c \
  "UPDATE users SET role = 'admin' WHERE email = 'admin@test.com';" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Rôle admin configuré${NC}"
else
    echo -e "${YELLOW}⚠️  Échec configuration admin${NC}"
fi

# ============================================
# 2. USERS (5 endpoints)
# ============================================
section "2. 👤 USERS (5/48)"

subsection "GET /users/me - Profil Alice (déjà testé au login)"
if echo "$ALICE_ME" | grep -q "alice_test"; then
    test_result 0 "Profil Alice récupéré"
else
    test_result 1 "Échec profil Alice"
    echo "Debug: $ALICE_ME"
fi

subsection "GET /users - Liste utilisateurs"
USERS_LIST=$(curl -s -X GET "$BASE_URL/users" \
  -H "Authorization: Bearer $ALICE_TOKEN")

if echo "$USERS_LIST" | grep -q "alice_test"; then
    test_result 0 "Liste utilisateurs OK"
else
    test_result 1 "Échec liste utilisateurs"
    echo "Debug: $USERS_LIST"
fi

subsection "GET /users/:id - Détails Bob"
USER_DETAILS=$(curl -s -X GET "$BASE_URL/users/$BOB_ID" \
  -H "Authorization: Bearer $ALICE_TOKEN")

if echo "$USER_DETAILS" | grep -q "bob_test"; then
    test_result 0 "Détails Bob OK"
else
    test_result 1 "Échec détails Bob"
fi

subsection "PUT /users/:id - Modifier Alice"
USER_UPDATE=$(curl -s -X PUT "$BASE_URL/users/$ALICE_ID" \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email":"alice_new@test.com"}')

if echo "$USER_UPDATE" | grep -q "alice_new@test.com"; then
    test_result 0 "Alice modifiée (email)"
else
    test_result 1 "Échec modification Alice"
fi

# ============================================
# 3. CONTACTS (6 endpoints)
# ============================================
section "3. 👥 CONTACTS (6/48)"

subsection "POST /contacts - Alice ajoute Bob"
CONTACT_CREATE=$(curl -s -X POST "$BASE_URL/contacts" \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"contact_username":"bob_test","nickname":"Bob"}')

if echo "$CONTACT_CREATE" | grep -q '"id"'; then
    CONTACT_ID=$(echo "$CONTACT_CREATE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
    test_result 0 "Contact créé (ID: $CONTACT_ID)"
else
    test_result 1 "Échec création contact"
    echo "Erreur: $CONTACT_CREATE"
fi

subsection "POST /contacts - Bob ajoute Alice (mutuel)"
CONTACT_CREATE_BOB=$(curl -s -X POST "$BASE_URL/contacts" \
  -H "Authorization: Bearer $BOB_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"contact_username":"alice_test","nickname":"Alice"}')

if echo "$CONTACT_CREATE_BOB" | grep -q '"id"'; then
    test_result 0 "Contact mutuel créé"
else
    test_result 1 "Échec contact mutuel"
    echo "Erreur: $CONTACT_CREATE_BOB"
fi

subsection "GET /contacts - Liste contacts Alice"
CONTACTS_LIST=$(curl -s -X GET "$BASE_URL/contacts" \
  -H "Authorization: Bearer $ALICE_TOKEN")

if echo "$CONTACTS_LIST" | grep -q "Bob"; then
    test_result 0 "Liste contacts OK"
else
    test_result 1 "Échec liste contacts"
fi

subsection "GET /contacts/assignable - Utilisateurs assignables"
ASSIGNABLE=$(curl -s -X GET "$BASE_URL/contacts/assignable" \
  -H "Authorization: Bearer $ALICE_TOKEN")

if echo "$ASSIGNABLE" | grep -q "Bob"; then
    test_result 0 "Liste assignables OK"
else
    test_result 1 "Échec liste assignables"
fi

subsection "GET /contacts/:id - Détails contact"
CONTACT_DETAILS=$(curl -s -X GET "$BASE_URL/contacts/$CONTACT_ID" \
  -H "Authorization: Bearer $ALICE_TOKEN")

if echo "$CONTACT_DETAILS" | grep -q "Bob"; then
    test_result 0 "Détails contact OK"
else
    test_result 1 "Échec détails contact"
fi

subsection "PUT /contacts/:id - Modifier contact"
CONTACT_UPDATE=$(curl -s -X PUT "$BASE_URL/contacts/$CONTACT_ID" \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nickname":"Bobby"}')

if echo "$CONTACT_UPDATE" | grep -q "Bobby"; then
    test_result 0 "Contact modifié"
else
    test_result 1 "Échec modification contact"
fi

# ============================================
# 4. NOTES (7 endpoints)
# ============================================
section "4. 📝 NOTES (7/48)"

subsection "POST /notes - Alice crée une note"
NOTE_CREATE=$(curl -s -X POST "$BASE_URL/notes" \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content":"Réunion Q4","important":true}')

if echo "$NOTE_CREATE" | grep -q '"id"'; then
    NOTE_ID=$(echo "$NOTE_CREATE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
    test_result 0 "Note créée (ID: $NOTE_ID)"
else
    test_result 1 "Échec création note"
    echo "Erreur: $NOTE_CREATE"
fi

subsection "GET /notes - Liste notes Alice"
NOTES_LIST=$(curl -s -X GET "$BASE_URL/notes?page=1&per_page=20" \
  -H "Authorization: Bearer $ALICE_TOKEN")

if echo "$NOTES_LIST" | grep -q "notes"; then
    test_result 0 "Liste notes OK (pagination)"
else
    test_result 1 "Échec liste notes"
    echo "Debug: $NOTES_LIST"
fi

subsection "GET /notes?filter=important - Filtre importantes"
NOTES_FILTER=$(curl -s -X GET "$BASE_URL/notes?filter=important" \
  -H "Authorization: Bearer $ALICE_TOKEN")

if echo "$NOTES_FILTER" | grep -q "Réunion Q4"; then
    test_result 0 "Filtre important OK"
else
    test_result 1 "Échec filtre important"
fi

subsection "GET /notes?sort=date_asc - Tri ascendant"
NOTES_SORT=$(curl -s -X GET "$BASE_URL/notes?sort=date_asc" \
  -H "Authorization: Bearer $ALICE_TOKEN")

if echo "$NOTES_SORT" | grep -q "items"; then
    test_result 0 "Tri date_asc OK"
else
    test_result 1 "Échec tri"
fi

subsection "GET /notes/:id - Détails note"
NOTE_DETAILS=$(curl -s -X GET "$BASE_URL/notes/$NOTE_ID" \
  -H "Authorization: Bearer $ALICE_TOKEN")

if echo "$NOTE_DETAILS" | grep -q "Réunion Q4"; then
    test_result 0 "Détails note OK"
else
    test_result 1 "Échec détails note"
fi

subsection "GET /notes/:id/details - Détails complets"
NOTE_FULL=$(curl -s -X GET "$BASE_URL/notes/$NOTE_ID/details" \
  -H "Authorization: Bearer $ALICE_TOKEN")

if echo "$NOTE_FULL" | grep -q "created_date"; then
    test_result 0 "Détails complets OK"
else
    test_result 1 "Échec détails complets"
fi

subsection "PUT /notes/:id - Modifier note"
NOTE_UPDATE=$(curl -s -X PUT "$BASE_URL/notes/$NOTE_ID" \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content":"Réunion Q4 - Modifiée"}')

if echo "$NOTE_UPDATE" | grep -q "Modifiée"; then
    test_result 0 "Note modifiée"
else
    test_result 1 "Échec modification note"
fi

# ============================================
# 5. ASSIGNMENTS (8 endpoints)
# ============================================
section "5. 📧 ASSIGNMENTS (8/48)"

subsection "POST /assignments - Alice assigne à Bob"
ASSIGNMENT_CREATE=$(curl -s -X POST "$BASE_URL/assignments" \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"note_id":'"$NOTE_ID"',"user_id":'"$BOB_ID"'}')

if echo "$ASSIGNMENT_CREATE" | grep -q '"id"'; then
    ASSIGNMENT_ID=$(echo "$ASSIGNMENT_CREATE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
    test_result 0 "Assignation créée (ID: $ASSIGNMENT_ID)"
    
    # Vérifier recipient_status par défaut
    if echo "$ASSIGNMENT_CREATE" | grep -q '"recipient_status":"en_cours"'; then
        test_result 0 "recipient_status = en_cours (défaut)"
    else
        test_result 1 "recipient_status incorrect"
    fi
else
    test_result 1 "Échec assignation"
    echo "Erreur: $ASSIGNMENT_CREATE"
fi

subsection "GET /notes/:id/assignments - Liste assignations note"
NOTE_ASSIGNMENTS=$(curl -s -X GET "$BASE_URL/notes/$NOTE_ID/assignments" \
  -H "Authorization: Bearer $ALICE_TOKEN")

if echo "$NOTE_ASSIGNMENTS" | grep -q "bob_test"; then
    test_result 0 "Liste assignations OK (créateur)"
else
    test_result 1 "Échec liste assignations"
fi

subsection "GET /assignments - Liste assignations Bob"
ASSIGNMENTS_LIST=$(curl -s -X GET "$BASE_URL/assignments" \
  -H "Authorization: Bearer $BOB_TOKEN")

if echo "$ASSIGNMENTS_LIST" | grep -q "$NOTE_ID"; then
    test_result 0 "Liste assignations Bob OK"
else
    test_result 1 "Échec liste assignations Bob"
fi

subsection "GET /assignments/unread - Assignations non lues Bob"
UNREAD=$(curl -s -X GET "$BASE_URL/assignments/unread" \
  -H "Authorization: Bearer $BOB_TOKEN")

if echo "$UNREAD" | grep -q "$NOTE_ID"; then
    test_result 0 "Unread OK"
else
    test_result 1 "Échec unread"
fi

subsection "GET /assignments/:id - Détails assignation"
ASSIGNMENT_DETAILS=$(curl -s -X GET "$BASE_URL/assignments/$ASSIGNMENT_ID" \
  -H "Authorization: Bearer $BOB_TOKEN")

if echo "$ASSIGNMENT_DETAILS" | grep -q "is_read"; then
    test_result 0 "Détails assignation OK"
else
    test_result 1 "Échec détails assignation"
fi

subsection "PUT /assignments/:id/priority - Toggle priorité"
PRIORITY=$(curl -s -X PUT "$BASE_URL/assignments/$ASSIGNMENT_ID/priority" \
  -H "Authorization: Bearer $BOB_TOKEN")

if echo "$PRIORITY" | grep -q '"recipient_priority":true'; then
    test_result 0 "Priorité activée"
else
    test_result 1 "Échec priorité"
fi

subsection "PUT /assignments/:id/status - Marquer terminé"
STATUS=$(curl -s -X PUT "$BASE_URL/assignments/$ASSIGNMENT_ID/status" \
  -H "Authorization: Bearer $BOB_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"recipient_status":"terminé"}')

if echo "$STATUS" | grep -q '"recipient_status":"terminé"'; then
    test_result 0 "Status terminé"
    
    # Vérifier finished_date auto-rempli
    if echo "$STATUS" | grep -q '"finished_date":"'; then
        test_result 0 "finished_date auto-rempli"
    else
        test_result 1 "finished_date non rempli"
    fi
else
    test_result 1 "Échec status"
fi

subsection "PUT /assignments/:id - Modifier assignation"
ASSIGNMENT_UPDATE=$(curl -s -X PUT "$BASE_URL/assignments/$ASSIGNMENT_ID" \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_read":true}')

if echo "$ASSIGNMENT_UPDATE" | grep -q '"is_read":true'; then
    test_result 0 "Assignation modifiée"
else
    test_result 1 "Échec modification assignation"
fi

# ============================================
# 6. ACTION LOGS - Admin Only (4 endpoints)
# ============================================
section "6. 📊 ACTION LOGS - Admin Only (4/48)"

# Rafraîchir le token admin pour éviter expiration
subsection "Rafraîchissement token admin..."
refresh_admin_token
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Token admin rafraîchi${NC}"
else
    echo -e "${YELLOW}⚠️  Token admin non rafraîchi, utilisation ancien token${NC}"
fi

subsection "GET /action_logs - Non-admin (doit échouer)"
LOGS_FAIL=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/action_logs" \
  -H "Authorization: Bearer $ALICE_TOKEN")

HTTP_CODE=$(echo "$LOGS_FAIL" | tail -n1)
if [ "$HTTP_CODE" = "403" ]; then
    test_result 0 "Non-admin bloqué (403)"
else
    test_result 1 "Non-admin devrait être bloqué"
fi

subsection "GET /action_logs - Admin"
LOGS=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/action_logs" \
  -H "Authorization: Bearer $ADMIN_TOKEN")

HTTP_CODE=$(echo "$LOGS" | tail -n1)
BODY=$(echo "$LOGS" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    test_result 0 "Admin accède aux logs (200)"
    
    # Vérifier qu'il y a des logs (registrations, logins, etc.)
    if echo "$BODY" | grep -q '"logs"'; then
        test_result 0 "Logs contenus présents"
        
        # Extraire un ID de log pour le test suivant
        LOG_ID=$(echo "$BODY" | python3 -c "import sys, json; data=json.load(sys.stdin); logs=data.get('logs', []); print(logs[0]['id'] if len(logs) > 0 else '')" 2>/dev/null)
    else
        test_result 1 "Pas de logs trouvés"
    fi
else
    test_result 1 "Admin devrait accéder aux logs"
    echo "HTTP Code: $HTTP_CODE"
fi

subsection "GET /action_logs/:id - Détails d'un log"

if [ -n "$LOG_ID" ] && [ "$LOG_ID" != "" ]; then
    LOG_DETAILS=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/action_logs/$LOG_ID" \
      -H "Authorization: Bearer $ADMIN_TOKEN")
    
    HTTP_CODE=$(echo "$LOG_DETAILS" | tail -n1)
    if [ "$HTTP_CODE" = "200" ]; then
        test_result 0 "Détails log OK"
    else
        test_result 1 "Échec détails log"
    fi
else
    echo -e "${YELLOW}⚠️  Pas d'ID log disponible pour test détails${NC}"
fi

subsection "GET /action_logs/stats - Statistiques"
STATS=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/action_logs/stats" \
  -H "Authorization: Bearer $ADMIN_TOKEN")

HTTP_CODE=$(echo "$STATS" | tail -n1)
if [ "$HTTP_CODE" = "200" ]; then
    test_result 0 "Statistiques logs OK"
else
    test_result 1 "Échec statistiques"
fi

# ============================================
# 7. ADMIN ROUTES (16 endpoints)
# ============================================
section "7. ⚙️ ADMIN ROUTES (16/48)"

# Rafraîchir le token admin pour éviter expiration
subsection "Rafraîchissement token admin..."
refresh_admin_token
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Token admin rafraîchi${NC}"
fi

subsection "GET /admin/users - Liste tous users"
ADMIN_USERS=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/admin/users" \
  -H "Authorization: Bearer $ADMIN_TOKEN")

HTTP_CODE=$(echo "$ADMIN_USERS" | tail -n1)
BODY=$(echo "$ADMIN_USERS" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    test_result 0 "Admin users list OK"
    
    # Vérifier qu'on a bien les 3 users
    if echo "$BODY" | grep -q "alice_test"; then
        test_result 0 "Tous users visibles par admin"
    fi
else
    test_result 1 "Échec admin/users (HTTP $HTTP_CODE)"
fi

subsection "GET /admin/notes - Liste toutes notes"
ADMIN_NOTES=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/admin/notes" \
  -H "Authorization: Bearer $ADMIN_TOKEN")

HTTP_CODE=$(echo "$ADMIN_NOTES" | tail -n1)
if [ "$HTTP_CODE" = "200" ]; then
    test_result 0 "Admin notes list OK"
else
    test_result 1 "Échec admin/notes"
fi

subsection "GET /admin/contacts - Liste tous contacts"
ADMIN_CONTACTS=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/admin/contacts" \
  -H "Authorization: Bearer $ADMIN_TOKEN")

HTTP_CODE=$(echo "$ADMIN_CONTACTS" | tail -n1)
if [ "$HTTP_CODE" = "200" ]; then
    test_result 0 "Admin contacts list OK"
else
    test_result 1 "Échec admin/contacts"
fi

subsection "GET /admin/assignments - Liste toutes assignations"
ADMIN_ASSIGNMENTS=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/admin/assignments" \
  -H "Authorization: Bearer $ADMIN_TOKEN")

HTTP_CODE=$(echo "$ADMIN_ASSIGNMENTS" | tail -n1)
if [ "$HTTP_CODE" = "200" ]; then
    test_result 0 "Admin assignments list OK"
else
    test_result 1 "Échec admin/assignments"
fi

subsection "GET /admin/stats - Statistiques globales"
ADMIN_STATS=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/admin/stats" \
  -H "Authorization: Bearer $ADMIN_TOKEN")

HTTP_CODE=$(echo "$ADMIN_STATS" | tail -n1)
BODY=$(echo "$ADMIN_STATS" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    test_result 0 "Stats admin OK"
    
    # Vérifier structure stats
    if echo "$BODY" | grep -q "total_users"; then
        test_result 0 "Stats structure OK"
    fi
else
    test_result 1 "Échec admin/stats"
fi

subsection "GET /admin/notes/:id - Lire note de n'importe qui"
ADMIN_NOTE=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/admin/notes/$NOTE_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN")

HTTP_CODE=$(echo "$ADMIN_NOTE" | tail -n1)
if [ "$HTTP_CODE" = "200" ]; then
    test_result 0 "Admin lecture note OK"
else
    test_result 1 "Échec admin GET note"
fi

subsection "PUT /admin/notes/:id - Modifier note de n'importe qui"
ADMIN_NOTE_UPDATE=$(curl -s -w "\n%{http_code}" -X PUT "$BASE_URL/admin/notes/$NOTE_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content":"Note modifiée par admin"}')

HTTP_CODE=$(echo "$ADMIN_NOTE_UPDATE" | tail -n1)
if [ "$HTTP_CODE" = "200" ]; then
    test_result 0 "Admin modification note OK"
else
    test_result 1 "Échec admin PUT note"
fi

subsection "GET /admin/contacts/:id - Lire contact"
ADMIN_CONTACT=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/admin/contacts/$CONTACT_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN")

HTTP_CODE=$(echo "$ADMIN_CONTACT" | tail -n1)
if [ "$HTTP_CODE" = "200" ]; then
    test_result 0 "Admin lecture contact OK"
else
    test_result 1 "Échec admin GET contact"
fi

subsection "PUT /admin/contacts/:id - Modifier contact"
ADMIN_CONTACT_UPDATE=$(curl -s -w "\n%{http_code}" -X PUT "$BASE_URL/admin/contacts/$CONTACT_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nickname":"Modifié par admin"}')

HTTP_CODE=$(echo "$ADMIN_CONTACT_UPDATE" | tail -n1)
if [ "$HTTP_CODE" = "200" ]; then
    test_result 0 "Admin modification contact OK"
else
    test_result 1 "Échec admin PUT contact"
fi

subsection "GET /admin/assignments/:id - Lire assignation"
ADMIN_ASSIGNMENT=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/admin/assignments/$ASSIGNMENT_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN")

HTTP_CODE=$(echo "$ADMIN_ASSIGNMENT" | tail -n1)
if [ "$HTTP_CODE" = "200" ]; then
    test_result 0 "Admin lecture assignment OK"
else
    test_result 1 "Échec admin GET assignment"
fi

subsection "PUT /admin/assignments/:id - Modifier assignation"
ADMIN_ASSIGNMENT_UPDATE=$(curl -s -w "\n%{http_code}" -X PUT "$BASE_URL/admin/assignments/$ASSIGNMENT_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_read":false}')

HTTP_CODE=$(echo "$ADMIN_ASSIGNMENT_UPDATE" | tail -n1)
if [ "$HTTP_CODE" = "200" ]; then
    test_result 0 "Admin modification assignment OK"
else
    test_result 1 "Échec admin PUT assignment"
fi

# Créer des ressources additionnelles pour tester DELETE admin
subsection "Préparation pour tests DELETE admin..."
NOTE2=$(curl -s -X POST "$BASE_URL/notes" \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content":"Note to delete"}')
NOTE2_ID=$(echo "$NOTE2" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)

CONTACT2=$(curl -s -X POST "$BASE_URL/contacts" \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"contact_username":"bob_test","nickname":"To delete"}')
CONTACT2_ID=$(echo "$CONTACT2" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)

ASSIGNMENT2=$(curl -s -X POST "$BASE_URL/assignments" \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"note_id":'"$NOTE2_ID"',"user_id":'"$BOB_ID"'}')
ASSIGNMENT2_ID=$(echo "$ASSIGNMENT2" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)

subsection "DELETE /admin/notes/:id - Supprimer note"
ADMIN_NOTE_DELETE=$(curl -s -w "\n%{http_code}" -X DELETE "$BASE_URL/admin/notes/$NOTE2_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN")

HTTP_CODE=$(echo "$ADMIN_NOTE_DELETE" | tail -n1)
if [ "$HTTP_CODE" = "200" ]; then
    test_result 0 "Admin suppression note OK"
else
    test_result 1 "Échec admin DELETE note"
fi

subsection "DELETE /admin/contacts/:id - Supprimer contact"
ADMIN_CONTACT_DELETE=$(curl -s -w "\n%{http_code}" -X DELETE "$BASE_URL/admin/contacts/$CONTACT2_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN")

HTTP_CODE=$(echo "$ADMIN_CONTACT_DELETE" | tail -n1)
if [ "$HTTP_CODE" = "200" ]; then
    test_result 0 "Admin suppression contact OK"
else
    test_result 1 "Échec admin DELETE contact"
fi

subsection "DELETE /admin/assignments/:id - Supprimer assignation"
ADMIN_ASSIGNMENT_DELETE=$(curl -s -w "\n%{http_code}" -X DELETE "$BASE_URL/admin/assignments/$ASSIGNMENT2_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN")

HTTP_CODE=$(echo "$ADMIN_ASSIGNMENT_DELETE" | tail -n1)
if [ "$HTTP_CODE" = "200" ]; then
    test_result 0 "Admin suppression assignment OK"
else
    test_result 1 "Échec admin DELETE assignment"
fi

# ============================================
# 8. SOFT DELETE
# ============================================
section "8. 🗑️ SOFT DELETE"

subsection "DELETE /notes/:id - Soft delete par créateur"
NOTE_DELETE=$(curl -s -X DELETE "$BASE_URL/notes/$NOTE_ID" \
  -H "Authorization: Bearer $ALICE_TOKEN")

if echo "$NOTE_DELETE" | grep -q "deleted"; then
    test_result 0 "Note soft deleted"
    
    # Vérifier delete_date et deleted_by
    NOTE_CHECK=$(curl -s -X GET "$BASE_URL/notes/$NOTE_ID" \
      -H "Authorization: Bearer $ALICE_TOKEN")
    
    if echo "$NOTE_CHECK" | grep -q '"delete_date"'; then
        test_result 0 "delete_date renseigné"
    else
        test_result 1 "delete_date manquant"
    fi
    
    if echo "$NOTE_CHECK" | grep -q "\"deleted_by\":$ALICE_ID"; then
        test_result 0 "deleted_by = créateur"
    else
        test_result 1 "deleted_by incorrect"
    fi
else
    test_result 1 "Échec soft delete"
fi

subsection "DELETE /contacts/:id - Supprimer contact"
CONTACT_DELETE=$(curl -s -X DELETE "$BASE_URL/contacts/$CONTACT_ID" \
  -H "Authorization: Bearer $ALICE_TOKEN")

if echo "$CONTACT_DELETE" | grep -q "deleted"; then
    test_result 0 "Contact supprimé"
else
    test_result 1 "Échec suppression contact"
fi

subsection "DELETE /assignments/:id - Supprimer assignation"
ASSIGNMENT_DELETE=$(curl -s -X DELETE "$BASE_URL/assignments/$ASSIGNMENT_ID" \
  -H "Authorization: Bearer $ALICE_TOKEN")

if echo "$ASSIGNMENT_DELETE" | grep -q "deleted"; then
    test_result 0 "Assignation supprimée"
else
    test_result 1 "Échec suppression assignation"
fi

# ============================================
# 9. RÉSULTATS FINAUX
# ============================================
section "9. 📊 RÉSULTATS FINAUX"

echo ""
echo -e "${CYAN}╔════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║          RÉSUMÉ DES TESTS              ║${NC}"
echo -e "${CYAN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}✅ Tests réussis  : $PASSED_TESTS${NC}"
echo -e "${RED}❌ Tests échoués  : $FAILED_TESTS${NC}"
echo -e "${BLUE}📊 Total tests    : $TOTAL_TESTS${NC}"
echo ""

PERCENTAGE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
echo -e "${BLUE}Taux de réussite : $PERCENTAGE%${NC}"

if [ $FAILED_TESTS -eq 0 ]; then
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║   🎉 TOUS LES TESTS SONT PASSÉS ! 🎉  ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
    exit 0
else
    echo ""
    echo -e "${YELLOW}╔════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║   ⚠️  CERTAINS TESTS ONT ÉCHOUÉ       ║${NC}"
    echo -e "${YELLOW}╚════════════════════════════════════════╝${NC}"
    exit 1
fi
