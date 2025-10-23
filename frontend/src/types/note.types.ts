// Types pour les notes
export interface Note {
  id: number;
  content: string;
  important: boolean;
  creator_id: number;
  created_date: string;
  update_date: string | null;
  delete_date: string | null;
}

export interface CreateNoteRequest {
  content: string;
  important?: boolean;
}

export interface UpdateNoteRequest {
  content?: string;
  important?: boolean;
}
