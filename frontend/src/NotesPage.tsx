import { useState, useEffect } from 'react';
import FilterBar, { FilterType, SortOrder } from './components/FilterBar';
import NoteCard from './components/NoteCard';
import NoteEditor from './components/NoteEditor';
import ContactBadges from './components/ContactBadges';
import ContactsManager from './components/ContactsManager';
import Sidebar from './components/Sidebar';
import ToastContainer, { useToast } from './components/ToastContainer';
import { Note } from './types/note.types';
import { Assignment } from './types/assignment.types';
import { noteService } from './services/note.service';
import { authService } from './services/auth.service';
import { assignmentService } from './services/assignment.service';
import { contactService } from './services/contact.service';
import { handleAuthError } from './utils/auth-redirect';
import './NotesPage.css';

interface NotesPageProps {
  onLogout?: () => void;
}

export default function NotesPage({ onLogout }: NotesPageProps) {
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showEditor, setShowEditor] = useState(false);
  const [selectedNote, setSelectedNote] = useState<Note | null>(null);
  const [showContactsManager, setShowContactsManager] = useState(false);
  const [contactsRefreshTrigger, setContactsRefreshTrigger] = useState(0);
  
  // Filtres
  const [activeFilter, setActiveFilter] = useState<FilterType>('all');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const [searchQuery, setSearchQuery] = useState('');
  const [showArchive, setShowArchive] = useState(false); // Vue Archive
  
  // Filtre par contact
  const [selectedContactId, setSelectedContactId] = useState<number | null>(null);

  // Drag & Drop
  const [draggedNote, setDraggedNote] = useState<Note | null>(null);

  // Toast notifications
  const { addToast } = useToast();
  const [lastAssignmentId, setLastAssignmentId] = useState<number | null>(null);

  // Contacts pour récupérer les noms
  const [contactsMap, setContactsMap] = useState<Map<number, string>>(new Map());
  
  // Liste des contacts pour le menu d'assignation
  const [contactsList, setContactsList] = useState<Array<{ id: number; nickname: string }>>([]);

  // Map des assignations par note_id pour accès rapide
  const [assignmentsMap, setAssignmentsMap] = useState<Map<number, Assignment[]>>(new Map());

  // Charger les notes
  const loadNotes = async () => {
    console.log('[NotesPage] Loading notes with filters:', { 
      activeFilter, 
      sortOrder, 
      searchQuery, 
      selectedContactId,
      showArchive
    });
    
    setLoading(true);
    setError(null);
    
    try {
      // Si on est en vue Archive, appeler la route spécifique
      if (showArchive) {
        const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/v1/notes/orphans`, {
          headers: {
            'Authorization': `Bearer ${authService.getToken()}`,
          },
        });
        
        if (!response.ok) {
          throw new Error('Failed to load orphan notes');
        }
        
        const data = await response.json();
        console.log('[NotesPage] Orphan notes loaded:', data.count);
        setNotes(data.notes || []);
        setLoading(false);
        return;
      }
      
      const params: any = {
        sort_by: 'created_date',
        sort_order: sortOrder,
      };

      // Appliquer les filtres
      if (activeFilter !== 'all') {
        if (activeFilter === 'important') {
          params.filter = 'important';
        } else if (activeFilter === 'received') {
          params.filter = 'received';
        } else if (activeFilter === 'sent') {
          params.filter = 'sent';
        } else if (activeFilter === 'in_progress') {
          params.filter = 'in_progress';
        } else if (activeFilter === 'done') {
          params.filter = 'completed'; // Backend utilise "completed"
        }
      }

      if (searchQuery) {
        params.q = searchQuery;
      }

      // Ne pas filtrer par creator_id si on filtre par contact
      // On va filtrer côté client après avoir chargé les assignations
      
      const data = await noteService.getNotes(params);
      console.log('[NotesPage] Notes loaded:', data.notes?.length || 0);
      
      let notesToDisplay = data.notes || [];

      // Charger toutes les assignations pour les notes chargées
      if (notesToDisplay && notesToDisplay.length > 0) {
        const loadedAssignmentsMap = await loadAssignments(notesToDisplay);
        
        // Filtrer par contact sélectionné APRÈS avoir chargé les assignations
        if (selectedContactId !== null && loadedAssignmentsMap) {
          const currentUserId = authService.getCurrentUser()?.id;
          
          notesToDisplay = notesToDisplay.filter((note: Note) => {
            // Vérifier si la note est créée par le contact
            if (note.creator_id === selectedContactId) {
              return true;
            }
            
            // Vérifier si la note est créée par moi et assignée au contact
            if (note.creator_id === currentUserId) {
              const noteAssignments = loadedAssignmentsMap.get(note.id) || [];
              return noteAssignments.some(
                (assignment: Assignment) => assignment.user_id === selectedContactId
              );
            }
            
            return false;
          });
          console.log('[NotesPage] Filtered by contact:', selectedContactId, '→', notesToDisplay.length, 'notes');
        }
      }
      
      setNotes(notesToDisplay);
    } catch (err) {
      console.error('[NotesPage] Error loading notes:', err);
      
      // Gérer les erreurs d'authentification
      if (handleAuthError(err)) {
        return; // Redirection en cours
      }
      
      const errorMessage = err instanceof Error ? err.message : 'Erreur de chargement';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Charger les assignations pour toutes les notes
  const loadAssignments = async (notesToLoad: Note[]) => {
    try {
      const currentUser = authService.getCurrentUser();
      if (!currentUser) return new Map<number, Assignment[]>();

      console.log('[NotesPage] Loading assignments for', notesToLoad.length, 'notes');
      
      // Créer une map pour stocker les assignations par note_id
      const newAssignmentsMap = new Map<number, Assignment[]>();

      // Charger les assignations pour chaque note en parallèle
      await Promise.all(
        notesToLoad.map(async (note) => {
          try {
            const assignments = await assignmentService.getAssignments({ note_id: note.id });
            newAssignmentsMap.set(note.id, assignments);
          } catch (err) {
            console.error(`[NotesPage] Error loading assignments for note ${note.id}:`, err);
            newAssignmentsMap.set(note.id, []);
          }
        })
      );

      setAssignmentsMap(newAssignmentsMap);
      console.log('[NotesPage] Assignments loaded for', newAssignmentsMap.size, 'notes');
      return newAssignmentsMap;
    } catch (err) {
      console.error('[NotesPage] Error in loadAssignments:', err);
    }
  };

  // Charger les contacts au montage pour créer une map des noms
  useEffect(() => {
    const loadContacts = async () => {
      try {
        const contacts = await contactService.getContacts();
        console.log('[NotesPage] Total contacts loaded:', contacts.length);
        const map = new Map<number, string>();
        const list: Array<{ id: number; nickname: string }> = [];
        
        contacts.forEach(contact => {
          console.log('[NotesPage] Contact:', contact.nickname || contact.username, 'is_self:', contact.is_self);
          // Inclure TOUS les contacts, y compris "Moi" pour permettre l'auto-assignation
          map.set(contact.contact_user_id, contact.nickname || contact.username);
          list.push({
            id: contact.contact_user_id,
            nickname: contact.nickname || contact.username
          });
        });
        
        console.log('[NotesPage] Contacts list for assignment menu:', list.length, 'contacts');
        setContactsMap(map);
        setContactsList(list);
      } catch (err) {
        console.error('[NotesPage] Error loading contacts:', err);
      }
    };
    loadContacts();
  }, []);

  // Charger les notes au montage et quand les filtres changent
  useEffect(() => {
    loadNotes();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeFilter, sortOrder, searchQuery, selectedContactId, showArchive]);

  const handleNoteCreated = async (savedNote: Note, isNew: boolean) => {
    setShowEditor(false);
    
    if (isNew) {
      // Nouvelle note : l'ajouter en tête de liste
      console.log('[NotesPage] Nouvelle note créée:', savedNote);
      setNotes((prevNotes: Note[]) => [savedNote, ...prevNotes]);
      
      // Charger ses assignations (vide au départ normalement)
      const assignments = await assignmentService.getAssignments({ note_id: savedNote.id });
      setAssignmentsMap((prev: Map<number, Assignment[]>) => {
        const newMap = new Map(prev);
        newMap.set(savedNote.id, assignments);
        return newMap;
      });
    } else {
      // Note modifiée : mettre à jour dans la liste
      console.log('[NotesPage] Note modifiée:', savedNote);
      setNotes((prevNotes: Note[]) => 
        prevNotes.map((n: Note) => (n.id === savedNote.id ? savedNote : n))
      );
      // Les assignations n'ont pas changé, pas besoin de les recharger
    }
  };

  const handleNoteDeleted = () => {
    setShowEditor(false);
    loadNotes();
  };

  // Recharger uniquement les assignations d'une note spécifique (sans tout recharger)
  const refreshNoteAssignments = async (noteId: number) => {
    try {
      console.log('[NotesPage] Refreshing assignments for note', noteId);
      const assignments = await assignmentService.getAssignments({ note_id: noteId });
      
      // Mettre à jour seulement cette note dans la map
      setAssignmentsMap((prev: Map<number, Assignment[]>) => {
        const newMap = new Map(prev);
        newMap.set(noteId, assignments);
        return newMap;
      });
      
      console.log('[NotesPage] Assignments refreshed for note', noteId);
    } catch (err) {
      console.error('[NotesPage] Error refreshing assignments:', err);
    }
  };

  const handleEditNote = (note: Note) => {
    setSelectedNote(note);
    setShowEditor(true);
  };

  const handleDeleteNote = async (noteId: number) => {
    const currentUserId = authService.getCurrentUser()?.id;
    if (!currentUserId) return;
    
    const note = notes.find(n => n.id === noteId);
    if (!note) return;
    
    const isCreator = note.creator_id === currentUserId;
    const assignments = assignmentsMap.get(noteId) || [];
    const myAssignment = assignments.find(a => a.user_id === currentUserId);
    
    // Si l'utilisateur a une assignation, on la supprime (créateur ou destinataire)
    if (myAssignment) {
      const message = isCreator
        ? 'Êtes-vous sûr de vouloir retirer cette note de votre liste ? Elle restera visible pour les destinataires.'
        : 'Êtes-vous sûr de vouloir retirer cette note de votre liste ?';
      
      if (!window.confirm(message)) return;
      
      try {
        await assignmentService.deleteAssignment(myAssignment.id);
        loadNotes();
      } catch (err) {
        alert('Erreur lors de la suppression de l\'assignation');
      }
    } else if (isCreator) {
      // Si le créateur n'a pas d'assignation (rare), on peut supprimer la note complètement
      if (!window.confirm('Êtes-vous sûr de vouloir supprimer définitivement cette note ? Elle sera supprimée pour tous les destinataires.')) {
        return;
      }
      
      try {
        await noteService.deleteNote(noteId);
        loadNotes();
      } catch (err) {
        alert('Erreur lors de la suppression');
      }
    }
  };

  // Gérer le drop d'une note sur un contact
  const handleNoteDrop = async (noteId: number, contactId: number) => {
    try {
      console.log('[NotesPage] Assigning note', noteId, 'to contact', contactId);
      
      // Créer l'assignation
      const assignment = await assignmentService.createAssignment({
        note_id: noteId,
        user_id: contactId, // Backend attend "user_id"
      });

      setLastAssignmentId(assignment.id);

      // Trouver le nom du contact
      const currentUser = authService.getCurrentUser();
      let contactName = 'contact';
      
      if (currentUser && contactId === currentUser.id) {
        contactName = 'vous-même';
      } else {
        // Récupérer le nom depuis la map des contacts
        contactName = contactsMap.get(contactId) || `contact #${contactId}`;
      }

      // Afficher un toast de confirmation avec bouton Annuler
      addToast({
        message: `Note assignée à ${contactName} ✓`,
        type: 'success',
        duration: 5000,
        actions: [
          {
            label: 'Annuler',
            onClick: async () => {
              try {
                await assignmentService.deleteAssignment(assignment.id);
                addToast({
                  message: 'Attribution annulée',
                  type: 'info',
                  duration: 3000,
                });
                loadNotes();
              } catch (err) {
                addToast({
                  message: 'Erreur lors de l\'annulation',
                  type: 'error',
                  duration: 3000,
                });
              }
            },
          },
        ],
      });

      // Recharger les notes pour mettre à jour l'affichage
      loadNotes();
    } catch (err) {
      console.error('[NotesPage] Error assigning note:', err);
      addToast({
        message: err instanceof Error ? err.message : 'Erreur lors de l\'assignation',
        type: 'error',
        duration: 5000,
      });
    }
  };

  const currentUser = authService.getCurrentUser();

  const handleShowAllNotes = () => {
    setActiveFilter('all');
    setSearchQuery('');
    setSelectedContactId(null);
    setShowArchive(false);
  };

  const handleFilterChange = (filter: FilterType) => {
    setActiveFilter(filter);
    setShowArchive(false); // Réinitialiser l'archive quand on change de filtre
  };

  const handleContactClick = (contactId: number) => {
    console.log('[NotesPage] Filtering by contact:', contactId);
    setSelectedContactId(contactId);
    setActiveFilter('all'); // Reset autres filtres
    setSearchQuery('');
    
    addToast({
      message: `Affichage des notes avec ce contact`,
      type: 'info',
      duration: 3000,
    });
  };

  // Obtenir le titre de la page en fonction du contact sélectionné
  const getPageTitle = () => {
    if (showArchive) {
      return 'Archives - Sans assignation';
    }
    
    if (selectedContactId === null) {
      return 'Mes Notes';
    }
    
    // Si c'est l'utilisateur lui-même
    if (currentUser && selectedContactId === currentUser.id) {
      return 'Mes Notes';
    }
    
    // Chercher le contact dans la liste
    const contact = contactsList.find(c => c.id === selectedContactId);
    if (contact) {
      return `Notes avec ${contact.nickname}`;
    }
    
    return 'Mes Notes';
  };

  return (
    <div className="notes-page">
      {/* Sidebar gauche */}
      <Sidebar 
        onNewNote={() => {
          setSelectedNote(null);
          setShowEditor(true);
        }}
        onShowAllNotes={handleShowAllNotes}
        onManageContacts={() => setShowContactsManager(true)}
        onShowArchive={() => {
          setShowArchive(true);
          setActiveFilter('all');
          setSearchQuery('');
          setSelectedContactId(null);
        }}
        activeView={showArchive ? 'archive' : (activeFilter === 'all' && !searchQuery ? 'all' : 'filtered')}
      />

      <div className="main-content">
        <header className="notes-header">
          <div className="header-left">
            <h1>{getPageTitle()}</h1>
            {currentUser && <span className="user-name">Bonjour, {currentUser.username} !</span>}
          </div>
          <div className="header-right">
            {onLogout && (
              <button className="logout-btn" onClick={onLogout}>
                🚪 Déconnexion
              </button>
            )}
          </div>
        </header>

      {/* Barre de filtres */}
      <FilterBar
        onFilterChange={handleFilterChange}
        onSortChange={setSortOrder}
        onSearchChange={setSearchQuery}
        activeFilter={activeFilter}
      />

      {/* Zone de contenu */}
      <div className="notes-content">
        {loading && <div className="loading">Chargement...</div>}
        
        {error && (
          <div className="error-banner">
            {error}
          </div>
        )}

        {!loading && notes.length === 0 && (
          <div className="empty-state">
            Aucune note trouvée. Créez votre première note !
          </div>
        )}

        {!loading && notes.length > 0 && (
          <div className="notes-grid">
            {notes.map((note) => (
              <NoteCard
                key={note.id}
                note={note}
                onEdit={handleEditNote}
                onClick={handleEditNote}
                onDelete={handleDeleteNote}
                onDragStart={setDraggedNote}
                onDragEnd={() => setDraggedNote(null)}
                assignments={assignmentsMap.get(note.id) || []}
                onAssign={handleNoteDrop}
                contacts={contactsList}
                isOrphan={(note as any).is_orphan || false}
              />
            ))}
          </div>
        )}
      </div>

      {/* Badges de contacts à droite */}
      <ContactBadges 
        onDrop={handleNoteDrop}
        refreshTrigger={contactsRefreshTrigger}
        onContactClick={handleContactClick}
        selectedContactId={selectedContactId}
      />

      {/* Toast Container */}
      <ToastContainer />

      {/* Modal d'édition */}
      {showEditor && (
        <NoteEditor
          note={selectedNote}
          onNoteCreated={handleNoteCreated}
          onNoteDeleted={handleNoteDeleted}
          onClose={() => {
            setShowEditor(false);
            // Si on a édité une note existante, rafraîchir seulement ses assignations
            // Si c'est une nouvelle note, on recharge tout (géré par onNoteCreated)
            if (selectedNote) {
              refreshNoteAssignments(selectedNote.id);
            }
          }}
        />
      )}

      {/* Modal de gestion des contacts */}
      {showContactsManager && (
        <ContactsManager
          onClose={() => setShowContactsManager(false)}
          onContactsChanged={() => {
            // Ne PAS recharger les notes, juste forcer le rechargement des ContactBadges
            setContactsRefreshTrigger(prev => prev + 1);
          }}
        />
      )}
      </div> {/* Fermeture de main-content */}
    </div>
  );
}
