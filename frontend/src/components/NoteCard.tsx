import { Note } from '../types/note.types';
import { authService } from '../services/auth.service';
import './NoteCard.css';

interface NoteCardProps {
  note: Note;
  onEdit?: (note: Note) => void;
  onDelete?: (noteId: number) => void;
}

export default function NoteCard({ note, onEdit, onDelete }: NoteCardProps) {
  const currentUser = authService.getCurrentUser();
  const isMyNote = currentUser && Number(note.creator_id) === Number(currentUser.id);
  
  // Debug: afficher les valeurs dans la console
  console.log('NoteCard Debug:', {
    currentUserId: currentUser?.id,
    noteCreatorId: note.creator_id,
    isMyNote,
    currentUser
  });
  
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  };

  const getCreatorName = () => {
    if (isMyNote) {
      return 'Moi';
    }
    // TODO: Récupérer le vrai nom depuis l'API
    return `Utilisateur #${note.creator_id}`;
  };

  return (
    <div className={`note-card ${note.important ? 'important' : ''}`}>
      {/* En-tête avec créateur et date */}
      <div className="note-header">
        <span className="note-creator">de {getCreatorName()}</span>
        <span className="note-date">créé le {formatDate(note.created_date)}</span>
      </div>

      {/* Contenu de la note */}
      <div className="note-body">
        {note.content}
      </div>

      {/* Icône d'édition */}
      <button
        className="note-edit-btn"
        onClick={() => onEdit && onEdit(note)}
        title="Modifier"
      >
        ✏️
      </button>

      {/* Badge important si applicable */}
      {note.important && (
        <div className="important-badge">
          ❗
        </div>
      )}
    </div>
  );
}
