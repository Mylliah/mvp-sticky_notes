# 🎨 Structure Frontend - MVP Sticky Notes

## 📐 Architecture Basée sur le Mockup

```
frontend/
├── src/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Header.tsx           # Logo + Filtres + Recherche
│   │   │   ├── Sidebar.tsx          # + / ●●● / M / ⚙️
│   │   │   ├── ContactsBar.tsx      # Tags contacts cliquables
│   │   │   └── Layout.tsx           # Container principal
│   │   │
│   │   ├── notes/
│   │   │   ├── NoteCard.tsx         # Miniature note dans la liste
│   │   │   ├── NoteList.tsx         # Grille de notes
│   │   │   ├── NoteModal.tsx        # Modal d'affichage/édition
│   │   │   ├── NoteForm.tsx         # Formulaire création/édition
│   │   │   └── NoteFilters.tsx      # Filtres (Important, En cours, etc.)
│   │   │
│   │   ├── contacts/
│   │   │   ├── ContactTag.tsx       # Tag contact cliquable
│   │   │   ├── ContactList.tsx      # Liste pour sélection
│   │   │   └── ContactModal.tsx     # Ajout/édition contact
│   │   │
│   │   └── common/
│   │       ├── Button.tsx           # Boutons réutilisables
│   │       ├── Input.tsx            # Champs input
│   │       ├── Modal.tsx            # Modal générique
│   │       ├── Tag.tsx              # Tag générique
│   │       └── Loader.tsx           # Spinner chargement
│   │
│   ├── pages/
│   │   ├── Login.tsx                # Page connexion
│   │   ├── Register.tsx             # Page inscription
│   │   ├── Dashboard.tsx            # Page principale (mockup)
│   │   ├── Contacts.tsx             # Gestion contacts
│   │   ├── Profile.tsx              # Profil utilisateur
│   │   └── Settings.tsx             # Paramètres
│   │
│   ├── api/
│   │   ├── axios.ts                 # Config + interceptors JWT
│   │   ├── auth.ts                  # Login/Register
│   │   ├── notes.ts                 # CRUD notes
│   │   ├── contacts.ts              # CRUD contacts
│   │   └── assignments.ts           # CRUD assignments
│   │
│   ├── hooks/
│   │   ├── useAuth.ts               # Gestion auth
│   │   ├── useNotes.ts              # Gestion notes
│   │   ├── useContacts.ts           # Gestion contacts
│   │   └── useFilters.ts            # Gestion filtres
│   │
│   ├── store/
│   │   └── authStore.ts             # État global (user, token)
│   │
│   ├── types/
│   │   ├── user.ts
│   │   ├── note.ts
│   │   ├── contact.ts
│   │   └── assignment.ts
│   │
│   ├── utils/
│   │   ├── formatDate.ts            # "créé le XX/XX/XX"
│   │   ├── constants.ts             # Constantes
│   │   └── colors.ts                # Palette couleurs
│   │
│   ├── App.tsx                      # Router principal
│   ├── main.tsx                     # Point d'entrée
│   └── index.css                    # Styles globaux
│
├── public/
│   ├── logo.svg
│   └── favicon.ico
│
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── Dockerfile
```

---

## 🎨 Composants Principaux (correspondance mockup)

### 1. **Dashboard.tsx** (Page principale)
```tsx
<Layout>
  <Header />              {/* Logo + Filtres + Recherche */}
  <ContactsBar />         {/* Tags: Moi, Laura, Jean... */}
  <NoteList />            {/* Grille de notes */}
  <NoteModal />           {/* Modal affichage note */}
</Layout>
```

### 2. **Header.tsx**
- Logo (coin gauche)
- Filtres : Important / En cours / Terminé / Reçus / Émis / Date ↑↓
- Icône recherche 🔍

### 3. **ContactsBar.tsx**
- Récupère `GET /contacts`
- Affiche tags cliquables
- Filtre notes par contact
- Tag "Moi" = notes envoyées par vous

### 4. **NoteCard.tsx**
- Icône édition ✏️
- Aperçu texte
- Destinataire (de XXX / à XXX)
- Date création

### 5. **NoteModal.tsx**
- Actions : ❗(Important) / ✓ (Statut) / ℹ️ (Info) / 🗑️ (Supprimer) / ✕ (Fermer)
- Contenu note
- Bouton validation ✓

