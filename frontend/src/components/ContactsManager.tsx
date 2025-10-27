import { useState, useEffect } from 'react';
import { contactService } from '../services/contact.service';
import { userService } from '../services/user.service';
import { authService } from '../services/auth.service';
import { Contact } from '../types/contact.types';
import { User } from '../types/auth.types';
import './ContactsManager.css';

interface ContactsManagerProps {
  onClose: () => void;
  onContactsChanged?: () => void;
}

export default function ContactsManager({ onClose, onContactsChanged }: ContactsManagerProps) {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // État pour l'ajout de contact
  const [showAddForm, setShowAddForm] = useState(false);
  const [searchUsername, setSearchUsername] = useState('');
  const [searchResults, setSearchResults] = useState<User[]>([]);
  const [newContactNickname, setNewContactNickname] = useState('');
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  
  // État pour l'édition
  const [editingContact, setEditingContact] = useState<Contact | null>(null);
  const [editNickname, setEditNickname] = useState('');

  // Charger les contacts au montage
  useEffect(() => {
    // Vérifier si l'utilisateur est connecté
    if (!authService.isAuthenticated()) {
      setError('Veuillez vous reconnecter');
      return;
    }
    loadContacts();
  }, []);

  const loadContacts = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await contactService.getContacts();
      // Filtrer "Moi" (is_self: true)
      const realContacts = data.filter(c => !c.is_self);
      setContacts(realContacts);
    } catch (err) {
      console.error('Erreur lors du chargement des contacts:', err);
      // Ne pas afficher l'erreur si c'est juste qu'il n'y a pas de contacts
      const errorMessage = err instanceof Error ? err.message : 'Erreur de chargement';
      if (!errorMessage.includes('401') && !errorMessage.includes('Unauthorized')) {
        setError(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSearchUsers = async () => {
    if (!searchUsername.trim()) {
      setError('Veuillez entrer un nom d\'utilisateur');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const users = await userService.searchUsers(searchUsername);
      setSearchResults(users);
      
      if (users.length === 0) {
        setError('Aucun utilisateur trouvé');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur de recherche');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectUser = (user: User) => {
    setSelectedUser(user);
    setNewContactNickname(user.username); // Par défaut, utiliser le username
    setSearchResults([]);
  };

  const handleAddContact = async () => {
    if (!selectedUser || !newContactNickname.trim()) {
      setError('Veuillez sélectionner un utilisateur et entrer un surnom');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);
    
    try {
      await contactService.createContact({
        contact_username: selectedUser.username,
        nickname: newContactNickname.trim(),
      });
      
      setSuccess(`Contact "${newContactNickname}" ajouté avec succès !`);
      setShowAddForm(false);
      setSearchUsername('');
      setSelectedUser(null);
      setNewContactNickname('');
      
      await loadContacts();
      
      if (onContactsChanged) {
        onContactsChanged();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de l\'ajout');
    } finally {
      setLoading(false);
    }
  };

  const handleEditContact = (contact: Contact) => {
    setEditingContact(contact);
    setEditNickname(contact.nickname);
  };

  const handleSaveEdit = async (e?: React.MouseEvent) => {
    // Empêcher la propagation du clic
    if (e) {
      e.stopPropagation();
      e.preventDefault();
    }

    if (!editingContact || !editNickname.trim()) {
      setError('Veuillez entrer un surnom');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);
    
    try {
      await contactService.updateContact(editingContact.id, {
        nickname: editNickname.trim(),
      });
      
      setSuccess(`Contact modifié avec succès !`);
      setEditingContact(null);
      
      await loadContacts();
      
      if (onContactsChanged) {
        onContactsChanged();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de la modification');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteContact = async (contact: Contact) => {
    if (!window.confirm(`Êtes-vous sûr de vouloir supprimer le contact "${contact.nickname}" ?`)) {
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);
    
    try {
      await contactService.deleteContact(contact.id);
      
      setSuccess(`Contact "${contact.nickname}" supprimé avec succès !`);
      
      await loadContacts();
      
      if (onContactsChanged) {
        onContactsChanged();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de la suppression');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="contacts-manager-overlay">
      <div className="contacts-manager-modal">
        {/* En-tête */}
        <div className="contacts-manager-header">
          <h2>📇 Gestion des contacts</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        {/* Contenu avec padding */}
        <div className="contacts-manager-content">
          {/* Messages */}
          {error && <div className="error-message">{error}</div>}
          {success && <div className="success-message">{success}</div>}

        {/* Bouton ajouter */}
        {!showAddForm && (
          <button 
            className="add-contact-btn"
            onClick={() => setShowAddForm(true)}
          >
            ➕ Ajouter un contact
          </button>
        )}

        {/* Formulaire d'ajout */}
        {showAddForm && (
          <div className="add-contact-form">
            <h3>Ajouter un nouveau contact</h3>
            
            {!selectedUser ? (
              <>
                <div className="search-user-section">
                  <input
                    type="text"
                    className="search-input"
                    placeholder="Nom d'utilisateur..."
                    value={searchUsername}
                    onChange={(e) => setSearchUsername(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSearchUsers()}
                  />
                  <button 
                    className="search-btn"
                    onClick={handleSearchUsers}
                    disabled={loading}
                  >
                    🔍 Rechercher
                  </button>
                </div>

                {searchResults.length > 0 && (
                  <div className="search-results">
                    {searchResults.map(user => (
                      <div 
                        key={user.id} 
                        className="search-result-item"
                        onClick={() => handleSelectUser(user)}
                      >
                        <span className="user-username">{user.username}</span>
                        <span className="user-email">{user.email}</span>
                      </div>
                    ))}
                  </div>
                )}
              </>
            ) : (
              <>
                <div className="selected-user">
                  <strong>Utilisateur sélectionné :</strong> {selectedUser.username}
                  <button 
                    className="cancel-selection-btn"
                    onClick={() => {
                      setSelectedUser(null);
                      setNewContactNickname('');
                    }}
                  >
                    ↩️ Changer
                  </button>
                </div>

                <div className="nickname-section">
                  <label htmlFor="nickname">Surnom :</label>
                  <input
                    id="nickname"
                    type="text"
                    className="nickname-input"
                    placeholder="Surnom pour ce contact..."
                    value={newContactNickname}
                    onChange={(e) => setNewContactNickname(e.target.value)}
                  />
                </div>

                <div className="form-actions">
                  <button 
                    className="save-btn"
                    onClick={handleAddContact}
                    disabled={loading || !newContactNickname.trim()}
                  >
                    💾 Ajouter
                  </button>
                  <button 
                    className="cancel-btn"
                    onClick={() => {
                      setShowAddForm(false);
                      setSelectedUser(null);
                      setSearchUsername('');
                      setNewContactNickname('');
                      setSearchResults([]);
                    }}
                  >
                    ✕ Annuler
                  </button>
                </div>
              </>
            )}
          </div>
        )}

        {/* Liste des contacts */}
        <div className="contacts-list">
          <h3>Mes contacts ({contacts.length})</h3>
          
          {loading && <div className="loading">Chargement...</div>}
          
          {!loading && contacts.length === 0 && (
            <div className="empty-state">
              Aucun contact. Ajoutez votre premier contact !
            </div>
          )}

          {!loading && contacts.length > 0 && (
            <div className="contacts-grid">
              {contacts.map(contact => (
                <div key={contact.id} className="contact-item">
                  {editingContact?.id === contact.id ? (
                    // Mode édition
                    <div className="edit-contact-form">
                      <input
                        type="text"
                        className="edit-nickname-input"
                        value={editNickname}
                        onChange={(e) => setEditNickname(e.target.value)}
                        autoFocus
                      />
                      <div className="edit-actions">
                        <button 
                          className="save-edit-btn"
                          onClick={(e) => handleSaveEdit(e)}
                          disabled={loading}
                        >
                          ✓
                        </button>
                        <button 
                          className="cancel-edit-btn"
                          onClick={(e) => {
                            e.stopPropagation();
                            setEditingContact(null);
                          }}
                        >
                          ✕
                        </button>
                      </div>
                    </div>
                  ) : (
                    // Mode affichage
                    <>
                      <div className="contact-info">
                        <div className="contact-nickname">{contact.nickname}</div>
                        <div className="contact-username">@{contact.username}</div>
                        {contact.is_mutual && (
                          <div className="mutual-badge" title="Contact mutuel">
                            ✓ Mutuel
                          </div>
                        )}
                        {!contact.is_mutual && (
                          <div className="pending-badge" title="En attente de confirmation">
                            ⏳ En attente
                          </div>
                        )}
                      </div>
                      <div className="contact-actions">
                        <button 
                          className="edit-contact-btn"
                          onClick={() => handleEditContact(contact)}
                          title="Modifier"
                        >
                          ✏️
                        </button>
                        <button 
                          className="delete-contact-btn"
                          onClick={() => handleDeleteContact(contact)}
                          title="Supprimer"
                        >
                          🗑️
                        </button>
                      </div>
                    </>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
        {/* Fin du contenu avec padding */}
        </div>
        {/* Fin du modal */}
      </div>
      {/* Fin de l'overlay */}
    </div>
  );
}
