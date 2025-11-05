# 🐛 BUGS & VULNÉRABILITÉS - MVP STICKY NOTES

**Date** : 17 Octobre 2025  
**Version** : v1.1.0  
**Total** : 13 bugs identifiés

---

## 📊 VUE D'ENSEMBLE

```
🔴 CRITIQUE : 3 bugs  (7h)   - BLOQUANT PRODUCTION
🟠 ÉLEVÉ    : 3 bugs  (5.5h) - FORTEMENT RECOMMANDÉ
🟡 MOYEN    : 4 bugs  (7h)   - RECOMMANDÉ
🟢 BAS      : 3 bugs  (17h)  - NICE TO HAVE
─────────────────────────────────────────────────
TOTAL       : 13 bugs (36.5h)
```

---

## 🔴 BUGS CRITIQUES (7h)

### BUG-001 : Isolation incomplète sur Notes
**Priorité** : 🔴 CRITIQUE  
**Impact** : Fuite de données confidentielles  
**Effort** : 2h

**Description** :  
Les routes GET/PUT/DELETE `/v1/notes/<id>` ne vérifient pas si l'utilisateur est le créateur ou un destinataire. N'importe quel utilisateur authentifié peut lire, modifier ou supprimer n'importe quelle note.

**Preuve de concept** :
```bash
# User1 crée une note
curl -X POST http://localhost:5000/v1/notes \
  -H "Authorization: Bearer $TOKEN_USER1" \
  -H "Content-Type: application/json" \
  -d '{"content": "Note confidentielle de User1"}'
# → {"id": 123, ...}

# User2 peut lire cette note (BUG)
curl http://localhost:5000/v1/notes/123 \
  -H "Authorization: Bearer $TOKEN_USER2"
# → {"id": 123, "content": "Note confidentielle de User1", ...}
```

**Routes affectées** :
- ❌ GET `/v1/notes/<id>`
- ❌ PUT `/v1/notes/<id>`
- ❌ DELETE `/v1/notes/<id>`

**Solution** :
```python
@bp.get('/notes/<int:note_id>')
@jwt_required()
def get_note(note_id):
    current_user_id = int(get_jwt_identity())
    note = Note.query.get_or_404(note_id)
    
    # Vérifier créateur OU assignation
    is_creator = note.creator_id == current_user_id
    is_assigned = Assignment.query.filter_by(
        note_id=note_id, user_id=current_user_id
    ).first() is not None
    
    if not is_creator and not is_assigned:
        abort(403, description="Access denied")
    
    return note.to_dict()
```

**Tests requis** :
- `test_user_cannot_read_others_note`
- `test_user_cannot_update_others_note`
- `test_user_cannot_delete_others_note`
- `test_assigned_user_can_read_note`

**Référence** : PLAN_ACTION.md § 1.1

---

### BUG-002 : Isolation incomplète sur Contacts
**Priorité** : 🔴 CRITIQUE  
**Impact** : Accès aux contacts d'autres utilisateurs  
**Effort** : 1h

**Description** :  
Les routes GET/PUT/DELETE `/v1/contacts/<id>` ne vérifient pas la propriété. Un utilisateur peut accéder aux contacts d'un autre.

**Preuve de concept** :
```bash
# User1 ajoute User2 en contact
curl -X POST http://localhost:5000/v1/contacts \
  -H "Authorization: Bearer $TOKEN_USER1" \
  -d '{"contact_username": "user2", "nickname": "Bob"}'
# → {"id": 456, "user_id": 1, "contact_user_id": 2, ...}

# User3 peut accéder à ce contact (BUG)
curl http://localhost:5000/v1/contacts/456 \
  -H "Authorization: Bearer $TOKEN_USER3"
# → {"id": 456, ...}
```

**Routes affectées** :
- ❌ GET `/v1/contacts/<id>`
- ❌ PUT `/v1/contacts/<id>`
- ❌ DELETE `/v1/contacts/<id>`

**Solution** :
```python
@bp.get('/contacts/<int:contact_id>')
@jwt_required()
def get_contact(contact_id):
    current_user_id = int(get_jwt_identity())
    contact = Contact.query.get_or_404(contact_id)
    
    if contact.user_id != current_user_id:
        abort(403, description="Access denied")
    
    return contact.to_dict()
```

**Référence** : PLAN_ACTION.md § 1.2

---

### BUG-003 : GET /assignments liste TOUTES les assignations
**Priorité** : 🔴 CRITIQUE  
**Impact** : Fuite de données d'assignation  
**Effort** : 2h

**Description** :  
La route GET `/v1/assignments` retourne TOUTES les assignations de tous les utilisateurs au lieu de filtrer par l'utilisateur connecté.

