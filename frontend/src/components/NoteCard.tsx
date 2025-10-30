import { useState, useEffect, useRef } from 'react';
import { Note } from '../types/note.types';
import { Assignment } from '../types/assignment.types';
import { authService } from '../services/auth.service';
import { userService } from '../services/user.service';
import { handleAuthError } from '../utils/auth-redirect';
import './NoteCard.css';

interface NoteCardProps {
  note: Note;
  onEdit?: (note: Note) => void;
  onDelete?: (noteId: number) => void;
  onDragStart?: (note: Note) => void;
  onDragEnd?: () => void;
  onClick?: (note: Note) => void;
  assignments?: Assignment[]; // Pré-chargé par le parent
  onAssign?: (noteId: number, contactId: number) => void; // Nouveau callback pour l'assignation
  contacts?: Array<{ id: number; nickname: string }>; // Liste des contacts disponibles
  isOrphan?: boolean; // Indique si la note est orpheline (sans assignation)
  selectionMode?: boolean; // Mode sélection multiple
  isSelected?: boolean; // Note sélectionnée
  onToggleSelect?: () => void; // Callback pour toggler la sélection
}

export default function NoteCard({ note, onEdit, onDelete, onDragStart, onDragEnd, onClick, assignments = [], onAssign, contacts = [], isOrphan = false, selectionMode = false, isSelected = false, onToggleSelect }: NoteCardProps) {
  const currentUser = authService.getCurrentUser();
  const isMyNote = currentUser && Number(note.creator_id) === Number(currentUser.id);
  const [isCompleted, setIsCompleted] = useState(false);
  const [isPriority, setIsPriority] = useState(false);
  const [isNew, setIsNew] = useState(false);
  const [creatorName, setCreatorName] = useState<string>('');
  const [recipientsText, setRecipientsText] = useState<string>('');
  const [isSelfAssigned, setIsSelfAssigned] = useState(false); // Pour distinguer "à Moi-même" des autres
  const [showAssignMenu, setShowAssignMenu] = useState(false);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const menuRef = useRef<HTMLDivElement>(null);
  
  // Fermer le menu quand on clique ailleurs
  useEffect(() => {
    if (!showAssignMenu) return;
    
    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as Node;
      // Ne fermer que si le clic est en dehors du bouton ET du menu
      if (buttonRef.current && !buttonRef.current.contains(target) &&
          menuRef.current && !menuRef.current.contains(target)) {
        setShowAssignMenu(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showAssignMenu]);
  
  // État pour distinguer le statut de complétion (partiel vs total)
  const [completionStatus, setCompletionStatus] = useState<'none' | 'partial' | 'full'>('none');

  // Calculer le statut à partir des assignations pré-chargées
  useEffect(() => {
    if (!currentUser || !assignments || assignments.length === 0) {
      setIsCompleted(false);
      setIsPriority(false);
      setIsNew(false);
      setCompletionStatus('none');
      return;
    }

    console.log(`[NoteCard ${note.id}] 📦 Using pre-loaded assignments:`, assignments);
    
    // Trouver MON assignation
    const myAssignment = assignments.find((a: Assignment) => a.user_id === currentUser.id);
    
    if (myAssignment) {
      const priority = myAssignment.recipient_priority === true;
      const isUnread = !myAssignment.is_read;
      
      // LOGIQUE DE LA COCHE VERTE
      if (isMyNote) {
        // Je suis le CRÉATEUR : vérifier le statut de TOUS les assignés
        const totalAssignments = assignments.length;
        const completedAssignments = assignments.filter(a => a.recipient_status === 'terminé').length;
        
        console.log(`[NoteCard ${note.id}] 👤 CRÉATEUR: ${completedAssignments}/${totalAssignments} terminés`);
        
        if (completedAssignments === 0) {
          setIsCompleted(false);
          setCompletionStatus('none');
        } else if (completedAssignments === totalAssignments) {
          setIsCompleted(true);
          setCompletionStatus('full'); // Tous terminés = vert foncé
        } else {
          setIsCompleted(true);
          setCompletionStatus('partial'); // Quelques-uns terminés = vert clair
        }
      } else {
        // Je suis un DESTINATAIRE : afficher seulement MON statut
        const myCompleted = myAssignment.recipient_status === 'terminé';
        console.log(`[NoteCard ${note.id}] 📨 DESTINATAIRE: Mon statut =`, myCompleted ? 'terminé' : 'en cours');
        
        setIsCompleted(myCompleted);
        setCompletionStatus(myCompleted ? 'full' : 'none'); // Ma coche = vert foncé
      }
      
      setIsPriority(priority);
      setIsNew(isUnread);
    } else {
      setIsCompleted(false);
      setIsPriority(false);
      setIsNew(false);
      setCompletionStatus('none');
    }
  }, [note.id, currentUser, assignments, isMyNote]);

  // Charger le nom du créateur et des destinataires
  useEffect(() => {
    const loadNames = async () => {
      // Charger le nom du créateur
      if (isMyNote) {
        setCreatorName('Moi');
      } else {
        try {
          const creator = await userService.getUser(note.creator_id);
          setCreatorName(creator.username);
        } catch (err) {
          console.error(`[NoteCard ${note.id}] ❌ Error loading creator name:`, err);
          if (handleAuthError(err)) {
            return; // Redirection en cours
          }
          setCreatorName(`Utilisateur #${note.creator_id}`);
        }
      }

      // Charger les noms des destinataires
      if (assignments && assignments.length > 0) {
        try {
          // CAS SPÉCIAL : Note self-only (créée par moi et assignée qu'à moi)
          if (isMyNote && assignments.length === 1 && currentUser && assignments[0].user_id === currentUser.id) {
            setRecipientsText('à Moi-même');
            setIsSelfAssigned(true);
            return;
          }
          
          setIsSelfAssigned(false);
          
          // Si je ne suis PAS le créateur, ne montrer que ma propre assignation
          let assignmentsToShow = assignments;
          if (!isMyNote && currentUser) {
            assignmentsToShow = assignments.filter(
              (assignment) => assignment.user_id === currentUser.id
            );
          }
          
          // Si aucune assignation à afficher, on arrête
          if (assignmentsToShow.length === 0) {
            setRecipientsText('');
            return;
          }
          
          // Charger les noms des destinataires à afficher
          const recipientNames = await Promise.all(
            assignmentsToShow.map(async (assignment) => {
              // Si c'est moi, afficher "Moi"
              if (currentUser && assignment.user_id === currentUser.id) {
                return 'Moi';
              }
              
              try {
                // D'abord chercher le nickname dans la liste des contacts
                const contact = contacts.find(c => c.id === assignment.user_id);
                if (contact && contact.nickname) {
                  return contact.nickname;
                }
                
                // Sinon, charger depuis l'API
                const user = await userService.getUser(assignment.user_id);
                return user.username;
              } catch (err) {
                console.error(`Error loading user ${assignment.user_id}:`, err);
                if (handleAuthError(err)) {
                  return null; // Redirection en cours
                }
                return `Utilisateur #${assignment.user_id}`;
              }
            })
          );
          
          // Filtrer les null (erreurs d'auth)
          const validNames = recipientNames.filter(name => name !== null) as string[];

          // Formater le texte selon le nombre de destinataires
          if (validNames.length === 0) {
            setRecipientsText('');
          } else if (validNames.length === 1) {
            setRecipientsText(`à ${validNames[0]}`);
          } else if (validNames.length === 2) {
            setRecipientsText(`à ${validNames[0]} et ${validNames[1]}`);
          } else if (validNames.length === 3) {
            setRecipientsText(`à ${validNames[0]}, ${validNames[1]} et ${validNames[2]}`);
          } else {
            setRecipientsText(`à ${validNames.length} personnes`);
          }
        } catch (err) {
          console.error(`[NoteCard ${note.id}] ❌ Error loading recipients:`, err);
          if (handleAuthError(err)) {
            return; // Redirection en cours
          }
          setRecipientsText('');
        }
      } else {
        setRecipientsText('');
      }
    };
    
    loadNames();
  }, [note.id, note.creator_id, isMyNote, assignments, currentUser]);
  
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

  // Vérifier si la note est auto-assignée uniquement (créée par moi ET assignée QU'À moi)
  const isSelfOnlyNote = () => {
    if (!currentUser || !isMyNote) return false;
    
    // Si pas d'assignations du tout, ce n'est pas une note "self-only"
    if (!assignments || assignments.length === 0) return false;
    
    // Vérifier si toutes les assignations sont pour moi uniquement
    const allAssignmentsAreToMe = assignments.every(a => a.user_id === currentUser.id);
    return allAssignmentsAreToMe && assignments.length === 1;
  };

  return (
    <div 
      className={`note-card ${note.important ? 'important' : ''} ${showAssignMenu ? 'menu-open' : ''} ${isOrphan ? 'orphan' : ''} ${selectionMode ? 'selection-mode' : ''} ${isSelected ? 'selected' : ''} ${isSelfOnlyNote() ? 'self-only' : ''}`}
      draggable={!selectionMode}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
      onClick={() => {
        if (selectionMode && onToggleSelect) {
          onToggleSelect();
        } else if (onClick) {
          onClick(note);
        }
      }}
      style={{ cursor: onClick || selectionMode ? 'pointer' : 'default' }}
      title={isOrphan ? '⚠️ Note sans assignation - Peut être supprimée définitivement' : ''}
    >
      {/* Checkbox en mode sélection */}
      {selectionMode && (
        <div className="note-checkbox" onClick={(e) => e.stopPropagation()}>
          <input
            type="checkbox"
            checked={isSelected}
            onChange={onToggleSelect}
          />
        </div>
      )}

      {/* En-tête avec créateur et date */}
      <div className="note-header">
        <div className="note-metadata">
          {/* Ne pas afficher "de Moi" pour les notes self-only */}
          {!isSelfOnlyNote() && (
            <span className="note-creator">de {getCreatorName()}</span>
          )}
          {recipientsText && (
            <span className={`note-recipients ${!isSelfAssigned ? 'assigned-to-others' : ''}`}>{recipientsText}</span>
          )}
        </div>
        <div className="note-header-right" onClick={(e) => e.stopPropagation()}>
          {/* Bouton d'assignation dans le bandeau - visible uniquement pour le créateur */}
          {isMyNote && onAssign && contacts.length > 0 && (
            <div className="assign-menu-container">
              <button
                ref={buttonRef}
                className="assign-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  setShowAssignMenu(!showAssignMenu);
                }}
                title="Assigner cette note"
              >
                👥
              </button>
              
              {showAssignMenu && (
                <div 
                  ref={menuRef}
                  className="assign-menu"
                >
                  <div className="assign-menu-header">
                    Assigner à :
                  </div>
                  {contacts.map((contact) => (
                    <button
                      key={contact.id}
                      className="assign-menu-item"
                      onClick={(e) => {
                        e.stopPropagation();
                        onAssign(note.id, contact.id);
                        setShowAssignMenu(false);
                      }}
                    >
                      {contact.nickname}
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Badge important si applicable - en haut à gauche */}
      {note.important && (
        <div className="important-badge">
          ❗
        </div>
      )}

      {/* Badge "Nouveau" si note récemment reçue et non lue - en haut à droite */}
      {isNew && (
        <div className="new-badge" title="Nouvelle note non lue">
          NOUVEAU
        </div>
      )}

      {/* Contenu de la note */}
      <div className="note-body">
        {note.content}
      </div>

      {/* Icône d'édition - visible uniquement pour le créateur et au survol */}
      {isMyNote && (
        <button
          className="note-edit-btn"
          onClick={(e) => {
            e.stopPropagation();
            onEdit && onEdit(note);
          }}
          title="Modifier"
        >
          ✏️
        </button>
      )}

      {/* Badge "terminé" avec couleur selon le statut */}
      {isCompleted && (
        <div 
          className={`completed-badge ${completionStatus === 'partial' ? 'partial' : 'full'}`}
          title={
            completionStatus === 'partial' 
              ? 'Terminé partiellement (certains contacts ont terminé)' 
              : 'Terminé'
          }
        >
          ✓
        </div>
      )}

      {/* Badge priorité en bas à gauche si l'assignation est prioritaire */}
      {isPriority && (
        <div className="priority-badge" title="Priorité haute">
          ⭐
        </div>
      )}

      {/* Date de création en bas à droite */}
      <span className="note-date">créé le {formatDate(note.created_date)}</span>
    </div>
  );
}
