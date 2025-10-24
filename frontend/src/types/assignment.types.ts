export interface Assignment {
  id: number;
  note_id: number;
  user_id: number; // ID du destinataire
  assigned_date: string;
  is_read: boolean;
  read_date: string | null;
  recipient_priority: boolean;
  recipient_status: 'en_cours' | 'terminé'; // Statut côté destinataire
  finished_date: string | null;
}

export interface CreateAssignmentRequest {
  note_id: number;
  user_id: number; // Backend attend "user_id"
  is_read?: boolean;
}

export interface UpdateAssignmentRequest {
  user_id?: number;
  is_read?: boolean;
}
