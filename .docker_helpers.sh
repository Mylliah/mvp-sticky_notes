#!/bin/bash

# Alias et helpers pour éviter les erreurs de DB

# Vérifier qu'on utilise bien Docker
check_docker() {
    if ps aux | grep -E "flask run" | grep mynh | grep -v grep > /dev/null; then
        echo "⚠️  ATTENTION : Flask tourne en LOCAL ! Arrêtez-le d'abord :"
        echo "   ./fix_db_once_and_for_all.sh"
        return 1
    fi
    
    if ! docker compose ps | grep backend | grep -q "Up"; then
        echo "⚠️  ATTENTION : Backend Docker n'est pas démarré !"
        echo "   docker compose up -d"
        return 1
    fi
    
    echo "✅ Configuration OK : Backend Docker tourne"
    return 0
}

# Alias pour lancer les tests en toute sécurité
alias test-safe='check_docker && ./run_all_tests.sh'
alias test-api='check_docker && ./test_api_complete.sh'
alias test-curl='check_docker && ./test_api_curl.sh'

echo "🔧 Helpers chargés !"
echo "Commandes disponibles :"
echo "  - check_docker        : Vérifier la configuration"
echo "  - test-safe          : Lancer les tests pytest (vérifie Docker d'abord)"
echo "  - test-api           : Lancer les tests API (vérifie Docker d'abord)"
echo "  - test-curl          : Lancer les tests curl (vérifie Docker d'abord)"
