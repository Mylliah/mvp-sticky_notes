export interface Contact {
  id: number;
  username: string;
  email: string;
  created_date: string;
}

export interface ContactRelationship {
  id: number;
  user_id: number;
  contact_user_id: number;
  username: string;
  email: string;
  nickname: string;
  is_self: boolean;
  is_mutual?: boolean;
  contact_action: string | null;
  created_date: string | null;
}
