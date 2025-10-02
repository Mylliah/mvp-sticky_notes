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
