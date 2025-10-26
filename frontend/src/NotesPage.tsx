import { useState, useEffect, useRef } from 'react';
import FilterBar, { FilterType, SortOrder } from './components/FilterBar';
import NoteCard from './components/NoteCard';
import NoteEditor from './components/NoteEditor';
import ContactBadges from './components/ContactBadges';
import ContactsManager from './components/ContactsManager';
import ProfileModal from './components/ProfileModal';
import SettingsModal from './components/SettingsModal';
import Sidebar from './components/Sidebar';
import SkeletonCard from './components/SkeletonCard';
import ToastContainer, { useToast } from './components/ToastContainer';
import { Note } from './types/note.types';
import { Assignment } from './types/assignment.types';
import { noteService } from './services/note.service';
import { authService } from './services/auth.service';
import { assignmentService } from './services/assignment.service';
import { contactService } from './services/contact.service';
import { handleAuthError } from './utils/auth-redirect';
import { getErrorMessage, formatErrorMessage } from './utils/error-handler';
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
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [contactsRefreshTrigger, setContactsRefreshTrigger] = useState(0);
  
  // Pagination pour scroll infini
  const [currentPage, setCurrentPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const observerTarget = useRef<HTMLDivElement>(null);
  
  // Filtres
  const [activeFilter, setActiveFilter] = useState<FilterType>('all');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const [searchQuery, setSearchQuery] = useState('');
  const [showArchive, setShowArchive] = useState(false); // Vue Archive
  
  // Filtre par contact
  const [selectedContactId, setSelectedContactId] = useState<number | null>(null);

  // Mode sélection multiple
  const [selectionMode, setSelectionMode] = useState(false);
  const [selectedNotes, setSelectedNotes] = useState<Set<number>>(new Set());

  // Dark mode
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode');
    return saved ? JSON.parse(saved) : false;
  });

  // Sidebar contacts rétractable
  const [contactsSidebarOpen, setContactsSidebarOpen] = useState(true);

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

  // Compteur de notes non lues
  const [unreadCount, setUnreadCount] = useState(0);

  // Charger les notes
  const loadNotes = async (page = 1, append = false) => {
    console.log('[NotesPage] Loading notes with filters:', { 
      page,
      append,
      activeFilter, 
      sortOrder, 
      searchQuery, 
      selectedContactId,
      showArchive
    });
    
    if (page === 1) {
      setLoading(true);
    } else {
      setLoadingMore(true);
    }
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
        setHasMore(false); // Archive ne supporte pas la pagination pour l'instant
        setLoading(false);
        setLoadingMore(false);
        return;
      }
      
      const params: any = {
        sort_by: 'created_date',
        sort_order: sortOrder,
        page: page,
        per_page: 20,
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
      console.log('[NotesPage] Notes loaded:', data.notes?.length || 0, 'Total:', data.total);
      
      let notesToDisplay = data.notes || [];

      // Vérifier s'il y a plus de notes à charger
      const hasMoreNotes = data.notes && data.notes.length === 20;
      setHasMore(hasMoreNotes);

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
      
      // Append ou remplacer les notes selon le mode
      if (append && page > 1) {
        setNotes(prevNotes => [...prevNotes, ...notesToDisplay]);
      } else {
        setNotes(notesToDisplay);
      }
    } catch (err) {
      console.error('[NotesPage] Error loading notes:', err);
      
      // Gérer les erreurs d'authentification
      if (handleAuthError(err)) {
        return; // Redirection en cours
      }
      
      const errorResponse = getErrorMessage(err);
      setError(formatErrorMessage(errorResponse));
    } finally {
      setLoading(false);
      setLoadingMore(false);
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
    // Reset pagination quand les filtres changent
    setCurrentPage(1);
    setHasMore(true);
    loadNotes(1, false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeFilter, sortOrder, searchQuery, selectedContactId, showArchive]);

  // Intersection Observer pour le scroll infini
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        const target = entries[0];
        if (target.isIntersecting && hasMore && !loading && !loadingMore) {
          console.log('[NotesPage] Loading more notes...');
          const nextPage = currentPage + 1;
          setCurrentPage(nextPage);
          loadNotes(nextPage, true);
        }
      },
      { threshold: 0.1 }
    );

    const currentTarget = observerTarget.current;
    if (currentTarget) {
      observer.observe(currentTarget);
    }

    return () => {
      if (currentTarget) {
        observer.unobserve(currentTarget);
      }
    };
  }, [hasMore, loading, loadingMore, currentPage]);

  // Calculer le nombre de notes non lues
  useEffect(() => {
    const user = authService.getCurrentUser();
    if (!user) return;
    
    let count = 0;
    assignmentsMap.forEach((assignments: Assignment[]) => {
      const myAssignment = assignments.find((a: Assignment) => 
        Number(a.user_id) === Number(user.id)
      );
      if (myAssignment && !myAssignment.is_read) {
        count++;
      }
    });
    
    setUnreadCount(count);
  }, [assignmentsMap]);

  // Sauvegarder la préférence dark mode et appliquer la classe
  useEffect(() => {
    localStorage.setItem('darkMode', JSON.stringify(darkMode));
    if (darkMode) {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
  }, [darkMode]);

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
        const errorResponse = getErrorMessage(err);
        addToast({
          message: formatErrorMessage(errorResponse),
          type: 'error',
          duration: 5000,
        });
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
        const errorResponse = getErrorMessage(err);
        addToast({
          message: formatErrorMessage(errorResponse),
          type: 'error',
          duration: 5000,
        });
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
                const errorResponse = getErrorMessage(err);
                addToast({
                  message: formatErrorMessage(errorResponse),
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
      const errorResponse = getErrorMessage(err);
      addToast({
        message: formatErrorMessage(errorResponse),
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
  };

  // === SÉLECTION MULTIPLE ===
  const toggleSelectionMode = () => {
    setSelectionMode(!selectionMode);
    setSelectedNotes(new Set()); // Clear sélection quand on change de mode
  };

  const toggleNoteSelection = (noteId: number) => {
    const newSelection = new Set(selectedNotes);
    if (newSelection.has(noteId)) {
      newSelection.delete(noteId);
    } else {
      newSelection.add(noteId);
    }
    setSelectedNotes(newSelection);
  };

  const selectAllNotes = () => {
    const allNoteIds = new Set(notes.map(note => note.id));
    setSelectedNotes(allNoteIds);
  };

  const clearSelection = () => {
    setSelectedNotes(new Set());
  };

  const handleBatchAssign = async (contactId: number) => {
    if (selectedNotes.size === 0) return;

    try {
      // Assigner toutes les notes sélectionnées
      const noteIds = Array.from(selectedNotes) as number[];
      const promises = noteIds.map(noteId =>
        assignmentService.createAssignment({ note_id: noteId, user_id: contactId })
      );
      
      await Promise.all(promises);
      
      addToast({
        message: `${selectedNotes.size} note(s) assignée(s) avec succès`,
        type: 'success',
        duration: 3000,
      });

      // Clear sélection et recharger
      clearSelection();
      setSelectionMode(false);
      loadNotes();
    } catch (err) {
      console.error('Error batch assigning:', err);
      const errorResponse = getErrorMessage(err);
      addToast({
        message: formatErrorMessage(errorResponse),
        type: 'error',
        duration: 5000,
      });
    }
  };

  const handleBatchDelete = async () => {
    if (selectedNotes.size === 0) return;
    
    if (!window.confirm(`Supprimer ${selectedNotes.size} note(s) ?`)) return;

    try {
      const noteIds = Array.from(selectedNotes) as number[];
      const promises = noteIds.map(noteId =>
        noteService.deleteNote(noteId)
      );
      
      await Promise.all(promises);
      
      addToast({
        message: `${selectedNotes.size} note(s) supprimée(s)`,
        type: 'success',
        duration: 3000,
      });

      clearSelection();
      setSelectionMode(false);
      loadNotes();
    } catch (err) {
      console.error('Error batch deleting:', err);
      const errorResponse = getErrorMessage(err);
      addToast({
        message: formatErrorMessage(errorResponse),
        type: 'error',
        duration: 5000,
      });
    }
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
        onShowProfile={() => setShowProfileModal(true)}
        onShowSettings={() => setShowSettingsModal(true)}
        activeView={showArchive ? 'archive' : (activeFilter === 'all' && !searchQuery ? 'all' : 'filtered')}
      />

      <div className={`main-content ${contactsSidebarOpen ? 'contacts-open' : ''}`}>
        <header className="notes-header">
          <div className="header-left">
            <div className="title-with-badge">
              <h1>{getPageTitle()}</h1>
              {unreadCount > 0 && (
                <span className="unread-badge" title={`${unreadCount} note(s) non lue(s)`}>
                  {unreadCount}
                </span>
              )}
            </div>
            {currentUser && <span className="user-name">Bonjour, {currentUser.username} !</span>}
          </div>
          <div className="header-right">
            <button 
              className={`selection-mode-btn ${selectionMode ? 'active' : ''}`}
              onClick={toggleSelectionMode}
              title={selectionMode ? "Quitter le mode sélection" : "Activer le mode sélection"}
            >
              {selectionMode ? '✓ Sélection' : '☐ Sélection'}
            </button>
            <button 
              className={`dark-mode-btn ${darkMode ? 'active' : ''}`}
              onClick={() => setDarkMode(!darkMode)}
              title={darkMode ? "Mode clair" : "Mode sombre"}
            >
              {darkMode ? '☀️' : '🌙'}
            </button>
            <button 
              className={`contacts-toggle-btn ${contactsSidebarOpen ? 'active' : ''}`}
              onClick={() => setContactsSidebarOpen(!contactsSidebarOpen)}
              title={contactsSidebarOpen ? "Masquer contacts" : "Afficher contacts"}
            >
              {contactsSidebarOpen ? '👥 →' : '← 👥'}
            </button>
            <button 
              className="logout-btn"
              onClick={onLogout}
              title="Déconnexion"
            >
              ⏻
            </button>
          </div>
        </header>

      {/* Barre de filtres */}
      <FilterBar
        onFilterChange={handleFilterChange}
        onSortChange={setSortOrder}
        onSearchChange={setSearchQuery}
        activeFilter={activeFilter}
      />

      {/* Barre d'actions pour sélection multiple */}
      {selectionMode && (
        <div className="selection-toolbar">
          <div className="selection-info">
            <span className="selection-count">
              {selectedNotes.size} note(s) sélectionnée(s)
            </span>
          </div>
          
          <div className="selection-actions">
            <button
              className="selection-action-btn"
              onClick={selectAllNotes}
              disabled={selectedNotes.size === notes.length}
            >
              Tout sélectionner
            </button>
            
            <button
              className="selection-action-btn"
              onClick={clearSelection}
              disabled={selectedNotes.size === 0}
            >
              Désélectionner
            </button>

            {contactsList.length > 0 && (
              <div className="batch-assign-dropdown">
                <select
                  className="selection-action-btn"
                  onChange={(e) => {
                    if (e.target.value) {
                      handleBatchAssign(Number(e.target.value));
                      e.target.value = '';
                    }
                  }}
                  disabled={selectedNotes.size === 0}
                >
                  <option value="">Assigner à...</option>
                  {contactsList.map(contact => (
                    <option key={contact.id} value={contact.id}>
                      {contact.nickname}
                    </option>
                  ))}
                </select>
              </div>
            )}

            <button
              className="selection-action-btn delete-btn"
              onClick={handleBatchDelete}
              disabled={selectedNotes.size === 0}
            >
              Supprimer
            </button>

            <button
              className="selection-action-btn cancel-btn"
              onClick={toggleSelectionMode}
            >
              Annuler
            </button>
          </div>
        </div>
      )}

      {/* Zone de contenu */}
      <div className="notes-content">
        {loading && (
          <div className="notes-grid">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <SkeletonCard key={i} />
            ))}
          </div>
        )}
        
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
          <>
            <div className="notes-grid">
              {notes.map((note, index) => (
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
                  selectionMode={selectionMode}
                  isSelected={selectedNotes.has(note.id)}
                  onToggleSelect={() => toggleNoteSelection(note.id)}
                />
              ))}
            </div>
            
            {/* Indicateur de chargement pour scroll infini */}
            {loadingMore && (
              <div className="loading-more">
                <div className="notes-grid">
                  {[1, 2, 3].map((i) => (
                    <SkeletonCard key={`loading-${i}`} />
                  ))}
                </div>
              </div>
            )}
            
            {/* Observer target pour déclencher le chargement */}
            {hasMore && !loadingMore && (
              <div ref={observerTarget} className="scroll-observer" style={{ height: '20px' }} />
            )}
          </>
        )}
      </div>

      {/* Badges de contacts à droite */}
      <ContactBadges 
        onDrop={handleNoteDrop}
        refreshTrigger={contactsRefreshTrigger}
        onContactClick={handleContactClick}
        selectedContactId={selectedContactId}
        isOpen={contactsSidebarOpen}
        onToggle={() => setContactsSidebarOpen(!contactsSidebarOpen)}
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

      {/* Modal de profil */}
      {showProfileModal && (
        <ProfileModal
          onClose={() => setShowProfileModal(false)}
        />
      )}

      {/* Modal de paramètres */}
      {showSettingsModal && (
        <SettingsModal
          onClose={() => setShowSettingsModal(false)}
          darkMode={darkMode}
          onToggleDarkMode={() => setDarkMode(!darkMode)}
        />
      )}
      </div> {/* Fermeture de main-content */}
    </div>
  );
}
