import { useState, useEffect } from 'react';
import { noteService } from '../services/note.service';
import { assignmentService } from '../services/assignment.service';
import { authService } from '../services/auth.service';
import { Note } from '../types/note.types';
import { Assignment } from '../types/assignment.types';
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
  
  // Gestion de l'assignation si l'utilisateur est destinataire
  const [myAssignment, setMyAssignment] = useState<Assignment | null>(null);
  const [isCompleted, setIsCompleted] = useState(false);
  const currentUser = authService.getCurrentUser();

  // Gestion du panel d'informations
  const [showInfoPanel, setShowInfoPanel] = useState(false);
  const [allAssignments, setAllAssignments] = useState<Assignment[]>([]);

  // Charger la note si on est en mode édition
  useEffect(() => {
    if (note) {
      setContent(note.content);
      setImportant(note.important);
      
      // Charger l'assignation de l'utilisateur courant si la note existe
      loadMyAssignment();
    } else {
      // Réinitialiser si on crée une nouvelle note
      setMyAssignment(null);
      setIsCompleted(false);
    }
  }, [note?.id]); // Dépendance sur note.id au lieu de note pour recharger si l'ID change

  const loadMyAssignment = async () => {
    if (!note || !currentUser) {
      console.log('❌ loadMyAssignment : note ou currentUser manquant', { note: !!note, currentUser: !!currentUser });
      return;
    }
    
    console.log('🔄 loadMyAssignment appelé pour note', note.id);
    
    try {
      const assignments = await assignmentService.getAssignments({ note_id: note.id });
      console.log('🔍 Assignments pour note', note.id, ':', assignments);
      console.log('👤 Current user ID:', currentUser.id);
      
      // Stocker toutes les assignations pour le panel d'info
      setAllAssignments(assignments);
      
      const mine = assignments.find(a => {
        console.log('  🔎 Checking assignment:', a.user_id, '=== ', currentUser.id, '?', a.user_id === currentUser.id);
        return a.user_id === currentUser.id;
      });
      console.log('📌 Mon assignation:', mine);
      
      if (mine) {
        setMyAssignment(mine);
        setIsCompleted(mine.recipient_status === 'terminé');
        console.log('✅ Assignation trouvée ! Status:', mine.recipient_status);
      } else {
        // Réinitialiser si pas d'assignation
        setMyAssignment(null);
        setIsCompleted(false);
        console.log('⚠️ Aucune assignation trouvée pour cet utilisateur');
      }
    } catch (err) {
      console.error('❌ Error loading assignment:', err);
    }
  };

  const handleDeleteAssignment = async (assignmentId: number) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer cette assignation ?')) {
      return;
    }

    try {
      await assignmentService.deleteAssignment(assignmentId);
      
      // Recharger les assignations
      await loadMyAssignment();
      
      // Notifier le parent pour rafraîchir la liste
      if (onNoteCreated) {
        onNoteCreated();
      }
    } catch (err) {
      setError('Erreur lors de la suppression de l\'assignation');
      console.error('❌ Error deleting assignment:', err);
    }
  };

  const handleToggleCompleted = async () => {
    if (!myAssignment) return;
    
    const newStatus = isCompleted ? 'en_cours' : 'terminé';
    
    try {
      await assignmentService.updateStatus(myAssignment.id, newStatus);
      setIsCompleted(!isCompleted);
      setMyAssignment({ ...myAssignment, recipient_status: newStatus });
      
      // NE PAS recharger toutes les notes, juste mettre à jour l'état local
      // Le badge sur la NoteCard sera mis à jour à la prochaine ouverture
      console.log('✅ Statut mis à jour:', newStatus);
    } catch (err) {
      setError('Erreur lors de la mise à jour du statut');
      console.error('❌ Erreur updateStatus:', err);
    }
  };

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
            title="Sauvegarder"
          >
            💾
          </button>
          
          <button
            className="action-btn"
            onClick={() => setShowInfoPanel(!showInfoPanel)}
            title="Informations"
            disabled={!note}
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

        {/* Checkbox "Marquer comme terminé" si l'utilisateur est destinataire */}
        {myAssignment && (
          <div className="assignment-status">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={isCompleted}
                onChange={handleToggleCompleted}
                disabled={isLoading}
              />
              <span>✓ Marquer comme terminé</span>
            </label>
          </div>
        )}

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

        {/* Panel d'informations */}
        {showInfoPanel && note && (
          <div className="info-panel">
            <h3>📋 Informations de la note</h3>
            
            <div className="info-section">
              <strong>Créée le :</strong> {new Date(note.created_date).toLocaleString('fr-FR')}
            </div>

            {note.update_date && (
              <div className="info-section">
                <strong>Modifiée le :</strong> {new Date(note.update_date).toLocaleString('fr-FR')}
              </div>
            )}

            <div className="info-section">
              <strong>Créateur :</strong> Utilisateur #{note.creator_id}
            </div>

            {allAssignments.length > 0 && (
              <div className="info-section">
                <strong>📤 Assignations ({allAssignments.length}) :</strong>
                <div className="assignments-list">
                  {allAssignments.map(assignment => (
                    <div key={assignment.id} className="assignment-item">
                      <div className="assignment-details">
                        <span className="assignment-user">
                          👤 Utilisateur #{assignment.user_id}
                          {assignment.user_id === currentUser?.id && ' (Vous)'}
                        </span>
                        <span className={`assignment-status ${assignment.recipient_status}`}>
                          {assignment.recipient_status === 'terminé' ? '✅ Terminé' : '⏳ En cours'}
                        </span>
                        {assignment.is_read && (
                          <span className="assignment-read">📖 Lu</span>
                        )}
                      </div>
                      
                      {/* Bouton supprimer uniquement si créateur de la note */}
                      {currentUser && note.creator_id === currentUser.id && (
                        <button
                          className="delete-assignment-btn"
                          onClick={() => handleDeleteAssignment(assignment.id)}
                          title="Supprimer cette assignation"
                        >
                          🗑️
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {allAssignments.length === 0 && (
              <div className="info-section">
                <em>Cette note n'est assignée à personne</em>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