### 6. **Sidebar.tsx**
- [+] Créer note
- [●●●] Menu
- [M] Profil
- [⚙️] Paramètres

---

## 🎨 Palette de Couleurs (basée sur mockup)

```css
/* Couleurs principales */
--primary: #5B5B87        /* Violet foncé (boutons, sidebar) */
--primary-light: #8B8BA7  /* Violet clair (tags inactifs) */
--primary-hover: #4A4A6E  /* Hover boutons */

/* Backgrounds */
--bg-main: #F5F5F7        /* Fond principal */
--bg-card: #FFFFFF        /* Fond cartes notes */
--bg-sidebar: #3A3A52     /* Sidebar gauche */

/* Textes */
--text-primary: #2C2C3E   /* Texte principal */
--text-secondary: #8B8B99 /* Texte secondaire (dates) */
--text-light: #FFFFFF     /* Texte sur fond foncé */

/* États */
--success: #4CAF50        /* Terminé */
--warning: #FFA726        /* Important */
--info: #29B6F6           /* En cours */
--error: #EF5350          /* Erreur */

/* Bordures */
--border: #E0E0E5
--border-active: #5B5B87
```

---

## 📱 Responsive Design

### Desktop (>1024px)
```
┌──┬────────────────────────┐
│  │  Header                │
│S ├────────────────────────┤
│I │  ContactsBar           │
│D ├────────────────────────┤
│E │  ┌───┐ ┌───┐ ┌───┐    │
│B │  │Note│Note│Note│      │
│A │  └───┘ └───┘ └───┘    │
│R │                        │
└──┴────────────────────────┘
```

### Tablet (768px-1024px)
- Sidebar rétractable
- 2 colonnes de notes

### Mobile (<768px)
- Sidebar en burger menu
- 1 colonne de notes
- ContactsBar défilable horizontalement

---

## 🎯 Fonctionnalités par Composant

### **Header**
- [ ] Filtres : Important, En cours, Terminé, Reçus, Émis
- [ ] Tri : Date croissante/décroissante
- [ ] Recherche notes (par contenu)
- [ ] Badge notifications (notes non lues)

### **ContactsBar**
- [ ] Afficher tous les contacts
- [ ] Tag "Moi" pour notes créées par vous
- [ ] Clic sur tag = filtre notes de ce contact
- [ ] Tag actif = style différent
- [ ] Ajout rapide contact (+)

### **NoteList**
- [ ] Grille responsive
- [ ] Pagination (infinite scroll)
- [ ] Tri par date
- [ ] Filtres combinés

### **NoteCard**
- [ ] Icône édition ✏️
- [ ] Aperçu contenu (150 caractères)
- [ ] Nom contact
- [ ] Date formatée
- [ ] Indicateur important (⭐)
- [ ] Indicateur statut (✓ terminé)

### **NoteModal**
- [ ] Affichage contenu complet
- [ ] Édition inline
- [ ] Actions : Important, Supprimer, Fermer
- [ ] Changer statut (en cours/terminé)
- [ ] Info assignation

### **Sidebar**
- [ ] Bouton créer note (+)
- [ ] Menu (●●●) : Dashboard, Contacts, Profil, Déconnexion
- [ ] Avatar utilisateur (M)
- [ ] Paramètres (⚙️)

---

## 🔄 Flux Utilisateur Principal

```
1. Login → Dashboard
2. Voir liste notes (filtrées par défaut)
3. Clic sur contact → Filtre notes de ce contact
4. Clic sur note → Modal d'affichage
5. Éditer note → Sauvegarde auto
6. Créer note (+) → Modal création
7. Assigner à contact → Sélecteur
8. Marquer important → Étoile jaune
9. Marquer terminé → Coche verte
```

---

## 📦 Dépendances Nécessaires

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.0",
    "@tanstack/react-query": "^5.0.0",
    "zustand": "^4.4.0",
    "date-fns": "^2.30.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "typescript": "^5.2.0",
    "vite": "^5.0.0",
    "tailwindcss": "^3.3.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0"
  }
}
```

---

## 🎯 Prochaines Étapes

1. ✅ Créer structure de base
2. ✅ Setup Docker
3. 🔲 Créer Layout + Sidebar
4. 🔲 Créer Header + Filtres
5. 🔲 Créer ContactsBar
6. 🔲 Créer NoteList + NoteCard
7. 🔲 Créer NoteModal
8. 🔲 Connecter à l'API backend

**On commence par quelle partie ?** 🚀
