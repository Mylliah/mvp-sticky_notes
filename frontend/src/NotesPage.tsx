import { useState, useEffect } from 'react';
import FilterBar, { FilterType, SortOrder } from './components/FilterBar';
import NoteCard from './components/NoteCard';
import NoteEditor from './components/NoteEditor';
import { Note } from './types/note.types';
import { noteService } from './services/note.service';
import { authService } from './services/auth.service';
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

  // Charger les notes
  const loadNotes = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const params: any = {
        sort_by: 'created_date',
        sort_order: sortOrder,
      };

      // Appliquer les filtres
      if (activeFilter === 'important') {
        params.important = true;
      }

      if (searchQuery) {
        params.q = searchQuery;
      }

      const data = await noteService.getNotes(params);
      setNotes(data.notes || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur de chargement');
    } finally {
      setLoading(false);
    }
  };

  // Charger les notes au montage et quand les filtres changent
  useEffect(() => {
    loadNotes();
  }, [activeFilter, sortOrder, searchQuery]);

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

  const currentUser = authService.getCurrentUser();

  return (
    <div className="notes-page">
      <header className="notes-header">
        <div className="header-left">
          <h1>Mes Notes</h1>
          {currentUser && <span className="user-name">Bonjour, {currentUser.username} !</span>}
        </div>
        <div className="header-right">
          <button
            className="new-note-btn"
            onClick={() => {
              setSelectedNote(null);
              setShowEditor(true);
            }}
          >
            + Nouvelle Note
          </button>
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
              />
            ))}
          </div>
        )}
      </div>

      {/* Modal d'édition */}
      {showEditor && (
        <NoteEditor
          note={selectedNote}
          onNoteCreated={handleNoteCreated}
          onNoteDeleted={handleNoteDeleted}
          onClose={() => setShowEditor(false)}
        />
      )}
    </div>
  );
}
