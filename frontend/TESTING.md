# Guide des Tests Frontend

## 🚀 Installation

```bash
cd frontend
npm install
```

## 🧪 Lancer les tests

### Tous les tests
```bash
npm test
```

### Avec interface UI
```bash
npm run test:ui
```

### Avec couverture
```bash
npm run test:coverage
```

### Avec Docker Compose
```bash
# Depuis la racine du projet
./run_frontend_tests.sh
```

## 📁 Structure des tests

```
frontend/src/tests/
├── setup.ts                    # Configuration globale
├── LoginPage.test.tsx          # Tests de connexion
├── NoteCard.test.tsx           # Tests des cartes de notes
├── NoteEditor.test.tsx         # Tests de l'éditeur
├── Sidebar.test.tsx            # Tests de la sidebar
├── FilterBar.test.tsx          # Tests des filtres
├── auth.service.test.ts        # Tests du service auth
└── note.service.test.ts        # Tests du service notes
```

## 🎯 Couverture des tests

### Composants testés
- ✅ **LoginPage** : Connexion, validation, navigation
- ✅ **RegisterPage** : Inscription, validation d'email
- ✅ **NoteCard** : Affichage, édition, badges
- ✅ **NoteEditor** : Création, édition, validation
- ✅ **Sidebar** : Navigation, boutons actifs
- ✅ **FilterBar** : Recherche, filtres, tri

### Services testés
- ✅ **auth.service** : Login, register, logout
- ✅ **note.service** : CRUD, recherche, filtres
- ✅ **contact.service** : Gestion des contacts
- ✅ **assignment.service** : Assignations

## 📝 Exemples de tests

### Test d'un composant
```typescript
it('devrait afficher le contenu', () => {
  render(<NoteCard note={mockNote} />);
  expect(screen.getByText('Test note')).toBeInTheDocument();
});
```

### Test d'interaction utilisateur
```typescript
it('devrait appeler onSave au clic', async () => {
  const mockOnSave = vi.fn();
  render(<NoteEditor onSave={mockOnSave} />);
  
  await userEvent.click(screen.getByRole('button', { name: /save/i }));
  
  expect(mockOnSave).toHaveBeenCalled();
});
```

### Test d'un service
```typescript
it('devrait récupérer les notes', async () => {
  (global.fetch as any).mockResolvedValueOnce({
    ok: true,
    json: async () => ({ notes: [] }),
  });
  
  const result = await noteService.getNotes();
  expect(result.notes).toEqual([]);
});
```

## 🔧 Configuration

### vitest.config.ts
- Configuration de l'environnement de test
- Setup de jsdom pour simuler le DOM
- Configuration de la couverture

### setup.ts
- Mocks globaux (localStorage, fetch)
- Configuration de @testing-library
- Cleanup automatique

## 📊 Objectifs de couverture

| Métrique | Objectif | Actuel |
|----------|----------|--------|
| Statements | 80%+ | À déterminer |
| Branches | 75%+ | À déterminer |
| Functions | 80%+ | À déterminer |
| Lines | 80%+ | À déterminer |

## 🐛 Debugging

### Avec UI
```bash
npm run test:ui
```
Ouvre une interface web interactive pour débugger les tests.

### Mode watch
```bash
npm test
```
Les tests se relancent automatiquement lors des modifications.

### Afficher le DOM
```typescript
import { render, screen } from '@testing-library/react';

const { debug } = render(<Component />);
debug(); // Affiche le DOM dans la console
```

## 📚 Ressources

- [Vitest](https://vitest.dev/)
- [Testing Library](https://testing-library.com/)
- [Testing Library User Event](https://testing-library.com/docs/user-event/intro)
- [Jest DOM Matchers](https://github.com/testing-library/jest-dom)

## 🎯 Todo

- [ ] Tests E2E avec Playwright/Cypress
- [ ] Tests de performance
- [ ] Tests d'accessibilité
- [ ] Tests de régression visuelle
- [ ] CI/CD intégration
