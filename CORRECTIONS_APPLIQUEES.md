# 🔧 Corrections appliquées suite aux tests curl

Date : 20 octobre 2025

## 📋 Résumé des corrections

Suite aux tests automatiques avec `test_api_curl.sh`, 3 problèmes ont été identifiés et corrigés :

---

## ✅ 1. Route GET /users/me manquante

### Problème
La route `/users/me` n'existait pas, causant une erreur 404 lors de l'appel.

### Solution
Ajout de la route dans `backend/app/routes/v1/users.py` :

```python
@bp.get('/users/me')
@jwt_required()
def get_current_user():
    """Récupérer le profil de l'utilisateur connecté."""
    current_user_id = int(get_jwt_identity())
    user = User.query.get_or_404(current_user_id)
    return user.to_dict()
```

### Usage
```bash
# Avant (fallback)
GET /users/4  # Nécessite de connaître son ID

# Après (recommandé)
GET /users/me  # Retourne automatiquement le profil de l'utilisateur connecté
```

### Avantages
- ✅ Plus simple pour le frontend (pas besoin de stocker l'ID utilisateur)
- ✅ Standard REST pour les routes "profil actuel"
- ✅ Meilleure sécurité (impossible d'accéder au profil d'un autre par erreur)

---

## ✅ 2. Validation du mot de passe trop faible

### Problème
Le endpoint `/auth/register` acceptait des mots de passe de 3 caractères, ce qui est une faille de sécurité.

```bash
# Avant : Accepté ❌
POST /auth/register
{"username":"test","email":"test@test.com","password":"123"}
→ 201 Created (MAUVAIS)
```

### Solution
Ajout de validation dans `backend/app/routes/v1/auth.py` :

```python
# Valider la longueur du mot de passe
if len(password) < 8:
    abort(400, description="Password must be at least 8 characters long")
```

### Résultat
```bash
# Après : Rejeté ✅
POST /auth/register
{"username":"test","email":"test@test.com","password":"123"}
→ 400 Bad Request: "Password must be at least 8 characters long"
```

### Impact
- ✅ Sécurité renforcée (minimum 8 caractères)
- ✅ Conforme aux bonnes pratiques de sécurité
- ✅ Message d'erreur clair pour l'utilisateur

---

## ✅ 3. Endpoint PUT /assignments/:id/status incorrect

### Problème
Le script de test envoyait `"status": "read"` au lieu du bon champ `"recipient_status"`.

```bash
# Avant : Erreur ❌
PUT /assignments/1/status
{"status": "read"}
→ 400 Bad Request: "Missing recipient_status"
```

### Solution
Correction du script `test_api_curl.sh` et `CURL_COMMANDS.md` :

```bash
# Après : Correct ✅
PUT /assignments/1/status
{"recipient_status": "terminé"}
→ 200 OK + finished_date rempli automatiquement
```

### Clarification du modèle Assignment

Le modèle `Assignment` a **3 types de statuts** différents :

| Champ | Type | Valeurs | Usage | Endpoint |
|-------|------|---------|-------|----------|
| `is_read` | boolean | `true`/`false` | Marquer comme lu | Auto GET /notes/:id |
| `recipient_priority` | boolean | `true`/`false` | Important pour MOI | PUT /assignments/:id/priority |
| `recipient_status` | string | `'en_cours'`/`'terminé'` | État d'avancement | PUT /assignments/:id/status |

### Exemples d'usage

#### Marquer comme lu (automatique)
```bash
# Se fait automatiquement lors de l'ouverture
GET /notes/1
→ is_read=true, read_date rempli
```

#### Toggle priorité personnelle
```bash
PUT /assignments/1/priority
# Pas de body, bascule automatiquement
→ recipient_priority passe de false à true (ou inverse)
```

#### Changer le statut d'avancement
```bash
# Marquer comme terminé
PUT /assignments/1/status
{"recipient_status": "terminé"}
→ recipient_status='terminé', finished_date rempli

# Remettre en cours
PUT /assignments/1/status
{"recipient_status": "en_cours"}
→ recipient_status='en_cours', finished_date=null
```

---

## 🧪 Tests de validation

### Test 1 : GET /users/me
```bash
curl -X GET http://localhost:5000/v1/users/me \
  -H "Authorization: Bearer $TOKEN"
  
# Résultat attendu
{
  "id": 4,
  "username": "testuser1",
  "email": "testuser1@test.com",
  "role": "user",
  "created_date": "..."
}
```
✅ **Validé** : Route fonctionne correctement

---

### Test 2 : Validation mot de passe
```bash
curl -X POST http://localhost:5000/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@test.com","password":"123"}'
  
# Résultat attendu
{
  "error": "Bad Request",
  "message": "Password must be at least 8 characters long"
}
```
✅ **Validé** : Mot de passe court rejeté

---

### Test 3 : PUT /assignments/status
```bash
curl -X PUT http://localhost:5000/v1/assignments/5/status \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"recipient_status":"terminé"}'
  
# Résultat attendu
{
  "id": 5,
  "recipient_status": "terminé",
  "finished_date": "2025-10-19T22:23:56.049674",
  ...
}
```
✅ **Validé** : Status mis à jour correctement avec finished_date

---

## 📊 Impact sur les tests

### Avant corrections
- ❌ GET /users/me → 404 Not Found
- ❌ POST /auth/register (password="123") → 201 Created (faille sécurité)
- ❌ PUT /assignments/:id/status → 400 Missing recipient_status

### Après corrections
- ✅ GET /users/me → 200 OK (profil utilisateur)
- ✅ POST /auth/register (password="123") → 400 Bad Request (validation)
- ✅ PUT /assignments/:id/status → 200 OK (status mis à jour)

### Résultat global
**100% des tests passent** ✅

---

## 📦 Fichiers modifiés

1. `backend/app/routes/v1/users.py`
   - ➕ Ajout route `GET /users/me`

2. `backend/app/routes/v1/auth.py`
   - 🔒 Ajout validation longueur mot de passe (min 8 caractères)

3. `test_api_curl.sh`
   - 🔧 Correction du test status : `"status": "read"` → `"recipient_status": "terminé"`
   - 🔧 Ajout test toggle priorité
   - 📝 Mise à jour messages tests

4. `CURL_COMMANDS.md`
   - 📝 Documentation corrigée pour `PUT /assignments/:id/status`
   - ➕ Ajout section toggle priorité

---

## 🎯 Prochaines étapes

Les corrections appliquées permettent maintenant de :

1. ✅ Tester tous les endpoints avec le script `./test_api_curl.sh`
2. ✅ Avoir une base backend solide pour le développement frontend
3. ✅ Respecter les bonnes pratiques de sécurité (validation password)
4. ✅ Offrir une API REST standard (route /me)

### Recommandations

- 🔒 **Sécurité** : Considérer l'ajout de critères supplémentaires pour le mot de passe (majuscule, chiffre, caractère spécial)
- 🧪 **Tests** : Ajouter des tests unitaires pytest pour ces nouvelles validations
- 📚 **Documentation** : Mettre à jour le `POSTMAN_TEST_PLAN.md` avec les corrections

---

**Auteur** : GitHub Copilot  
**Date** : 20 octobre 2025  
**Status** : ✅ Toutes les corrections validées et testées
