#!/bin/bash

# Script de test des modifications recipient_status et finished_date

BASE_URL="http://localhost:5000/v1"
ECHO_SEPARATOR="echo '========================================'"

echo "🧪 TESTS DES MODIFICATIONS"
echo "========================================="

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher les résultats
test_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

# 1. Créer deux utilisateurs
echo ""
echo "📝 1. Création des utilisateurs Alice et Bob..."

ALICE_REGISTER=$(curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"alice_test","email":"alice@test.com","password":"password123"}')

BOB_REGISTER=$(curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"bob_test","email":"bob@test.com","password":"password123"}')

echo "Alice: $ALICE_REGISTER"
echo "Bob: $BOB_REGISTER"

# 2. Login Alice
echo ""
echo "🔐 2. Connexion d'Alice..."

ALICE_LOGIN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"alice_test","password":"password123"}')

ALICE_TOKEN=$(echo $ALICE_LOGIN | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -n "$ALICE_TOKEN" ]; then
    test_result 0 "Alice connectée"
else
    test_result 1 "Échec connexion Alice"
    exit 1
fi

# 3. Login Bob
echo ""
echo "🔐 3. Connexion de Bob..."

BOB_LOGIN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"bob_test","password":"password123"}')

BOB_TOKEN=$(echo $BOB_LOGIN | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -n "$BOB_TOKEN" ]; then
    test_result 0 "Bob connecté"
else
    test_result 1 "Échec connexion Bob"
    exit 1
fi

# 4. Alice crée une note (SANS status car supprimé)
echo ""
echo "📋 4. Alice crée une note (sans champ status)..."

