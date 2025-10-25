import { useState, useEffect } from 'react';
import { contactService } from '../services/contact.service';
import { authService } from '../services/auth.service';
import { handleAuthError } from '../utils/auth-redirect';
import { Contact, ContactRelationship } from '../types/contact.types';
import './ContactTabs.css';

interface ContactTabsProps {
  selectedContactId: number | null;
  onSelectContact: (contactId: number | null) => void;
}

export function ContactTabs({ selectedContactId, onSelectContact }: ContactTabsProps) {
  const [contacts, setContacts] = useState<ContactRelationship[]>([]);
  const [currentUser, setCurrentUser] = useState<{ id: number; username: string } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadContactsAndCurrentUser();
  }, []);

  const loadContactsAndCurrentUser = async () => {
    try {
      setLoading(true);
      setError(null);

      const user = authService.getCurrentUser();
      if (!user) {
        console.warn('No user found in ContactTabs');
        setCurrentUser(null);
        setLoading(false);
        return;
      }
      setCurrentUser(user);

      try {
        const contactsList = await contactService.getContacts();
        setContacts(contactsList || []);
      } catch (contactErr) {
        // Si l'appel API échoue, gérer l'erreur d'authentification
        console.error('Error loading contacts:', contactErr);
        
        if (handleAuthError(contactErr)) {
          return; // Redirection en cours
        }
        
        setContacts([]);
      }
    } catch (err) {
      console.error('Error loading contacts:', err);
      setError(err instanceof Error ? err.message : 'Failed to load contacts');
      setContacts([]);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="contact-tabs-loading">Chargement des contacts...</div>;
  }

  // Ne pas bloquer l'interface en cas d'erreur, juste afficher les onglets de base
  return (
    <div className="contact-tabs">
      {/* Onglet "Moi" */}
      {currentUser && (
        <button
          className={`contact-tab ${selectedContactId === currentUser.id ? 'active' : ''}`}
          onClick={() => onSelectContact(currentUser.id)}
        >
          <span className="contact-icon">👤</span>
          Moi
        </button>
      )}

      {/* Onglet "Tous" */}
      <button
        className={`contact-tab ${selectedContactId === null ? 'active' : ''}`}
        onClick={() => onSelectContact(null)}
      >
        <span className="contact-icon">👥</span>
        Tous
      </button>

      {/* Onglets pour chaque contact */}
      {contacts
        .filter((relationship) => relationship.contact)  // Filtrer les contacts undefined
        .map((relationship) => (
          <button
            key={relationship.contact_id}
            className={`contact-tab ${selectedContactId === relationship.contact_id ? 'active' : ''}`}
            onClick={() => onSelectContact(relationship.contact_id)}
          >
            <span className="contact-icon">👤</span>
            {relationship.contact.username}
          </button>
        ))}
    </div>
  );
}
