import { useState, useEffect, useRef } from 'react';
import { noteService } from '../services/note.service';
import { assignmentService } from '../services/assignment.service';
import { authService } from '../services/auth.service';
import { handleAuthError, setEmergencySaveCallback } from '../utils/auth-redirect';
import { saveDraft, loadDraft, clearDraft, getDraftAge } from '../utils/draft-storage';
import { Note } from '../types/note.types';
import { Assignment } from '../types/assignment.types';
import './NoteEditor.css';

interface NoteEditorProps {
  note?: Note | null;
  onNoteCreated?: (note: Note, isNew: boolean) => void; // Passer la note et indiquer si nouvelle
  onNoteDeleted?: () => void;
  onClose?: () => void;
  autoAssignContactId?: number | null; // ID du contact à assigner automatiquement
}

export default function NoteEditor({ note, onNoteCreated, onNoteDeleted, onClose, autoAssignContactId }: NoteEditorProps) {
  const [content, setContent] = useState('');
  const [important, setImportant] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showDraftNotice, setShowDraftNotice] = useState(false);
  const [showSaveConfirmation, setShowSaveConfirmation] = useState(false);
  
  // Timer pour l'auto-sauvegarde
  const autoSaveTimerRef = useRef<number | null>(null);
  
  // Gestion de l'assignation si l'utilisateur est destinataire
  const [myAssignment, setMyAssignment] = useState<Assignment | null>(null);
  const [isCompleted, setIsCompleted] = useState(false);
  const currentUser = authService.getCurrentUser();

  // État local pour la note mise à jour (pour afficher les infos à jour)
  const [currentNote, setCurrentNote] = useState<Note | undefined>(note || undefined);

  // Gestion du panel d'informations
  const [showInfoPanel, setShowInfoPanel] = useState(false);
  const [allAssignments, setAllAssignments] = useState<Assignment[]>([]);
  const [deletionHistory, setDeletionHistory] = useState<Array<{
    user_id: number;
    username: string;
    deleted_date: string;
    deleted_by: number;
    deleted_by_username?: string;
  }>>([]);
  const [completionHistory, setCompletionHistory] = useState<Array<{
    assignment_id: number;
    user_id: number;
    username: string;
    completed_date: string;
    completed_by: number;
  }>>([]);

  // Charger la note si on est en mode édition
  useEffect(() => {
    if (note) {
      setContent(note.content);
      setImportant(note.important);
      setCurrentNote(note);
      
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
      setCurrentNote(undefined);
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

  // Charger l'historique des suppressions et completions quand le panel d'info s'ouvre
  // + recharger les assignations pour voir les mises à jour de statut
  useEffect(() => {
    if (showInfoPanel && note) {
      loadMyAssignment(); // Recharger les assignations pour voir les changements de statut
      loadDeletionHistory();
      loadCompletionHistory();
    }
  }, [showInfoPanel, note?.id]);

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
      // Les assignations contiennent déjà les username grâce au backend
      setAllAssignments(assignments);
      
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

  const loadDeletionHistory = async () => {
    if (!note || !currentUser) {
      return;
    }
    
    // Seulement le créateur peut voir l'historique des suppressions
    if (note.creator_id !== currentUser.id) {
      return;
    }
    
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/v1/notes/${note.id}/deletion-history`, {
        headers: {
          'Authorization': `Bearer ${authService.getToken()}`,
        },
      });
      
      if (!response.ok) {
        throw new Error('Failed to load deletion history');
      }
      
      const data = await response.json();
      setDeletionHistory(data.deletions || []);
      console.log('📜 Historique des suppressions chargé:', data.deletions);
      // Les username sont déjà fournis par le backend
    } catch (err) {
      console.error('❌ Error loading deletion history:', err);
      if (handleAuthError(err)) {
        return; // Redirection en cours
      }
    }
  };

  const loadCompletionHistory = async () => {
    if (!note || !currentUser) {
      return;
    }
    
    // Seulement le créateur peut voir l'historique des completions
    if (note.creator_id !== currentUser.id) {
      return;
    }
    
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/v1/notes/${note.id}/completion-history`, {
        headers: {
          'Authorization': `Bearer ${authService.getToken()}`,
        },
      });
      
      if (!response.ok) {
        throw new Error('Failed to load completion history');
      }
      
      const data = await response.json();
      setCompletionHistory(data.completions || []);
      console.log('✅ Historique des completions chargé:', data.completions);
      // Les username sont déjà fournis par le backend
    } catch (err) {
      console.error('❌ Error loading completion history:', err);
      if (handleAuthError(err)) {
        return; // Redirection en cours
      }
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
      // Récupérer l'assignation mise à jour depuis l'API (avec finished_date)
      const updatedAssignment = await assignmentService.updateStatus(myAssignment.id, newStatus);
      
      // Mettre à jour l'état local avec l'assignation complète
      setIsCompleted(!isCompleted);
      setMyAssignment(updatedAssignment);
      
      // Mettre à jour aussi dans la liste complète des assignations pour le panel d'info
      setAllAssignments((prev: Assignment[]) => 
        prev.map((a: Assignment) => a.id === updatedAssignment.id ? updatedAssignment : a)
      );
      
      // Recharger l'historique des completions pour le créateur
      if (currentUser && note && note.creator_id === currentUser.id) {
        loadCompletionHistory();
      }
      
      // Notifier le parent pour qu'il recharge les assignations (pour mettre à jour la vignette)
      if (note && onNoteCreated) {
        onNoteCreated(note, false); // false = pas une nouvelle note
      }
      
      console.log('✅ Statut mis à jour:', newStatus);
      console.log('📅 finished_date:', updatedAssignment.finished_date);
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
      
      if (note) {
        // Mode édition : sauvegarder sans fermer
        savedNote = await noteService.updateNote(note.id, {
          content: content.trim(),
          important,
        });
        
        // Mettre à jour l'état local de la note pour que les infos soient à jour instantanément
        setCurrentNote(savedNote);
        
        // Supprimer le brouillon car la note est sauvegardée
        clearDraft();
        console.log('[NoteEditor] ✅ Note mise à jour, brouillon supprimé');
        
        // Afficher la confirmation de sauvegarde
        setShowSaveConfirmation(true);
        setTimeout(() => setShowSaveConfirmation(false), 2000); // Masquer après 2 secondes
        
        // Notifier le parent pour mettre à jour la vignette
        if (onNoteCreated) {
          onNoteCreated(savedNote, false); // false = pas une nouvelle note
        }
        
        // NE PAS réinitialiser le formulaire ni fermer l'éditeur
        // La note reste ouverte avec le contenu mis à jour
        
      } else {
        // Mode création : créer et fermer
        savedNote = await noteService.createNote({
          content: content.trim(),
          important,
        });
        
        // Si on crée depuis la vue d'un contact, assigner automatiquement
        if (autoAssignContactId !== null && autoAssignContactId !== undefined) {
          try {
            await assignmentService.createAssignment({
              note_id: savedNote.id,
              user_id: autoAssignContactId
            });
            console.log('[NoteEditor] Note automatiquement assignée au contact', autoAssignContactId);
          } catch (assignErr) {
            console.error('[NoteEditor] Erreur lors de l\'auto-assignation:', assignErr);
            // On ne bloque pas la création de la note même si l'assignation échoue
          }
        }
        
        // Pour une nouvelle note : réinitialiser et fermer
        setContent('');
        setImportant(false);
        clearDraft();
        console.log('[NoteEditor] ✅ Nouvelle note créée, brouillon supprimé');
        
        // Notifier le parent avec la note sauvegardée
        if (onNoteCreated) {
          onNoteCreated(savedNote, true); // true = nouvelle note
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de la sauvegarde de la note');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!note) return;
    
    // Tout le monde (créateur et destinataire) supprime seulement son assignation
    const isCreator = currentUser && note.creator_id === currentUser.id;
    
    if (myAssignment) {
      // Supprimer l'assignation (pour destinataire ET créateur)
      const message = isCreator 
        ? 'Êtes-vous sûr de vouloir retirer cette note de votre liste ? Elle restera visible pour les destinataires.'
        : 'Êtes-vous sûr de vouloir retirer cette note de votre liste ?';
      
      if (!window.confirm(message)) {
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
      // Si le créateur n'a pas d'assignation (note non auto-assignée), on peut supprimer complètement
      if (!window.confirm('Êtes-vous sûr de vouloir supprimer définitivement cette note ? Elle sera supprimée pour tous les destinataires.')) {
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
        
        {/* Message de confirmation de sauvegarde */}
        {showSaveConfirmation && (
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
            ✅ Note sauvegardée !
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
          disabled={isLoading || !!(note && currentUser && note.creator_id !== currentUser.id)}
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
              <span>Marquer comme terminé ✓</span>
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
        {showInfoPanel && currentNote && (
          <div className="info-panel">
            <h3>📋 Informations de la note</h3>
            
            <div className="info-section">
              <strong>Créée le :</strong> {new Date(currentNote.created_date).toLocaleString('fr-FR')}
            </div>

            {currentNote.update_date && (
              <div className="info-section">
                <strong>Modifiée le :</strong> {new Date(currentNote.update_date).toLocaleString('fr-FR')}
              </div>
            )}

            <div className="info-section">
              <strong>Créateur :</strong> {currentNote.creator_username || `Utilisateur #${currentNote.creator_id}`}
            </div>

            {currentNote.deleted_by && (
              <div className="info-section deleted-info">
                <strong>🗑️ Supprimé par :</strong> {currentNote.deleted_by_username || `Utilisateur #${currentNote.deleted_by}`}
                {currentNote.delete_date && (
                  <span className="delete-date">
                    {' '}le {new Date(currentNote.delete_date).toLocaleDateString('fr-FR')} à {new Date(currentNote.delete_date).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}
                  </span>
                )}
              </div>
            )}

            {allAssignments.length > 0 && (
              <div className="info-section">
                <strong>📤 Assignations ({
                  // Si créateur, afficher toutes les assignations, sinon seulement la sienne
                  currentUser && currentNote.creator_id === currentUser.id 
                    ? allAssignments.length 
                    : allAssignments.filter(a => a.user_id === currentUser?.id).length
                }) :</strong>
                <div className="assignments-list">
                  {allAssignments
                    .filter(assignment => {
                      // Si créateur : voir toutes les assignations
                      // Si destinataire : voir seulement sa propre assignation
                      if (currentUser && currentNote.creator_id === currentUser.id) {
                        return true;
                      }
                      return assignment.user_id === currentUser?.id;
                    })
                    .map(assignment => {
                    const userName = assignment.username || `Utilisateur #${assignment.user_id}`;
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
                            {/* La priorité est personnelle : visible uniquement pour le destinataire concerné */}
                            {assignment.recipient_priority && isMe && (
                              <span className="assignment-priority">
                                ⭐ Prioritaire
                              </span>
                            )}
                          </div>
                        </div>
                        
                        {/* Bouton supprimer uniquement si créateur de la note */}
                        {currentUser && currentNote.creator_id === currentUser.id && (
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

            {/* Historique des completions (visible uniquement par le créateur) */}
            {currentUser && currentNote.creator_id === currentUser.id && completionHistory.length > 0 && (
              <div className="info-section completion-history">
                <strong>Terminés ({completionHistory.length}) :</strong>
                <div className="completions-list">
                  {completionHistory.map((completion, index) => {
                    const userName = completion.username || `Utilisateur #${completion.user_id}`;
                    
                    return (
                      <div key={index} className="completion-item">
                        <span className="completion-user">
                          ✅ {userName} a terminé sa note
                        </span>
                        {completion.completed_date && (
                          <span className="completion-date">
                            {' '}le {new Date(completion.completed_date).toLocaleDateString('fr-FR')} à {new Date(completion.completed_date).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}
                          </span>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Historique des suppressions (visible uniquement par le créateur) */}
            {currentUser && currentNote.creator_id === currentUser.id && deletionHistory.length > 0 && (
              <div className="info-section deletion-history">
                <strong>Suppressions ({deletionHistory.length}) :</strong>
                <div className="deletions-list">
                  {deletionHistory.map((deletion, index) => {
                    // Utiliser les username fournis directement par le backend
                    const deletedByName = deletion.deleted_by_username || 
                      (deletion.deleted_by === currentUser.id ? 'Vous' : `Utilisateur #${deletion.deleted_by}`);
                    const recipientName = deletion.username || `Utilisateur #${deletion.user_id}`;
                    
                    // Message différent si le destinataire supprime sa propre assignation ou si le créateur la supprime
                    const isSelfDeletion = deletion.deleted_by === deletion.user_id;
                    const message = isSelfDeletion 
                      ? `${deletedByName} a supprimé son assignation`
                      : `${deletedByName} a supprimé l'assignation de ${recipientName}`;
                    
                    return (
                      <div key={index} className="deletion-item">
                        <span className="deletion-user">
                          👤 {message}
                        </span>
                        {deletion.deleted_date && (
                          <span className="deletion-date">
                            {' '}le {new Date(deletion.deleted_date).toLocaleDateString('fr-FR')} à {new Date(deletion.deleted_date).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}
                          </span>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
