# 🎯 Guide de Test - Système d'Assignation de Notes

## ✅ Fonctionnalités Implémentées

### 1. **Drag & Drop de Notes** 🎨
- ✅ Les cartes de notes sont maintenant **draggables** (curseur en forme de main)
- ✅ Feedback visuel pendant le drag (opacité réduite, échelle 95%)
- ✅ Les notes peuvent être glissées vers les badges de contacts

### 2. **Badges de Contacts en Bas** 👥
- ✅ Panel fixé en bas de page avec badges circulaires colorés
- ✅ Badge "Moi" en premier avec couleur distinctive (rose)
- ✅ Initiales des contacts dans les badges
- ✅ Dégradés de couleurs pour chaque contact
- ✅ Highlight au survol pendant le drag (fond bleu + agrandissement)

### 3. **Assignation de Notes** 📤
- ✅ Drop d'une note sur un contact crée une assignation (POST /v1/assignments)
- ✅ Toast de confirmation "Note assignée à [contact] ✓"
- ✅ Bouton "Annuler" dans le toast (actif pendant 5 secondes)
- ✅ Suppression de l'assignation si "Annuler" est cliqué (DELETE /v1/assignments/{id})

### 4. **Notifications Toast** 🔔
- ✅ Position: top-right
- ✅ Auto-dismiss après 5 secondes
- ✅ Animation slide-in/slide-out
- ✅ Types: success, error, info, warning
- ✅ Actions personnalisables (bouton Annuler)

## 🧪 Scénarios de Test

### Test 1: Drag & Drop Basique
1. **Connectez-vous** à l'application (alice@test.com / password123)
2. **Créez une nouvelle note** avec le bouton "+ Nouvelle Note"
3. **Cliquez et maintenez** sur une note
4. **Glissez la note** vers un badge de contact en bas
5. ✅ **Vérifiez** que le badge s'illumine en bleu au survol
6. **Relâchez** sur le badge
7. ✅ **Vérifiez** qu'un toast apparaît : "Note assignée à [contact] ✓"

### Test 2: Annulation d'Assignation
1. **Assignez une note** à un contact (voir Test 1)
2. **Attendez** que le toast apparaisse
3. **Cliquez sur "Annuler"** dans le toast (avant 5 secondes)
4. ✅ **Vérifiez** qu'un nouveau toast apparaît : "Attribution annulée"
5. ✅ **Vérifiez** que l'assignation a été supprimée dans la base de données

### Test 3: Multi-Assignation
1. **Assignez la même note** à plusieurs contacts différents
2. ✅ **Vérifiez** qu'un toast apparaît pour chaque assignation
3. ✅ **Vérifiez** que chaque assignation est créée dans la base de données

### Test 4: Feedback Visuel
1. **Commencez à glisser** une note
2. ✅ **Vérifiez** que la note devient semi-transparente (opacity: 0.5)
3. ✅ **Vérifiez** que le curseur change
4. **Survolez un badge** de contact
5. ✅ **Vérifiez** que le badge s'agrandit et change de couleur (bleu)
6. **Relâchez en dehors** d'un badge
7. ✅ **Vérifiez** que rien ne se passe (pas d'assignation)

## 🔍 Vérifications Backend

### Vérifier les Assignations Créées
```bash
# Dans le terminal
docker compose exec db psql -U app -d appdb -c "SELECT * FROM assignments ORDER BY assigned_date DESC LIMIT 5;"
```

### Vérifier les Logs
```bash
# Logs frontend
docker compose logs frontend -f

# Logs backend
docker compose logs backend -f
```

## 🐛 Résolution de Problèmes

### Le drag ne fonctionne pas
- ✅ Vérifiez que `draggable={true}` est bien sur les NoteCard
- ✅ Vérifiez que `onDragStart` et `onDragEnd` sont appelés
- ✅ Consultez la console du navigateur (F12)

### Le toast n'apparaît pas
- ✅ Vérifiez que ToastContainer est bien dans NotesPage
- ✅ Vérifiez que `useToast()` est appelé
- ✅ Vérifiez que `__addToast` est défini dans window

### L'assignation ne se crée pas
- ✅ Vérifiez les logs backend: `docker compose logs backend -f`
- ✅ Vérifiez que l'API POST /v1/assignments fonctionne
- ✅ Vérifiez l'authentification (token JWT)

### Le badge ne s'illumine pas
- ✅ Vérifiez que `onDragOver`, `onDragLeave`, `onDrop` sont bien sur ContactBadges
- ✅ Vérifiez que `e.preventDefault()` est appelé dans `onDragOver`
- ✅ Vérifiez le CSS `.contact-badge.drag-over`

## 📊 API Endpoints Utilisés

### POST /v1/assignments
```json
{
  "note_id": 123,
  "assignee_id": 456,
  "status": "pending" // optionnel
}
```

### DELETE /v1/assignments/{id}
Supprime (soft delete) l'assignation

### GET /v1/assignments
Récupère les assignations (avec filtres optionnels)

## 🎨 Correspondance avec le Mockup

| Fonctionnalité Mockup | État | Notes |
|----------------------|------|-------|
| Badges circulaires en bas | ✅ | Implémenté avec ContactBadges |
| Drag & drop des notes | ✅ | Implémenté sur NoteCard |
| Highlight au survol | ✅ | Classe `.drag-over` |
| Toast de confirmation | ✅ | ToastContainer + useToast |
| Bouton Annuler | ✅ | Action dans le toast |
| Multi-attribution | ✅ | Pas de limite |
| Feedback visuel | ✅ | Opacity + scale pendant drag |

## 🚀 Prochaines Étapes

### Phase 2 - Améliorations
1. **Afficher le nom réel du contact** dans le toast (actuellement "contact #123")
2. **Indicateurs visuels** sur les notes assignées
3. **Compteur de notes non lues** sur les badges
4. **Animation pulse** sur le badge après assignation
5. **Récupérer les détails de l'assignation** pour affichage

### Phase 3 - Fonctionnalités Avancées
6. **Panneau Info** avec détails d'assignation
7. **Statuts visuels** (en cours, terminé) sur les vignettes
8. **Filtres par statut** d'assignation
9. **Debouncing** sur la recherche
10. **Gestion des contacts** (ajout/édition/suppression)

## 🎉 Félicitations !

Vous avez maintenant un **système complet de drag & drop** pour assigner des notes aux contacts, avec :
- ✨ Feedback visuel fluide
- 🔔 Notifications toast élégantes
- ↩️ Possibilité d'annulation
- 🎯 Multi-attribution
- 📱 Interface responsive

Le MVP prend vraiment forme ! 🚀
