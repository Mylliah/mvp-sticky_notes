#!/bin/bash

echo "=================================="
echo "🔍 DIAGNOSTIC COMPLET DES BASES DE DONNÉES"
echo "=================================="
echo ""

echo "1️⃣  BACKEND DOCKER - Utilisateurs dans la DB"
echo "-------------------------------------------"
docker compose exec -T db psql -U app -d appdb -c "SELECT COUNT(*) as total_users FROM users;" 2>/dev/null
docker compose exec -T db psql -U app -d appdb -c "SELECT id, username FROM users ORDER BY id LIMIT 15;" 2>/dev/null
echo ""

echo "2️⃣  PROCESSUS POSTGRES"
echo "-------------------------------------------"
ps aux | grep postgres | grep -v grep
echo ""

echo "3️⃣  PORTS OCCUPÉS"
echo "-------------------------------------------"
echo "Port 5000 (Backend):"
ss -tlnp 2>/dev/null | grep ":5000" || echo "  Libre"
echo ""
echo "Port 5432 (PostgreSQL):"
ss -tlnp 2>/dev/null | grep ":5432" || echo "  Libre"
echo ""
echo "Port 3001 (Frontend):"
ss -tlnp 2>/dev/null | grep ":3001" || echo "  Libre"
echo ""

echo "4️⃣  PROCESSUS FLASK/PYTHON"
echo "-------------------------------------------"
ps aux | grep -E "flask|python.*app" | grep -v grep | grep -v docker
echo ""

echo "5️⃣  CONFIGURATION DOCKER"
echo "-------------------------------------------"
echo "DATABASE_URL dans backend:"
docker compose exec -T backend env | grep DATABASE_URL
echo ""
echo "VITE_API_URL dans frontend:"
docker compose exec -T frontend env | grep VITE_API_URL || echo "  Non défini"
echo ""

echo "6️⃣  TEST API DIRECTE"
echo "-------------------------------------------"
echo "Test de /health sur localhost:5000:"
curl -s http://localhost:5000/health 2>/dev/null || echo "  ❌ Pas de réponse"
echo ""

echo "7️⃣  CONTENEURS DOCKER"
echo "-------------------------------------------"
docker compose ps
echo ""

echo "=================================="
echo "✅ Diagnostic terminé"
echo "=================================="
