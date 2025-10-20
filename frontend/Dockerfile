# Utilise l'image Node.js version 20 (LTS = Long Term Support)
FROM node:20-alpine

# Définit le dossier de travail dans le container
WORKDIR /app

# Copie package.json dans le container
# Pourquoi d'abord ? Pour profiter du cache Docker
COPY package*.json ./

# Install les dépendances npm
RUN npm install

# Copie tout le reste du code
COPY . .

# Expose le port 3000 (port par défaut de Vite)
EXPOSE 3000

# Commande pour démarrer Vite en mode dev
# --host 0.0.0.0 = accessible depuis l'extérieur du container
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
