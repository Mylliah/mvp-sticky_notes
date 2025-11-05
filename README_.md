# HBNB - Client Web Simple


## Objectif du projet

Cette **part 4** du projet **HBnB** consiste à construire un **client web front-end** en utilisant des technologies modernes (**HTML5**, **CSS3** et **JavaScript ES6**) afin d’interagir avec l’**API RESTful** développée dans les parties précédentes. Mon objectif a été de créer une interface simple, responsive et interactive avec les fonctionnalités suivantes :
- Se connecter via un système d’authentification JWT
- Parcourir les lieux disponibles
- Voir les détails d’un lieu
- Filtrer les lieux par prix
- Ajouter des avis (uniquement pour les utilisateurs connectés)


---


## Fonctionnalités principales

### Authentification
- Formulaire de connexion (email + mot de passe)
- Envoie une requête `POST` vers `/api/v1/auth/login`
- Stocke le token JWT dans un **cookie**
- Déconnexion automatique si le token expire

### Liste des lieux
- Requête `GET /api/v1/places`
- Affichage sous forme de **cartes responsives**
- Affiche prix, image, bouton de détails
- **Filtrage côté client** par prix maximal (`10`, `50`, `100`, `Tous`)

### Détails d’un lieu
- Requête `GET /api/v1/places/:id`
- Affiche :
  - Titre
  - Hôte
  - Prix
  - Description
  - Commodités (amenities)
  - Avis (reviews)
- Affiche le formulaire "Ajouter un avis" si l’utilisateur est connecté

### Ajout d’un avis
- Disponible uniquement si connecté
- Envoie une requête `POST` vers `/api/v1/reviews/`
- Formulaire avec validation, gestion d’erreurs et redirection


---


## Objectifs pédagogiques

Ce projet vise à consolider les bases du développement web côté client et à renforcer la compréhension de l’architecture web moderne.

### Compétences développées :
- Structuration sémantique en **HTML5**
- Application du **modèle de boîte CSS** pour concevoir des interfaces propres et responsives
- Utilisation du **JavaScript moderne (ES6)** pour la manipulation du DOM
- Utilisation de **Fetch API** pour interagir avec des services RESTful
- Gestion des **sessions utilisateur via JWT et cookies**
- Contrôle de l'affichage dynamique selon l'état d’authentification
- Compréhension des mécanismes de **CORS** et d’interaction sécurisée client/serveur
- Intégration d’une **authentification basée sur token** dans un front statique


---


## Architecture du projet

```
├── 📁 client/
│ ├── 📄 index.html  → Page principale (liste des lieux)
│ ├── 📄 place.html  → Détails d’un lieu
│ ├── 📄 login.html  → Page de connexion
│ ├── 📄 add_review.html  → Formulaire pour ajouter un avis
│ ├── 📄 styles.css  → Feuille de style CSS
│ ├── 📄 index.js  → JS pour la liste des lieux
│ ├── 📄 place.js  → JS pour les détails
│ ├── 📄 login.js  → JS pour l'authentification
│ ├── 📄 add_review.js  → JS pour le formulaire d’avis
│ ├── 📄 logo.png  → Logo de l’application
│ └── 📄 favicon.ico  → Favicon
```


---


## Technologies utilisées

-  **HTML5** : Structure sémantique, accessibilité 
-  **CSS3** : Mise en page, design responsive 
-  **JavaScript (ES6)** : Manipulation du DOM, Fetch API, JWT 
-  **Fetch API** : Requêtes asynchrones vers l’API 
-  **Cookies** : Gestion de la session utilisateur 
-  **Responsive Design** : Utilisation de Grid/Flexbox 


---


## Installation & Lancement

### Prérequis
- Python 3.12+
- pip
- virtualenv (optionnel mais recommandé)
- Node.js (pour servir le front localement)

### Installation du Back-end

