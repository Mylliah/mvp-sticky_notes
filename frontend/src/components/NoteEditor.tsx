import { useState, useEffect } from 'react';
import { noteService } from '../services/note.service';
import { Note } from '../types/note.types';
import './NoteEditor.css';

interface NoteEditorProps {
  note?: Note | null;
  onNoteCreated?: () => void;
  onNoteDeleted?: () => void;
  onClose?: () => void;
}

export default function NoteEditor({ note, onNoteCreated, onNoteDeleted, onClose }: NoteEditorProps) {
  const [content, setContent] = useState('');
  const [important, setImportant] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Charger la note si on est en mode édition
  useEffect(() => {
    if (note) {
      setContent(note.content);
      setImportant(note.important);
    }
  }, [note]);

  const handleSubmit = async () => {
    if (!content.trim()) {
      setError('Le contenu de la note ne peut pas être vide');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      if (note) {
        // Mode édition
        await noteService.updateNote(note.id, {
          content: content.trim(),
          important,
        });
      } else {
        // Mode création
        await noteService.createNote({
          content: content.trim(),
          important,
        });
      }
      
      // Réinitialiser le formulaire
      setContent('');
      setImportant(false);
      
      // Notifier le parent
      if (onNoteCreated) {
        onNoteCreated();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de la sauvegarde de la note');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!note) return;
    
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer cette note ?')) {
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      await noteService.deleteNote(note.id);
      
      // Notifier le parent
      if (onNoteDeleted) {
        onNoteDeleted();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de la suppression');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="note-editor-overlay">
      <div className="note-editor-modal">
        {/* Barre d'actions supérieure */}
        <div className="note-editor-actions">
          <button
            className="action-btn"
            onClick={() => setImportant(!important)}
            title="Marquer comme important"
          >
            {important ? '❗' : '❕'}
          </button>
          
          <button
            className="action-btn"
            onClick={handleSubmit}
            disabled={isLoading || !content.trim()}
            title="Valider"
          >
            ✓
          </button>
          
          <button
            className="action-btn"
            title="Informations"
          >
            ℹ
          </button>
          
          <button
            className="action-btn"
            onClick={handleDelete}
            disabled={isLoading || !note}
            title="Supprimer"
          >
            🗑
          </button>
          
          <button
            className="action-btn close-btn"
            onClick={onClose}
            title="Fermer"
          >
            ×
          </button>
        </div>

        {/* Zone de texte */}
        <textarea
          className="note-content"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Écrivez votre note ici..."
          disabled={isLoading}
          autoFocus
        />

        {/* Message d'erreur */}
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {/* Indicateur de chargement */}
        {isLoading && (
          <div className="loading-indicator">
            {note ? 'Modification en cours...' : 'Création en cours...'}
          </div>
        )}
      </div>
    </div>
  );
}
