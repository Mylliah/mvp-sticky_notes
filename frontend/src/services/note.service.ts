import { Note, CreateNoteRequest, UpdateNoteRequest } from '../types/note.types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';
const API_BASE = `${API_URL}/v1`;

// Fonction helper pour gérer les erreurs API
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ description: 'Unknown error' }));
    // Le backend Flask utilise "description" pour les messages d'erreur
    const errorMessage = error.description || error.message || `HTTP error ${response.status}`;
    throw new Error(errorMessage);
  }
  return response.json();
}

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

export const noteService = {
  // Créer une nouvelle note
  async createNote(data: CreateNoteRequest): Promise<Note> {
    const response = await fetch(`${API_BASE}/notes`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse<Note>(response);
  },

  // Récupérer toutes les notes
  async getNotes(params?: {
    filter?: 'important' | 'unread' | 'received' | 'sent' | 'in_progress' | 'completed';
    sort?: 'date_asc' | 'date_desc' | 'important_first';
    sort_by?: string;
    sort_order?: 'asc' | 'desc';
    page?: number;
    per_page?: number;
    q?: string; // Recherche textuelle
    creator_id?: number; // Filtrer par créateur
  }): Promise<{
    notes: Note[];
    total: number;
    page: number;
    pages: number;
    has_next: boolean;
    has_prev: boolean;
  }> {
    const queryParams = new URLSearchParams();
    if (params?.filter) queryParams.append('filter', params.filter);
    if (params?.sort) queryParams.append('sort', params.sort);
    if (params?.sort_by) queryParams.append('sort_by', params.sort_by);
    if (params?.sort_order) queryParams.append('sort_order', params.sort_order);
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.per_page) queryParams.append('per_page', params.per_page.toString());
    if (params?.q) queryParams.append('q', params.q);
    if (params?.creator_id) queryParams.append('creator_id', params.creator_id.toString());

    const response = await fetch(
      `${API_BASE}/notes?${queryParams.toString()}`,
      { headers: getHeaders() }
    );
    return handleResponse(response);
  },

  // Récupérer une note par ID
  async getNote(id: number): Promise<Note> {
    const response = await fetch(`${API_BASE}/notes/${id}`, {
      headers: getHeaders(),
    });
    return handleResponse<Note>(response);
  },

  // Mettre à jour une note
  async updateNote(id: number, data: UpdateNoteRequest): Promise<Note> {
    const response = await fetch(`${API_BASE}/notes/${id}`, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse<Note>(response);
  },

  // Supprimer une note (soft delete)
  async deleteNote(id: number): Promise<Note> {
    const response = await fetch(`${API_BASE}/notes/${id}`, {
      method: 'DELETE',
      headers: getHeaders(),
    });
    return handleResponse<Note>(response);
  },
};