**Preuve de concept** :
```bash
# User1 assigne une note à User2
curl -X POST http://localhost:5000/v1/assignments \
  -H "Authorization: Bearer $TOKEN_USER1" \
  -d '{"note_id": 123, "user_id": 2}'

# User3 voit cette assignation (BUG)
curl http://localhost:5000/v1/assignments \
  -H "Authorization: Bearer $TOKEN_USER3"
# → [{"note_id": 123, "user_id": 2, ...}, ...]
```

**Routes affectées** :
- ❌ GET `/v1/assignments` - Liste globale
- ❌ GET `/v1/assignments/<id>` - Pas de vérification
- ❌ PUT `/v1/assignments/<id>` - Pas de vérification
- ❌ DELETE `/v1/assignments/<id>` - Pas de vérification

**Solution** :
```python
@bp.get('/assignments')
@jwt_required()
def list_assignments():
    current_user_id = int(get_jwt_identity())
    
    # Filtrer : assigné à moi OU créateur de la note
    assignments = Assignment.query.join(
        Note, Assignment.note_id == Note.id
    ).filter(
        or_(
            Assignment.user_id == current_user_id,
            Note.creator_id == current_user_id
        )
    ).order_by(Assignment.id.asc()).all()
    
    return [a.to_dict() for a in assignments]
```

**Référence** : PLAN_ACTION.md § 1.3

---

### BUG-004 : Action logs accessibles à tous
**Priorité** : 🔴 CRITIQUE  
**Impact** : Fuite de traçabilité et vie privée  
**Effort** : 2h

**Description** :  
Les routes action_logs ne filtrent pas par utilisateur. Tous les users authentifiés peuvent voir les logs de tous les autres utilisateurs.

**Preuve de concept** :
```bash
# User1 fait des actions
# ...

# User2 peut voir les logs de User1 (BUG)
curl http://localhost:5000/v1/action_logs \
  -H "Authorization: Bearer $TOKEN_USER2"
# → [{"user_id": 1, "action_type": "create_note", ...}, ...]
```

**Routes affectées** :
- ❌ GET `/v1/action_logs` - Liste globale
- ❌ GET `/v1/action_logs/<id>` - Pas de vérification

**Solution** :
```python
@bp.get('/action_logs')
@jwt_required()
def list_action_logs():
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    
    query = ActionLog.query
    
    # Admin : peut filtrer par user_id
    # User : voit uniquement SES logs
    if current_user.is_admin():
        user_id = request.args.get('user_id', type=int)
        if user_id:
            query = query.filter_by(user_id=user_id)
    else:
        query = query.filter_by(user_id=current_user_id)
    
    # ... pagination ...
```

**Référence** : PLAN_ACTION.md § 1.4

---

## 🟠 BUGS ÉLEVÉS (5.5h)

### BUG-005 : Pas de rate limiting
**Priorité** : 🟠 ÉLEVÉE  
**Impact** : Brute force sur login, spam de requêtes  
**Effort** : 2h

**Description** :  
Aucune limite sur le nombre de tentatives de connexion. Un attaquant peut essayer des milliers de mots de passe par minute.

**Attaque possible** :
```bash
# Brute force login
for password in $(cat passwords.txt); do
  curl -X POST http://localhost:5000/v1/auth/login \
    -d "{\"username\": \"admin\", \"password\": \"$password\"}"
done
# → Aucune limitation
```

**Solution** :
```python
# Installer Flask-Limiter
from flask_limiter import Limiter

limiter = Limiter(app, key_func=get_remote_address)

@bp.post('/auth/login')
@limiter.limit("10 per minute")
def login():
    # ...
```

**Référence** : PLAN_ACTION.md § 1.5

---

### BUG-006 : CORS non configuré
**Priorité** : 🟠 ÉLEVÉE  
**Impact** : Frontend ne peut pas consommer l'API  
**Effort** : 1h

**Description** :  
Pas de configuration CORS. Un frontend hébergé sur un domaine différent ne pourra pas appeler l'API.

**Erreur frontend** :
```
Access to fetch at 'http://api.sticky-notes.com/v1/notes'
from origin 'http://frontend.sticky-notes.com' has been blocked by CORS policy:
No 'Access-Control-Allow-Origin' header is present
```

**Solution** :
```python
from flask_cors import CORS

CORS(app, resources={
    r"/v1/*": {
        "origins": ["https://frontend.sticky-notes.com"],
        "methods": ["GET", "POST", "PUT", "DELETE"]
    }
})
```

**Référence** : PLAN_ACTION.md § 1.6

---

### BUG-007 : Contraintes UNIQUE manquantes en DB
**Priorité** : 🟠 ÉLEVÉE  
**Impact** : Race conditions, doublons possibles  
**Effort** : 2h

**Description** :  
Les contraintes de doublon sont vérifiées en code Python, pas en base de données. Cela crée des race conditions.