```bash
git clone https://github.com/Mylliah/holbertonschool-hbnb.git
cd part4/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Lancement

```bash
python3 run.py
```

Le serveur démarre sur `http://127.0.0.1:5000/`

### Lancement du Front-end (Partie 4)

```bash
cd ../part4/client/
npx http-server -p 5500
```

Le client sera accessible à l’adresse : `http://127.0.0.1:5500/client/index.html`
Assurez-vous que le serveur back-end est déjà lancé avant d’ouvrir le client front-end.


---


## 🔐 Identifiants administrateur

Pour faciliter les tests, voici un compte administrateur par défaut :

- **Email** : `admin@hbnb.io`  
- **Mot de passe** : `adminpass`


---


## Exemple d’utilisation des fonctionnalités disponibles

### Connexion via le formulaire (`login.html`)

Remplir les champs email et mot de passe, puis cliquer sur “Login”.  
Un cookie `token` est alors enregistré automatiquement et utilisé pour les appels suivants.

### Navigation vers la liste des lieux (`index.html`)

- Accessible à tous (même non authentifié)
- Filtrage dynamique des lieux par prix (`10`, `50`, `100`, `Tous`)
- Chaque lieu contient un bouton "View Details"

### Page de détails (`place.html?id=<place_id>`)

- Affiche les détails du lieu : titre, hôte, prix, description, commodités
- Affiche les avis existants
- Si connecté → bouton “Ajouter un avis” visible

### Formulaire d’ajout d’un avis (`add_review.html?id=<place_id>`)

- Accessible uniquement si l’utilisateur est connecté
- Soumission d’un avis :
  - champ texte
  - note (1 à 5 étoiles)
- Redirection automatique vers la page du lieu après soumission

### Déconnexion

Depuis n’importe quelle page, bouton "Logout" visible si connecté  
→ Supprime le cookie `token` et rafraîchit la page


---


## Captures d’écran

**Page d'accueil - liste des lieux :**
<p align="center">
  <a href="screenshots_front/index_page_places_list.jpg">
    <img src="screenshots_front/index_page_places_list.jpg" alt="Page d'accueil - Liste des lieux" width="500">
  </a>
</p>

**Page de connexion :**
<p align="center">
  <a href="screenshots_front/login_page.jpg">
    <img src="screenshots_front/login_page.jpg" alt="Page de connexion" width="500">
  </a>
</p>

**Détails d'un lieu :**
<p align="center">
  <a href="screenshots_front/view_place_details.jpg">
    <img src="screenshots_front/view_place_details.jpg" alt="Détails d'un lieu" width="500">
  </a>
</p>

**Ajout d'un avis si connecté :**
<p align="center">
  <a href="screenshots_front/add_review_if_connected.jpg">
    <img src="screenshots_front/add_review_if_connected.jpg" alt="Ajout d'un commentaire possible si connecté" width="500">
  </a>
</p>

**si non connecté, vue des détails du lieu seulement :**
<p align="center">
  <a href="screenshots_front/only_view_review_not_connected.jpg">
    <img src="screenshots_front/only_view_review_not_connected.jpg" alt="Vue commentaires seulement si non connecté" width="500">
  </a>
</p>

**Tri par prix :**
<p align="center">
  <a href="screenshots_front/sorting_by_price.jpg">
    <img src="screenshots_front/sorting_by_price.jpg" alt="Tri par prix" width="500">
  </a>
</p>

**Tentative d'ajout d'un second commentaire par le même utilisateur :**
<p align="center">
  <a href="screenshots_front/already_add_review_message.jpg">
    <img src="screenshots_front/already_add_review_message.jpg" alt="Tri par prix" width="500">
  </a>
</p>

**Champ laissé vide pendant l'ajout d'un avis :**
<p align="center">
  <a href="screenshots_front/field_empty.jpg">
    <img src="screenshots_front/field_empty.jpg" alt="Tri par prix" width="500">
  </a>
</p>


---


## Auteurs

- [Mylliah](https://github.com/Mylliah)