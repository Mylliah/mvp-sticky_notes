import { User } from '../types/auth.types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';
const API_BASE = `${API_URL}/v1`;

// Récupérer le token depuis localStorage
function getAuthToken(): string | null {
  return localStorage.getItem('access_token');
}

// Headers avec authentification
function getHeaders(): HeadersInit {
  const token = getAuthToken();
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` }),
  };
}

// Fonction helper pour gérer les erreurs API
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'Unknown error' }));
    throw new Error(error.message || `HTTP error ${response.status}`);
  }
  return response.json();
}

// Cache pour les utilisateurs
const userCache = new Map<number, User>();

export const userService = {
  // Récupérer un utilisateur par son ID
  async getUser(userId: number): Promise<User> {
    // Vérifier le cache d'abord
    if (userCache.has(userId)) {
      return userCache.get(userId)!;
    }

    const response = await fetch(`${API_BASE}/users/${userId}`, {
      headers: getHeaders(),
    });
    const user = await handleResponse<User>(response);
    
    // Mettre en cache
    userCache.set(userId, user);
    
    return user;
  },

  // Récupérer plusieurs utilisateurs
  async getUsers(userIds: number[]): Promise<Map<number, User>> {
    const usersMap = new Map<number, User>();
    const toFetch: number[] = [];

    // Vérifier le cache
    for (const id of userIds) {
      if (userCache.has(id)) {
        usersMap.set(id, userCache.get(id)!);
      } else {
        toFetch.push(id);
      }
    }

    // Récupérer les utilisateurs manquants
    if (toFetch.length > 0) {
      await Promise.all(
        toFetch.map(async (id) => {
          try {
            const user = await this.getUser(id);
            usersMap.set(id, user);
          } catch (err) {
            console.error(`Error fetching user ${id}:`, err);
          }
        })
      );
    }

    return usersMap;
  },

  // Récupérer tous les utilisateurs
  async getAllUsers(): Promise<User[]> {
    const response = await fetch(`${API_BASE}/users`, {
      headers: getHeaders(),
    });
    const users = await handleResponse<User[]>(response);
    
    // Mettre en cache
    users.forEach(user => userCache.set(user.id, user));
    
    return users;
  },

  // Vider le cache
  clearCache() {
    userCache.clear();
  },

  // Rechercher des utilisateurs par username
  async searchUsers(query: string): Promise<User[]> {
    const response = await fetch(`${API_BASE}/users?search=${encodeURIComponent(query)}`, {
      headers: getHeaders(),
    });
    return handleResponse<User[]>(response);
  },
};
