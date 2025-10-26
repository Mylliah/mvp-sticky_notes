import { useState, useEffect } from 'react';
import { contactService } from '../services/contact.service';
import { authService } from '../services/auth.service';
import { handleAuthError } from '../utils/auth-redirect';
import { ContactRelationship } from '../types/contact.types';
import './ContactBadges.css';

interface ContactBadgesProps {
  onDrop?: (noteId: number, contactId: number) => void;
  refreshTrigger?: number; // Incrémenter ce nombre force un rechargement
  onContactClick?: (contactId: number) => void; // Nouveau callback pour filtrer par contact
  selectedContactId?: number | null; // ID du contact sélectionné pour l'effet visuel
  isOpen?: boolean; // État ouvert/fermé de la sidebar
  onToggle?: () => void; // Callback pour toggle
}

export default function ContactBadges({ onDrop, refreshTrigger = 0, onContactClick, selectedContactId, isOpen = true, onToggle }: ContactBadgesProps) {
  const [contacts, setContacts] = useState<ContactRelationship[]>([]);
  const [currentUser, setCurrentUser] = useState<{ id: number; username: string } | null>(null);
  const [dragOverContactId, setDragOverContactId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadContactsAndCurrentUser();
  }, [refreshTrigger]); // Recharger quand refreshTrigger change

  const loadContactsAndCurrentUser = async () => {
    try {
      setLoading(true);

      const user = authService.getCurrentUser();
      if (!user) {
        console.warn('No user found in ContactBadges');
        setCurrentUser(null);
        setLoading(false);
        return;
      }
      setCurrentUser(user);

      try {
        const contactsList = await contactService.getContacts();
        console.log('[ContactBadges] Contacts loaded:', contactsList);
        setContacts(contactsList || []);
      } catch (contactErr) {
        console.error('[ContactBadges] Error loading contacts:', contactErr);
        
        // Gérer les erreurs d'authentification
        if (handleAuthError(contactErr)) {
          return; // Redirection en cours
        }
        
        setContacts([]);
      }
    } catch (err) {
      console.error('Error loading contacts:', err);
      setContacts([]);
    } finally {
      setLoading(false);
    }
  };

  const handleDragOver = (e: React.DragEvent, contactId: number) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    setDragOverContactId(contactId);
  };

  const handleDragLeave = () => {
    setDragOverContactId(null);
  };

  const handleDrop = (e: React.DragEvent, contactId: number) => {
    e.preventDefault();
    setDragOverContactId(null);

    const noteId = e.dataTransfer.getData('text/plain');
    if (noteId && onDrop) {
      onDrop(parseInt(noteId, 10), contactId);
    }
  };

  const getInitials = (name: string): string => {
    return name
      .split(' ')
      .map(word => word[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const getAvatarColor = (index: number): string => {
    const colors = [
      'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
      'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
      'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
      'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
      'linear-gradient(135deg, #30cfd0 0%, #330867 100%)',
      'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
      'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)',
    ];
    return colors[index % colors.length];
  };

  if (loading) {
    return (
      <div className="contact-badges-container">
        <div className="contact-badges-header">
          <h3>Contacts</h3>
        </div>
        <div className="contact-badges">
          <p style={{ color: '#999', fontSize: '13px' }}>Chargement...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`contact-badges-container ${isOpen ? 'open' : 'closed'}`}>
      <div className="contact-badges-header">
        <h3>👥 Contacts</h3>
        {onToggle && (
          <button className="toggle-btn" onClick={onToggle} title={isOpen ? "Réduire" : "Afficher"}>
            {isOpen ? '→' : '←'}
          </button>
        )}
      </div>
      <div className="contact-badges">
        {/* Badge "Moi" */}
        {currentUser && (
          <div
            className={`contact-badge me ${dragOverContactId === currentUser.id ? 'drag-over' : ''} ${selectedContactId === currentUser.id ? 'selected' : ''}`}
            onDragOver={(e) => handleDragOver(e, currentUser.id)}
            onDragLeave={handleDragLeave}
            onDrop={(e) => handleDrop(e, currentUser.id)}
            onClick={() => onContactClick && onContactClick(currentUser.id)}
            style={{ cursor: onContactClick ? 'pointer' : 'default' }}
            title="Voir toutes mes notes"
          >
            <div className="contact-avatar" style={{ background: '#f5576c' }}>
              {getInitials(currentUser.username)}
            </div>
            <span className="contact-name">Moi</span>
          </div>
        )}

        {/* Badges des contacts */}
        {contacts
          .filter((contact) => !contact.is_self) // Exclure "Moi" qui est déjà affiché
          .map((contact, index) => (
            <div
              key={contact.contact_user_id}
              className={`contact-badge ${dragOverContactId === contact.contact_user_id ? 'drag-over' : ''} ${selectedContactId === contact.contact_user_id ? 'selected' : ''}`}
              onDragOver={(e) => handleDragOver(e, contact.contact_user_id)}
              onDragLeave={handleDragLeave}
              onDrop={(e) => handleDrop(e, contact.contact_user_id)}
              onClick={() => onContactClick && onContactClick(contact.contact_user_id)}
              style={{ cursor: onContactClick ? 'pointer' : 'default' }}
              title={`Voir toutes les notes avec ${contact.nickname || contact.username}`}
            >
              <div 
                className="contact-avatar"
                style={{ background: getAvatarColor(index) }}
              >
                {getInitials(contact.username)}
              </div>
              <span className="contact-name">{contact.nickname || contact.username}</span>
            </div>
          ))}
      </div>
    </div>
  );
}
