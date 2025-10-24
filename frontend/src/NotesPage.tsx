import { useState, useEffect } from 'react';
import FilterBar, { FilterType, SortOrder } from './components/FilterBar';
import NoteCard from './components/NoteCard';
import NoteEditor from './components/NoteEditor';
import ContactBadges from './components/ContactBadges';
import Sidebar from './components/Sidebar';
import ToastContainer, { useToast } from './components/ToastContainer';
import { Note } from './types/note.types';
import { noteService } from './services/note.service';
import { authService } from './services/auth.service';
import { assignmentService } from './services/assignment.service';
import { contactService } from './services/contact.service';
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
  
  // Filtres
  const [activeFilter, setActiveFilter] = useState<FilterType>('all');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const [searchQuery, setSearchQuery] = useState('');
  
  // Filtre par contact
  const [selectedContactId, setSelectedContactId] = useState<number | null>(null);

  // Drag & Drop
  const [draggedNote, setDraggedNote] = useState<Note | null>(null);

  // Toast notifications
  const { addToast } = useToast();
  const [lastAssignmentId, setLastAssignmentId] = useState<number | null>(null);

  // Contacts pour récupérer les noms
  const [contactsMap, setContactsMap] = useState<Map<number, string>>(new Map());

  // Charger les notes
  const loadNotes = async () => {
    console.log('[NotesPage] Loading notes with filters:', { 
      activeFilter, 
      sortOrder, 
      searchQuery, 
      selectedContactId 
    });
    
    setLoading(true);
    setError(null);
    
    try {
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

      // Filtrer par contact sélectionné
      if (selectedContactId !== null) {
        params.creator_id = selectedContactId;
      }

      const data = await noteService.getNotes(params);
      console.log('[NotesPage] Notes loaded:', data.notes?.length || 0);
      setNotes(data.notes || []);
    } catch (err) {
      console.error('[NotesPage] Error loading notes:', err);
      const errorMessage = err instanceof Error ? err.message : 'Erreur de chargement';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Charger les contacts au montage pour créer une map des noms
  useEffect(() => {
    const loadContacts = async () => {
      try {
        const contacts = await contactService.getContacts();
        const map = new Map<number, string>();
        contacts.forEach(contact => {
          map.set(contact.contact_user_id, contact.nickname || contact.username);
        });
        setContactsMap(map);
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
  }, [activeFilter, sortOrder, searchQuery, selectedContactId]);

  const handleNoteCreated = () => {
    setShowEditor(false);
    loadNotes();
  };

  const handleNoteDeleted = () => {
    setShowEditor(false);
    loadNotes();
  };

  const handleEditNote = (note: Note) => {
    setSelectedNote(note);
    setShowEditor(true);
  };

  const handleDeleteNote = async (noteId: number) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer cette note ?')) {
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
        activeView={activeFilter === 'all' && !searchQuery ? 'all' : 'filtered'}
      />

      <div className="main-content">
        <header className="notes-header">
          <div className="header-left">
            <h1>Mes Notes</h1>
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
        onFilterChange={setActiveFilter}
        onSortChange={setSortOrder}
        onSearchChange={setSearchQuery}
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
                onDelete={handleDeleteNote}
                onDragStart={setDraggedNote}
                onDragEnd={() => setDraggedNote(null)}
              />
            ))}
          </div>
        )}
      </div>

      {/* Badges de contacts à droite */}
      <ContactBadges onDrop={handleNoteDrop} />

      {/* Toast Container */}
      <ToastContainer />

      {/* Modal d'édition */}
      {showEditor && (
        <NoteEditor
          note={selectedNote}
          onNoteCreated={handleNoteCreated}
          onNoteDeleted={handleNoteDeleted}
          onClose={() => setShowEditor(false)}
        />
      )}
      </div> {/* Fermeture de main-content */}
    </div>
  );
}
