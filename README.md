MVP Sticky-notes Project - Coming soon... 



---------

# MVP Sticky Notes — J1

## Démarrer en dev
docker compose up -d --build
# API: http://localhost:5000/health
# DB Adminer: http://localhost:8080 (System: PostgreSQL, Server: db, user: app, pass: app, db: appdb)

## Migrations (dans le conteneur)
docker compose exec -it backend flask db migrate -m "message"
docker compose exec -it backend flask db upgrade

## Commandes utiles
docker compose logs backend -f
docker compose exec -it db psql -U app -d appdb
docker compose down  # stop; docker compose down -v => reset data


# MVP Sticky Notes — J2 

Justifications choix : Migration Alembic
But : Mettre à jour la base de données PostgreSQL pour qu’elle corresponde exactement aux modèles Python (tables, colonnes, relations). Alembic (via Flask-Migrate) crée des scripts de "migration" qui versionnent et appliquent les évolutions du schéma, ce qui permet de :
- Synchroniser la structure de la base de données avec le code à chaque modification (ajout d’une colonne, nouvelle table, suppression...)
- Garder l’historique de toutes les évolutions du schéma pour revenir en arrière ou déployer sur plusieurs environnements.
- Sécuriser le projet en évitant les erreurs de structures ou d’incohérence (tests, production).

Workflow typique :
- On écrit ou modifie les modèles.
- On génère une migration : `flask db migrate -m "Ajout des modèles principaux"` (cela crée un script dans le dossier `migrations`).
- On vérifie le script (éventuellement on l'ajuste si besoin).
- On applique la migration à la base : `flask db upgrade` (cela crée/modifie les tables réelles).
Cela rend le projet robuste et évolutif, car toute modification du modèle passe par des migrations suivies et maîtrisées.

## Création des Endpoints pour chaque entité

1. But des Endpoints CRUD pour Note
- Create (POST) : créer une nouvelle note depuis les données envoyées par le frontend.
- Read (GET) : récupérer la liste de toutes les notes, ou une note précise par son id.
- Update (PUT/PATCH) : modifier le contenu (ex : titre) d’une note en base.
- Delete (DELETE) : supprimer une note existante.
Cela permet de valider l’API du MVP et de connecter tous les clients (front, tests manuels, outils d’automatisation).