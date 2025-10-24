export interface Assignment {
  id: number;
  note_id: number;
  assigner_id: number;
  user_id: number; // Backend utilise "user_id" pour l'assignee
  status: 'pending' | 'in_progress' | 'completed';
  assigned_date: string;
  read_date: string | null;
  is_deleted: boolean;
  deleted_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateAssignmentRequest {
  note_id: number;
  user_id: number; // Backend attend "user_id" et non "assignee_id"
  status?: 'pending' | 'in_progress' | 'completed';
}

export interface UpdateAssignmentRequest {
  status?: 'pending' | 'in_progress' | 'completed';
  read_date?: string;
}
