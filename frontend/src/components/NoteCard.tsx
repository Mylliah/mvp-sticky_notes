import { useState, useEffect } from 'react';
import { Note } from '../types/note.types';
import { authService } from '../services/auth.service';
import { assignmentService } from '../services/assignment.service';
import './NoteCard.css';

interface NoteCardProps {
  note: Note;
  onEdit?: (note: Note) => void;
  onDelete?: (noteId: number) => void;
  onDragStart?: (note: Note) => void;
  onDragEnd?: () => void;
  onClick?: (note: Note) => void;
}

export default function NoteCard({ note, onEdit, onDelete, onDragStart, onDragEnd, onClick }: NoteCardProps) {
  const currentUser = authService.getCurrentUser();
  const isMyNote = currentUser && Number(note.creator_id) === Number(currentUser.id);
  const [isCompleted, setIsCompleted] = useState(false);
  
  // Charger le statut de l'assignation au montage
  useEffect(() => {
    const loadAssignmentStatus = async () => {
      if (!currentUser) return;
      
      console.log(`[NoteCard ${note.id}] 🔄 Chargement du statut...`);
      
      try {
        const assignments = await assignmentService.getAssignments({ note_id: note.id });
        console.log(`[NoteCard ${note.id}] 📦 Assignments reçus:`, assignments);
        
        if (assignments && assignments.length > 0) {
          // Vérifier si MON assignation (user_id = moi) est terminée
          const myAssignment = assignments.find(a => {
            console.log(`[NoteCard ${note.id}] 🔍 Compare: ${a.user_id} === ${currentUser.id} ?`, a.user_id === currentUser.id);
            return a.user_id === currentUser.id;
          });
          
          const completed = myAssignment?.recipient_status === 'terminé';
          console.log(`[NoteCard ${note.id}] ✅ Mon assignation:`, myAssignment, 'Terminé?', completed);
          setIsCompleted(completed);
        } else {
          console.log(`[NoteCard ${note.id}] ⚠️ Aucune assignation trouvée`);
          setIsCompleted(false);
        }
      } catch (err) {
        console.error(`[NoteCard ${note.id}] ❌ Error loading assignment status:`, err);
      }
    };
    loadAssignmentStatus();
  }, [note.id, currentUser]);
  
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

  const handleDragStart = (e: React.DragEvent) => {
    if (onDragStart) {
      onDragStart(note);
    }
    // Ajouter une classe pour le feedback visuel
    e.currentTarget.classList.add('dragging');
    
    // Stocker l'ID de la note dans le dataTransfer
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', note.id.toString());
  };

  const handleDragEnd = (e: React.DragEvent) => {
    e.currentTarget.classList.remove('dragging');
    if (onDragEnd) {
      onDragEnd();
    }
  };

  return (
    <div 
      className={`note-card ${note.important ? 'important' : ''}`}
      draggable={true}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
      onClick={() => onClick && onClick(note)}
      style={{ cursor: onClick ? 'pointer' : 'default' }}
    >
      {/* En-tête avec créateur et date */}
      <div className="note-header">
        <span className="note-creator">de {getCreatorName()}</span>
        <span className="note-date">créé le {formatDate(note.created_date)}</span>
      </div>

      {/* Contenu de la note */}
      <div className="note-body">
        {note.content}
      </div>

      {/* Icône d'édition - visible uniquement pour le créateur */}
      {isMyNote && (
        <button
          className="note-edit-btn"
          onClick={() => onEdit && onEdit(note)}
          title="Modifier"
        >
          ✏️
        </button>
      )}

      {/* Badge important si applicable */}
      {note.important && (
        <div className="important-badge">
          ❗
        </div>
      )}

      {/* Badge "terminé" si au moins une assignation est terminée */}
      {isCompleted && (
        <div className="completed-badge" title="Terminé">
          ✓
        </div>
      )}
    </div>
  );
}
