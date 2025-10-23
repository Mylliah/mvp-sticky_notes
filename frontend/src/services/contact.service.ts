import { Contact, ContactRelationship } from '../types/contact.types';

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

export const contactService = {
  // Récupérer tous les contacts de l'utilisateur
  async getContacts(): Promise<ContactRelationship[]> {
    const response = await fetch(`${API_BASE}/contacts`, {
      headers: getHeaders(),
    });
    return handleResponse(response);
  },

  // Récupérer tous les utilisateurs (pour recherche)
  async getAllUsers(): Promise<Contact[]> {
    const response = await fetch(`${API_BASE}/users`, {
      headers: getHeaders(),
    });
    const data = await handleResponse<{ users: Contact[] }>(response);
    return data.users;
  },

  // Ajouter un contact
  async addContact(contactId: number): Promise<ContactRelationship> {
    const response = await fetch(`${API_BASE}/contacts`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ contact_id: contactId }),
    });
    return handleResponse(response);
  },

  // Supprimer un contact
  async removeContact(contactId: number): Promise<void> {
    const response = await fetch(`${API_BASE}/contacts/${contactId}`, {
      method: 'DELETE',
      headers: getHeaders(),
    });
    if (!response.ok) {
      throw new Error('Failed to remove contact');
    }
  },
};
