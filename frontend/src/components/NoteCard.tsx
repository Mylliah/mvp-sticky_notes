import { useState, useEffect } from 'react';
import { Note } from '../types/note.types';
import { Assignment } from '../types/assignment.types';
import { authService } from '../services/auth.service';
import { userService } from '../services/user.service';
import './NoteCard.css';

interface NoteCardProps {
  note: Note;
  onEdit?: (note: Note) => void;
  onDelete?: (noteId: number) => void;
  onDragStart?: (note: Note) => void;
  onDragEnd?: () => void;
  onClick?: (note: Note) => void;
  assignments?: Assignment[]; // Pré-chargé par le parent
}

export default function NoteCard({ note, onEdit, onDelete, onDragStart, onDragEnd, onClick, assignments = [] }: NoteCardProps) {
  const currentUser = authService.getCurrentUser();
  const isMyNote = currentUser && Number(note.creator_id) === Number(currentUser.id);
  const [isCompleted, setIsCompleted] = useState(false);
  const [isPriority, setIsPriority] = useState(false);
  const [creatorName, setCreatorName] = useState<string>('');
  
  // Calculer le statut à partir des assignations pré-chargées
  useEffect(() => {
    if (!currentUser || !assignments || assignments.length === 0) {
      setIsCompleted(false);
      setIsPriority(false);
      return;
    }

    console.log(`[NoteCard ${note.id}] 📦 Using pre-loaded assignments:`, assignments);
    
    // Trouver MON assignation
    const myAssignment = assignments.find((a: Assignment) => a.user_id === currentUser.id);
    
    if (myAssignment) {
      const completed = myAssignment.recipient_status === 'terminé';
      const priority = myAssignment.recipient_priority === true;
      console.log(`[NoteCard ${note.id}] ✅ Mon assignation:`, myAssignment, 'Terminé?', completed, 'Priorité?', priority);
      setIsCompleted(completed);
      setIsPriority(priority);
    } else {
      setIsCompleted(false);
      setIsPriority(false);
    }
  }, [note.id, currentUser, assignments]);

  // Charger le nom du créateur
  useEffect(() => {
    const loadCreatorName = async () => {
      // Si c'est ma note, pas besoin de charger
      if (isMyNote) {
        setCreatorName('Moi');
        return;
      }

      try {
        const creator = await userService.getUser(note.creator_id);
        setCreatorName(creator.username);
      } catch (err) {
        console.error(`[NoteCard ${note.id}] ❌ Error loading creator name:`, err);
        setCreatorName(`Utilisateur #${note.creator_id}`);
      }
    };
    loadCreatorName();
  }, [note.id, note.creator_id, isMyNote]);
  
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
    // Retourner le nom chargé, ou un placeholder pendant le chargement
    return creatorName || 'Chargement...';
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

      {/* Badge priorité en bas à gauche si l'assignation est prioritaire */}
      {isPriority && (
        <div className="priority-badge" title="Priorité haute">
          ⭐
        </div>
      )}
    </div>
  );
}
