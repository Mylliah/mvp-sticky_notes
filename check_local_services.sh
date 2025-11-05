#!/bin/bash

echo "🔍 Vérification des services locaux qui pourraient interférer avec Docker..."
echo ""

# Vérifier Flask
FLASK_PROCESSES=$(ps aux | grep -E "flask run" | grep -v grep)
if [ -n "$FLASK_PROCESSES" ]; then
    echo "⚠️  ATTENTION : Flask tourne localement !"
    echo "$FLASK_PROCESSES"
    echo ""
else
    echo "✅ Aucun Flask local détecté"
fi

# Vérifier Vite/Node
VITE_PROCESSES=$(ps aux | grep -E "vite|npm run dev" | grep -v -E "grep|vscode-server" | head -5)
if [ -n "$VITE_PROCESSES" ]; then
    echo "⚠️  ATTENTION : Vite/npm tourne localement !"
    echo "$VITE_PROCESSES"
    echo ""
else
    echo "✅ Aucun Vite/npm local détecté"
fi

# Vérifier les ports
echo ""
echo "🔌 Ports utilisés :"
PORTS=$(ss -tlnp | grep -E ":3000|:3001|:5000|:5432" 2>/dev/null)
if [ -n "$PORTS" ]; then
    echo "$PORTS"
else
    echo "✅ Aucun des ports 3000, 3001, 5000, 5432 n'est utilisé"
fi

echo ""
echo "✨ Vérification terminée !"