**Scénario** :
```python
# Requête 1 et 2 en parallèle
# Les deux passent la vérification Python avant que l'une soit commitée
# → Doublon créé en DB
Contact(user_id=1, contact_user_id=2)  # Requête 1
Contact(user_id=1, contact_user_id=2)  # Requête 2 (doublon)
```

**Solution** :
```python
# Migration Alembic
op.create_unique_constraint(
    'uq_contact_user_contact',
    'contacts',
    ['user_id', 'contact_user_id']
)

op.create_unique_constraint(
    'uq_assignment_note_user',
    'assignments',
    ['note_id', 'user_id']
)
```

**Référence** : PLAN_ACTION.md § 2.1

---

## 🟡 BUGS MOYENS (7h)

### BUG-008 : finished_date référencé mais non existant
**Priorité** : 🟡 MOYENNE  
**Impact** : Erreur potentielle si utilisé  
**Effort** : 1h

**Description** :  
Le code `Note.to_details_dict()` référence un champ `finished_date` qui n'existe pas dans le modèle Note.

**Code problématique** :
```python
# backend/app/models/note.py
def to_details_dict(self, assignment=None):
    return {
        # ...
        "finished_date": self.finished_date.isoformat() if hasattr(self, "finished_date") and self.finished_date else None,
        # ↑ finished_date n'est pas défini en DB
    }
```

**Solutions possibles** :
1. Ajouter le champ en DB (migration)
2. Supprimer la référence

**Référence** : PLAN_ACTION.md § 2.2

---

### BUG-009 : Logs supprimables
**Priorité** : 🟡 MOYENNE  
**Impact** : Violation de traçabilité  
**Effort** : 30min

**Description** :  
La route DELETE `/v1/action_logs/<id>` permet de supprimer des logs. C'est un anti-pattern pour un système d'audit.

**Problème** :
```bash
# Un utilisateur peut supprimer ses propres logs
curl -X DELETE http://localhost:5000/v1/action_logs/123 \
  -H "Authorization: Bearer $TOKEN"
# → Log supprimé (perte de traçabilité)
```

**Solution** :  
Supprimer complètement cette route. Les logs doivent être immuables.

**Référence** : PLAN_ACTION.md § 3.3

---

### BUG-010 : Pas de pagination sur notes
**Priorité** : 🟡 MOYENNE  
**Impact** : Performance si milliers de notes  
**Effort** : 2h

**Description** :  
GET `/v1/notes` retourne TOUTES les notes sans limite. Problème de performance si un utilisateur a 1000+ notes.

**Problème** :
```bash
# Utilisateur avec 5000 notes
curl http://localhost:5000/v1/notes \
  -H "Authorization: Bearer $TOKEN"
# → Retourne 5000 notes d'un coup (lent)
```

**Solution** :
```python
@bp.get('/notes')
@jwt_required()
def get_notes():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    paginated = query.paginate(page=page, per_page=per_page)
    
    return {
        "notes": [n.to_dict() for n in paginated.items],
        "total": paginated.total,
        "pages": paginated.pages
    }
```

**Référence** : PLAN_ACTION.md § 3.1

---

### BUG-011 : Validation email basique
**Priorité** : 🟡 MOYENNE  
**Impact** : Emails invalides acceptés  
**Effort** : 1h

**Description** :  
La validation d'email actuelle est trop simple (`@` et `.` présents). Des emails invalides sont acceptés.

**Exemples acceptés à tort** :
```python
"test@test"        # Pas de TLD
"test @test.com"   # Espace
"@test.com"        # Pas de partie locale
```

**Solution** :
```python
from email_validator import validate_email

@validates('email')
def validate_email_field(self, key, email):
    try:
        valid = validate_email(email, check_deliverability=False)
        return valid.email
    except EmailNotValidError:
        raise ValueError("Email invalide")
```

**Référence** : PLAN_ACTION.md § 2.3

---

## 🟢 BUGS BAS / AMÉLIORATIONS (17h)

### BUG-012 : Pas de gestion compte verrouillé
**Priorité** : 🟢 BASSE  
**Impact** : Brute force facilité  
**Effort** : 4h

**Description** :  
Pas de verrouillage de compte après N échecs de connexion. Complément au rate limiting.

**Solution** :
```python
# Ajouter failed_login_attempts et locked_until
# Verrouiller après 5 échecs pour 30 minutes
if user.failed_login_attempts >= 5:
    user.locked_until = datetime.now() + timedelta(minutes=30)
```

**Référence** : PLAN_ACTION.md § 4.1

---

### BUG-013 : Pas de rotation logs
**Priorité** : 🟢 BASSE  
**Impact** : Table action_logs croissance infinie  
**Effort** : 3h

**Description** :  
Les logs ne sont jamais archivés ou supprimés. La table va grossir indéfiniment.