NOTE_CREATE=$(curl -s -X POST "$BASE_URL/notes" \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content":"Préparer le rapport Q4","important":true}')

NOTE_ID=$(echo $NOTE_CREATE | grep -o '"id":[0-9]*' | cut -d':' -f2)

if [ -n "$NOTE_ID" ]; then
    test_result 0 "Note créée (ID: $NOTE_ID)"
    echo "Réponse: $NOTE_CREATE"
else
    test_result 1 "Échec création note"
    echo "Réponse: $NOTE_CREATE"
fi

# 5. Alice ajoute Bob en contact
echo ""
echo "👥 5. Alice ajoute Bob en contact..."

CONTACT_CREATE=$(curl -s -X POST "$BASE_URL/contacts" \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"contact_username":"bob_test","nickname":"Bob"}')

echo "Contact: $CONTACT_CREATE"

# 6. Bob ajoute Alice en contact (pour contact mutuel)
echo ""
echo "👥 6. Bob ajoute Alice en contact..."

CONTACT_CREATE_BOB=$(curl -s -X POST "$BASE_URL/contacts" \
  -H "Authorization: Bearer $BOB_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"contact_username":"alice_test","nickname":"Alice"}')

echo "Contact: $CONTACT_CREATE_BOB"

# 7. Alice assigne la note à Bob
echo ""
echo "📤 7. Alice assigne la note à Bob..."

BOB_ID=$(echo $BOB_REGISTER | grep -o '"id":[0-9]*' | cut -d':' -f2)

ASSIGNMENT_CREATE=$(curl -s -X POST "$BASE_URL/assignments" \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"note_id\":$NOTE_ID,\"user_id\":$BOB_ID}")

ASSIGNMENT_ID=$(echo $ASSIGNMENT_CREATE | grep -o '"id":[0-9]*' | cut -d':' -f2)

if [ -n "$ASSIGNMENT_ID" ]; then
    test_result 0 "Assignation créée (ID: $ASSIGNMENT_ID)"
    echo "Réponse: $ASSIGNMENT_CREATE"
    
    # Vérifier que recipient_status = 'en_cours' par défaut
    if echo "$ASSIGNMENT_CREATE" | grep -q '"recipient_status":"en_cours"'; then
        test_result 0 "recipient_status = 'en_cours' par défaut"
    else
        test_result 1 "recipient_status manquant ou incorrect"
    fi
    
    # Vérifier que finished_date = null
    if echo "$ASSIGNMENT_CREATE" | grep -q '"finished_date":null'; then
        test_result 0 "finished_date = null par défaut"
    else
        test_result 1 "finished_date manquant ou incorrect"
    fi
else
    test_result 1 "Échec assignation"
fi

# 8. Bob marque comme terminé
echo ""
echo "✅ 8. Bob marque l'assignation comme terminé..."

STATUS_UPDATE=$(curl -s -X PUT "$BASE_URL/assignments/$ASSIGNMENT_ID/status" \
  -H "Authorization: Bearer $BOB_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"recipient_status":"terminé"}')

echo "Réponse: $STATUS_UPDATE"

# Vérifier que finished_date est maintenant renseigné
if echo "$STATUS_UPDATE" | grep -q '"finished_date":"'; then
    test_result 0 "finished_date automatiquement renseigné"
else
    test_result 1 "finished_date non renseigné"
fi

if echo "$STATUS_UPDATE" | grep -q '"recipient_status":"terminé"'; then
    test_result 0 "recipient_status = 'terminé'"
else
    test_result 1 "recipient_status incorrect"
fi

# 9. Alice consulte la note et voit les détails
echo ""
echo "👁️  9. Alice consulte la note (créateur)..."

NOTE_DETAILS=$(curl -s -X GET "$BASE_URL/notes/$NOTE_ID" \
  -H "Authorization: Bearer $ALICE_TOKEN")

echo "Réponse: $NOTE_DETAILS"

# Vérifier la présence des nouveaux champs
if echo "$NOTE_DETAILS" | grep -q '"assignments_details"'; then
    test_result 0 "assignments_details présent (créateur)"
else
    test_result 1 "assignments_details manquant"
fi

if echo "$NOTE_DETAILS" | grep -q '"read_by"'; then
    test_result 0 "read_by présent (créateur)"
else
    test_result 1 "read_by manquant"
fi

if echo "$NOTE_DETAILS" | grep -q '"finished_date"'; then
    test_result 0 "finished_date présent dans assignments_details"
else
    test_result 1 "finished_date manquant dans assignments_details"
fi

# 10. Bob consulte la note (destinataire)
echo ""
echo "👁️  10. Bob consulte la note (destinataire)..."

NOTE_DETAILS_BOB=$(curl -s -X GET "$BASE_URL/notes/$NOTE_ID" \
  -H "Authorization: Bearer $BOB_TOKEN")

echo "Réponse: $NOTE_DETAILS_BOB"

# Vérifier la confidentialité
if echo "$NOTE_DETAILS_BOB" | grep -q '"my_assignment"'; then
    test_result 0 "my_assignment présent (destinataire)"
else
    test_result 1 "my_assignment manquant"
fi

if echo "$NOTE_DETAILS_BOB" | grep -q '"assigned_to":null'; then
    test_result 0 "assigned_to = null (confidentialité)"
else
    test_result 1 "assigned_to visible (violation confidentialité)"
fi

if echo "$NOTE_DETAILS_BOB" | grep -q '"read_by":null'; then
    test_result 0 "read_by = null (confidentialité)"
else
    test_result 1 "read_by visible (violation confidentialité)"
fi

# 11. Bob remet en cours
echo ""
echo "⏳ 11. Bob remet l'assignation en cours..."

STATUS_REVERT=$(curl -s -X PUT "$BASE_URL/assignments/$ASSIGNMENT_ID/status" \
  -H "Authorization: Bearer $BOB_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"recipient_status":"en_cours"}')

echo "Réponse: $STATUS_REVERT"

# Vérifier que finished_date est maintenant null
if echo "$STATUS_REVERT" | grep -q '"finished_date":null'; then
    test_result 0 "finished_date reset à null"
else
    test_result 1 "finished_date non reset"
fi

echo ""
echo "========================================="
echo "🎉 Tests terminés !"
echo "========================================="
