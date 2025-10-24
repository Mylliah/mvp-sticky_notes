import { Assignment, CreateAssignmentRequest, UpdateAssignmentRequest } from '../types/assignment.types';

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

export const assignmentService = {
  // Créer une assignation (assigner une note à un contact)
  async createAssignment(data: CreateAssignmentRequest): Promise<Assignment> {
    console.log('[assignmentService] Creating assignment:', data);
    const response = await fetch(`${API_BASE}/assignments`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse<Assignment>(response);
  },

  // Récupérer toutes les assignations
  async getAssignments(params?: {
    note_id?: number;
    user_id?: number; // Backend utilise "user_id"
    assigner_id?: number;
    status?: string;
  }): Promise<Assignment[]> {
    const queryParams = new URLSearchParams();
    if (params?.note_id) queryParams.append('note_id', params.note_id.toString());
    if (params?.user_id) queryParams.append('user_id', params.user_id.toString());
    if (params?.assigner_id) queryParams.append('assigner_id', params.assigner_id.toString());
    if (params?.status) queryParams.append('status', params.status);

    const response = await fetch(
      `${API_BASE}/assignments?${queryParams.toString()}`,
      { headers: getHeaders() }
    );
    return handleResponse<Assignment[]>(response);
  },

  // Récupérer une assignation spécifique
  async getAssignment(id: number): Promise<Assignment> {
    const response = await fetch(`${API_BASE}/assignments/${id}`, {
      headers: getHeaders(),
    });
    return handleResponse<Assignment>(response);
  },

  // Mettre à jour une assignation
  async updateAssignment(id: number, data: UpdateAssignmentRequest): Promise<Assignment> {
    console.log('[assignmentService] Updating assignment:', id, data);
    const response = await fetch(`${API_BASE}/assignments/${id}`, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse<Assignment>(response);
  },

  // Supprimer une assignation (soft delete)
  async deleteAssignment(id: number): Promise<void> {
    console.log('[assignmentService] Deleting assignment:', id);
    const response = await fetch(`${API_BASE}/assignments/${id}`, {
      method: 'DELETE',
      headers: getHeaders(),
    });
    if (!response.ok) {
      throw new Error('Failed to delete assignment');
    }
  },
};