**Solution** :  
Archiver logs > 90 jours dans table `action_logs_archive`.

**Référence** : PLAN_ACTION.md § 4.2

---

### AMÉLIORATION-014 : Pas de monitoring
**Priorité** : 🟢 BASSE  
**Impact** : Pas de détection d'erreurs en production  
**Effort** : 2h

**Description** :  
Pas de monitoring (Sentry, Datadog). Impossible de détecter les erreurs en production.

**Solution** :
```python
import sentry_sdk
sentry_sdk.init(dsn="https://xxxxx@sentry.io/xxxxx")
```

**Référence** : PLAN_ACTION.md § 4.3

---

### AMÉLIORATION-015 : Pas de CI/CD
**Priorité** : 🟢 BASSE  
**Impact** : Tests manuels à chaque commit  
**Effort** : 4h

**Description** :  
Pas de GitHub Actions pour lancer automatiquement les tests.

**Solution** :  
Créer `.github/workflows/tests.yml` pour lancer pytest sur chaque push.

**Référence** : PLAN_ACTION.md § 4.4

---

## 📊 MATRICE DE PRIORISATION

```
┌─────────────────────────────────────────────────────────┐
│  IMPACT vs EFFORT                                       │
│                                                         │
│  Élevé │ BUG-005          │ BUG-001, 002   │          │
│  Impact│ Rate limit       │ BUG-003, 004   │          │
│        │ (2h)             │ Isolation      │          │
│        │                  │ (7h)           │          │
│  ──────┼──────────────────┼────────────────┼──────────┤
│        │ BUG-008          │ BUG-007        │ BUG-012  │
│  Moyen │ finished_date    │ UNIQUE DB      │ Account  │
│  Impact│ (1h)             │ (2h)           │ lock(4h) │
│        │ BUG-009 (0.5h)   │ BUG-010 (2h)   │          │
│  ──────┼──────────────────┼────────────────┼──────────┤
│        │                  │ BUG-006 CORS   │ BUG-013  │
│  Bas   │                  │ (1h)           │ Rotation │
│  Impact│                  │ BUG-011 Email  │ (3h)     │
│        │                  │ (1h)           │ A-14,15  │
└─────────────────────────────────────────────────────────┘
         Bas Effort         Moyen Effort      Haut Effort
```

**Priorité** :
1. 🔴 Haut impact + Moyen effort (BUG-001 à 004)
2. 🟠 Haut impact + Bas effort (BUG-005)
3. 🟠 Moyen impact + Moyen effort (BUG-007)
4. 🟡 Moyen impact + Bas effort (BUG-008, 009)

---

## ✅ PLAN DE CORRECTION

### Semaine 1 (9h)
- [x] BUG-001 : Isolation notes (2h)
- [x] BUG-002 : Isolation contacts (1h)
- [x] BUG-003 : Isolation assignments (2h)
- [x] BUG-004 : Isolation logs (2h)
- [x] BUG-005 : Rate limiting (2h)

**Livrable** : Bugs critiques corrigés ✅

### Semaine 2 (7h)
- [x] BUG-006 : CORS (1h)
- [x] BUG-007 : Contraintes UNIQUE (2h)
- [x] BUG-008 : finished_date (1h)
- [x] BUG-009 : Supprimer DELETE logs (0.5h)
- [x] BUG-010 : Pagination notes (2h)
- [x] BUG-011 : Email validation (1h)

**Livrable** : v1.2.0 Production-Ready ✅

### Semaine 3-4 (Optionnel, 17h)
- [ ] BUG-012 : Account lock (4h)
- [ ] BUG-013 : Rotation logs (3h)
- [ ] AMÉLIORATION-014 : Monitoring (2h)
- [ ] AMÉLIORATION-015 : CI/CD (4h)

**Livrable** : v1.3.0 Optimisé ✅

---

## 🔍 MÉTHODE DE DÉTECTION

Ces bugs ont été identifiés par :

✅ **Revue de code manuelle** : Analyse ligne par ligne  
✅ **Analyse de sécurité** : Vérification autorisation  
✅ **Tests de scénarios** : Simulation attaques  
✅ **Analyse architecture** : Patterns anti-sécurité  
✅ **Coverage analysis** : Parties non testées  

**Outils utilisés** :
- Grep/search pour trouver routes sans `@jwt_required`
- Analyse des queries SQL pour filtres manquants
- Tests manuels avec tokens de différents users

---

## 📞 SUPPORT

**Questions sur un bug ?**
- Consulter `PLAN_ACTION.md` pour le code de correction
- Consulter `AUDIT_COMPLET.md` pour l'analyse détaillée
- Ouvrir une issue GitHub avec référence bug (ex: BUG-001)

---

**Document créé par** : GitHub Copilot  
**Date** : 17 Octobre 2025  
**Dernière mise à jour** : 17 Octobre 2025
