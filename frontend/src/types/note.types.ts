// Types pour les notes
export interface Note {
  id: number;
  content: string;
  important: boolean;
  creator_id: number;
  creator_username?: string; // Nom du créateur
  created_date: string;
  update_date: string | null;
  delete_date: string | null;
  deleted_by: number | null;
  deleted_by_username?: string; // Nom de celui qui a supprimé
}

export interface CreateNoteRequest {
  content: string;
  important?: boolean;
}

export interface UpdateNoteRequest {
  content?: string;
  important?: boolean;
}
