export interface Contact {
  id: number;
  username: string;
  email: string;
  created_date: string;
}

export interface ContactRelationship {
  contact_id: number;
  contact: Contact;
  created_date: string;
}
