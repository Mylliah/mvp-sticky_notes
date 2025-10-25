import { useState, useEffect, useRef } from 'react';
import { noteService } from '../services/note.service';
import { assignmentService } from '../services/assignment.service';
import { authService } from '../services/auth.service';
import { userService } from '../services/user.service';
import { handleAuthError, setEmergencySaveCallback } from '../utils/auth-redirect';
import { saveDraft, loadDraft, clearDraft, getDraftAge } from '../utils/draft-storage';
import { Note } from '../types/note.types';
import { Assignment } from '../types/assignment.types';
import { User } from '../types/auth.types';
import './NoteEditor.css';

interface NoteEditorProps {
  note?: Note | null;
  onNoteCreated?: (note: Note, isNew: boolean) => void; // Passer la note et indiquer si nouvelle
  onNoteDeleted?: () => void;
  onClose?: () => void;
}

export default function NoteEditor({ note, onNoteCreated, onNoteDeleted, onClose }: NoteEditorProps) {
  const [content, setContent] = useState('');
  const [important, setImportant] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showDraftNotice, setShowDraftNotice] = useState(false);
  
  // Timer pour l'auto-sauvegarde
  const autoSaveTimerRef = useRef<NodeJS.Timeout | null>(null);
  
  // Gestion de l'assignation si l'utilisateur est destinataire
  const [myAssignment, setMyAssignment] = useState<Assignment | null>(null);
  const [isCompleted, setIsCompleted] = useState(false);
  const currentUser = authService.getCurrentUser();

  // Gestion du panel d'informations
  const [showInfoPanel, setShowInfoPanel] = useState(false);
  const [allAssignments, setAllAssignments] = useState<Assignment[]>([]);
  const [usersMap, setUsersMap] = useState<Map<number, User>>(new Map());
  const [creatorName, setCreatorName] = useState<string>('');

  // Charger la note si on est en mode édition
  useEffect(() => {
    if (note) {
      setContent(note.content);
      setImportant(note.important);
      
      // Charger l'assignation de l'utilisateur courant si la note existe
      loadMyAssignment();
    } else {
      // Mode création : tenter de restaurer un brouillon
      const draft = loadDraft();
      if (draft && !draft.noteId) {
        // C'est un brouillon de nouvelle note
        setContent(draft.content);
        setImportant(draft.important);
        
        const age = getDraftAge();
        if (age !== null) {
          setShowDraftNotice(true);
          console.log(`[NoteEditor] 📂 Brouillon restauré (sauvegardé il y a ${age} min)`);
          
          // Cacher le message après 5 secondes
          setTimeout(() => setShowDraftNotice(false), 5000);
        }
      }
      
      // Réinitialiser si on crée une nouvelle note
      setMyAssignment(null);
      setIsCompleted(false);
    }
  }, [note?.id]); // Dépendance sur note.id au lieu de note pour recharger si l'ID change

  // Auto-sauvegarde toutes les 3 secondes
  useEffect(() => {
    // Ne sauvegarder que si on a du contenu
    if (!content.trim()) {
      return;
    }

    // Annuler le timer précédent
    if (autoSaveTimerRef.current) {
      clearTimeout(autoSaveTimerRef.current);
    }

    // Programmer une nouvelle sauvegarde
    autoSaveTimerRef.current = setTimeout(() => {
      saveDraft({
        content,
        important,
        noteId: note?.id,
      });
    }, 3000); // 3 secondes

    // Cleanup
    return () => {
      if (autoSaveTimerRef.current) {
        clearTimeout(autoSaveTimerRef.current);
      }
    };
  }, [content, important, note?.id]);

  // Enregistrer le callback de sauvegarde d'urgence au montage
  useEffect(() => {
    const emergencySave = () => {
      if (content.trim()) {
        console.log('[NoteEditor] 🚨 Sauvegarde d\'urgence déclenchée');
        saveDraft({
          content,
          important,
          noteId: note?.id,
        });
      }
    };

    setEmergencySaveCallback(emergencySave);

    // Cleanup: retirer le callback au démontage
    return () => {
      setEmergencySaveCallback(null);
    };
  }, [content, important, note?.id]);

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
      
      // Charger les noms d'utilisateurs pour toutes les assignations
      const userIds = assignments.map(a => a.user_id);
      if (userIds.length > 0) {
        try {
          const users = await userService.getUsers(userIds);
          setUsersMap(users);
        } catch (err) {
          console.error('Error loading users:', err);
          if (handleAuthError(err)) {
            return; // Redirection en cours
          }
        }
      }
      
      // Charger le nom du créateur
      try {
        const creator = await userService.getUser(note.creator_id);
        setCreatorName(creator.username);
      } catch (err) {
        console.error('Error loading creator:', err);
        if (handleAuthError(err)) {
          return; // Redirection en cours
        }
        setCreatorName(`Utilisateur #${note.creator_id}`);
      }
      
      const mine = assignments.find(a => {
        console.log('  🔎 Checking assignment:', a.user_id, '=== ', currentUser.id, '?', a.user_id === currentUser.id);
        return a.user_id === currentUser.id;
      });
      console.log('📌 Mon assignation:', mine);
      
      if (mine) {
        setMyAssignment(mine);
        setIsCompleted(mine.recipient_status === 'terminé');
        console.log('✅ Assignation trouvée ! Status:', mine.recipient_status, 'is_read:', mine.is_read);
        
        // Marquer comme lu automatiquement si pas encore lu
        if (!mine.is_read) {
          console.log('🔄 La note n\'est pas encore lue, marquage en cours...');
          await markAsRead(mine.id);
        } else {
          console.log('✅ La note est déjà marquée comme lue');
        }
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

  const markAsRead = async (assignmentId: number) => {
    try {
      console.log('📖 Marquage comme lu de l\'assignation', assignmentId);
      const updatedAssignment = await assignmentService.updateAssignment(assignmentId, { is_read: true });
      console.log('✅ Assignation mise à jour:', updatedAssignment);
      
      // Mettre à jour l'état local sans recharger
      setMyAssignment(updatedAssignment);
      
      // Mettre à jour aussi dans la liste complète des assignations
      setAllAssignments((prev: Assignment[]) => 
        prev.map((a: Assignment) => a.id === assignmentId ? updatedAssignment : a)
      );
      
      console.log('✅ État local mis à jour');
    } catch (err) {
      console.error('❌ Erreur lors du marquage comme lu:', err);
    }
  };

  const handleDeleteAssignment = async (assignmentId: number) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer cette assignation ?')) {
      return;
    }

    try {
      await assignmentService.deleteAssignment(assignmentId);
      
      // Recharger les assignations de cette note
      await loadMyAssignment();
      
      // La mise à jour visuelle se fera automatiquement via le state local
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

  const handleTogglePriority = async () => {
    if (!myAssignment) return;
    
    try {
      console.log('🌟 Toggle priorité pour assignation', myAssignment.id, '- État actuel:', myAssignment.recipient_priority);
      
      // Utiliser la méthode dédiée togglePriority
      const updatedAssignment = await assignmentService.togglePriority(myAssignment.id);
      
      console.log('✅ Priorité mise à jour:', updatedAssignment);
      console.log('📌 Nouvelle valeur recipient_priority:', updatedAssignment.recipient_priority);
      
      // Mettre à jour l'état local immédiatement
      setMyAssignment(updatedAssignment);
      
      // Mettre à jour aussi dans la liste complète des assignations pour le panel d'info
      setAllAssignments((prev: Assignment[]) => 
        prev.map((a: Assignment) => a.id === updatedAssignment.id ? updatedAssignment : a)
      );
      
      console.log('🔄 État React mis à jour !');
      
    } catch (err) {
      setError('Erreur lors de la mise à jour de la priorité');
      console.error('❌ Erreur togglePriority:', err);
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
      let savedNote: Note;
      const isNew = !note;
      
      if (note) {
        // Mode édition
        savedNote = await noteService.updateNote(note.id, {
          content: content.trim(),
          important,
        });
      } else {
        // Mode création
        savedNote = await noteService.createNote({
          content: content.trim(),
          important,
        });
      }
      
      // Réinitialiser le formulaire
      setContent('');
      setImportant(false);
      
      // Supprimer le brouillon sauvegardé car la note est maintenant enregistrée
      clearDraft();
      console.log('[NoteEditor] ✅ Note sauvegardée, brouillon supprimé');
      
      // Notifier le parent avec la note sauvegardée et si c'est une nouvelle
      if (onNoteCreated) {
        onNoteCreated(savedNote, isNew);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de la sauvegarde de la note');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!note) return;
    
    // Si l'utilisateur est le destinataire (pas le créateur), supprimer seulement l'assignation
    const isCreator = currentUser && note.creator_id === currentUser.id;
    
    if (!isCreator && myAssignment) {
      // Destinataire : supprimer l'assignation
      if (!window.confirm('Êtes-vous sûr de vouloir retirer cette note de votre liste ?')) {
        return;
      }
      
      setIsLoading(true);
      setError(null);
      
      try {
        await assignmentService.deleteAssignment(myAssignment.id);
        
        // Notifier le parent
        if (onNoteDeleted) {
          onNoteDeleted();
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erreur lors de la suppression de l\'assignation');
      } finally {
        setIsLoading(false);
      }
    } else if (isCreator) {
      // Créateur : supprimer la note complètement
      if (!window.confirm('Êtes-vous sûr de vouloir supprimer cette note ? Elle sera supprimée pour tous les destinataires.')) {
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
    }
  };

  return (
    <div className="note-editor-overlay">
      <div className="note-editor-modal">
        {/* Message de brouillon restauré */}
        {showDraftNotice && (
          <div style={{
            position: 'absolute',
            top: '10px',
            left: '50%',
            transform: 'translateX(-50%)',
            background: '#4CAF50',
            color: 'white',
            padding: '8px 16px',
            borderRadius: '4px',
            fontSize: '14px',
            zIndex: 1000,
            boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
          }}>
            💾 Brouillon restauré !
          </div>
        )}
        
        {/* Barre d'actions supérieure */}
        <div className="note-editor-actions">
          {/* Bouton Important - visible pour le créateur (existant) OU lors de la création */}
          {currentUser && (!note || note.creator_id === currentUser.id) && (
            <button
              className="action-btn"
              onClick={() => setImportant(!important)}
              title="Marquer comme important"
            >
              {important ? '❗' : '❕'}
            </button>
          )}
          
          {/* Bouton Priorité - visible si l'utilisateur a une assignation (même s'il est créateur) */}
          {myAssignment && (
            <button
              className="action-btn"
              onClick={handleTogglePriority}
              title={myAssignment.recipient_priority ? "Retirer la priorité" : "Marquer comme prioritaire"}
            >
              {myAssignment.recipient_priority ? '⭐' : '☆'}
            </button>
          )}
          
          {/* Bouton Sauvegarder - visible seulement pour le créateur ou nouvelle note */}
          {(!note || (currentUser && note.creator_id === currentUser.id)) && (
            <button
              className="action-btn"
              onClick={handleSubmit}
              disabled={isLoading || !content.trim()}
              title="Sauvegarder"
            >
              💾
            </button>
          )}
          
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
            title={currentUser && note && note.creator_id === currentUser.id ? "Supprimer la note" : "Retirer de ma liste"}
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
          disabled={isLoading || (note && currentUser && note.creator_id !== currentUser.id)}
          maxLength={5000}
          autoFocus
        />
        
        {/* Compteur de caractères */}
        <div style={{
          fontSize: '12px',
          color: content.length > 4500 ? '#f44336' : '#999',
          textAlign: 'right',
          marginTop: '8px',
          fontWeight: content.length > 4500 ? 'bold' : 'normal',
        }}>
          {content.length} / 5000 caractères
        </div>

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
              <strong>Créateur :</strong> {creatorName || `Utilisateur #${note.creator_id}`}
            </div>

            {note.deleted_by && (
              <div className="info-section deleted-info">
                <strong>🗑️ Supprimé par :</strong> {usersMap.get(note.deleted_by)?.username || `Utilisateur #${note.deleted_by}`}
                {note.delete_date && (
                  <span className="delete-date">
                    {' '}le {new Date(note.delete_date).toLocaleDateString('fr-FR')} à {new Date(note.delete_date).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}
                  </span>
                )}
              </div>
            )}

            {allAssignments.length > 0 && (
              <div className="info-section">
                <strong>📤 Assignations ({allAssignments.length}) :</strong>
                <div className="assignments-list">
                  {allAssignments.map(assignment => {
                    const assignedUser = usersMap.get(assignment.user_id);
                    const userName = assignedUser?.username || `Utilisateur #${assignment.user_id}`;
                    const isMe = assignment.user_id === currentUser?.id;
                    
                    return (
                      <div key={assignment.id} className="assignment-item">
                        <div className="assignment-details">
                          <span className="assignment-user">
                            👤 {userName}{isMe && ' (Vous)'}
                          </span>
                          <div className="assignment-info">
                            <span className={`assignment-status ${assignment.recipient_status}`}>
                              {assignment.recipient_status === 'terminé' ? '✅ Terminé' : '⏳ En cours'}
                            </span>
                            <span className="assignment-date">
                              📅 Assigné le {new Date(assignment.assigned_date).toLocaleDateString('fr-FR')}
                            </span>
                            {assignment.read_date && (
                              <span className="assignment-read">
                                📖 Lu le {new Date(assignment.read_date).toLocaleDateString('fr-FR')} à {new Date(assignment.read_date).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}
                              </span>
                            )}
                            {!assignment.read_date && (
                              <span className="assignment-unread">
                                ✉️ Non lu
                              </span>
                            )}
                            {assignment.finished_date && (
                              <span className="assignment-finished">
                                🏁 Terminé le {new Date(assignment.finished_date).toLocaleDateString('fr-FR')} à {new Date(assignment.finished_date).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}
                              </span>
                            )}
                            {/* La priorité est personnelle : visible uniquement pour le destinataire concerné */}
                            {assignment.recipient_priority && isMe && (
                              <span className="assignment-priority">
                                ⭐ Prioritaire
                              </span>
                            )}
                          </div>
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
                    );
                  })}
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
