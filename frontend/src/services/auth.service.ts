import { LoginRequest, LoginResponse, User } from '../types/auth.types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';
const API_BASE = `${API_URL}/v1`;

export const authService = {
  // S'inscrire
  async register(userData: { username: string; email: string; password: string }): Promise<LoginResponse> {
    const response = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Erreur lors de l\'inscription' }));
      throw new Error(error.message || 'Impossible de créer le compte');
    }

    const data: LoginResponse = await response.json();
    
    // Sauvegarder automatiquement le token après l'inscription
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('user', JSON.stringify(data.user));
    
    return data;
  },

  // Se connecter
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Erreur de connexion' }));
      throw new Error(error.message || 'Email ou mot de passe incorrect');
    }

    const data: LoginResponse = await response.json();
    
    // Sauvegarder le token dans localStorage
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('user', JSON.stringify(data.user));
    
    return data;
  },

  // Se déconnecter
  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  },

  // Récupérer l'utilisateur courant
  getCurrentUser(): User | null {
    const userStr = localStorage.getItem('user');
    if (!userStr) return null;
    
    try {
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  },

  // Vérifier si l'utilisateur est connecté
  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  },

  // Récupérer le token
  getToken(): string | null {
    return localStorage.getItem('access_token');
  },
};
