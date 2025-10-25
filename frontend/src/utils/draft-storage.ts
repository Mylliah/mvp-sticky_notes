/**
 * Utilitaire pour gérer les brouillons de notes dans localStorage
 * Permet de sauvegarder automatiquement et de récupérer les notes en cours d'édition
 */

export interface NoteDraft {
  content: string;
  important: boolean;
  noteId?: number; // undefined si nouvelle note
  timestamp: number; // Quand le brouillon a été sauvegardé
}

const DRAFT_KEY = 'note_draft';
const DRAFT_EXPIRY_HOURS = 24; // Les brouillons expirent après 24h

/**
 * Sauvegarder un brouillon dans localStorage
 */
export function saveDraft(draft: Omit<NoteDraft, 'timestamp'>): void {
  try {
    const draftWithTimestamp: NoteDraft = {
      ...draft,
      timestamp: Date.now(),
    };
    localStorage.setItem(DRAFT_KEY, JSON.stringify(draftWithTimestamp));
    console.log('[Draft] 💾 Brouillon sauvegardé:', draftWithTimestamp);
  } catch (error) {
    console.error('[Draft] ❌ Erreur lors de la sauvegarde:', error);
  }
}

/**
 * Récupérer le brouillon depuis localStorage
 * Retourne null si pas de brouillon ou si expiré
 */
export function loadDraft(): NoteDraft | null {
  try {
    const draftStr = localStorage.getItem(DRAFT_KEY);
    if (!draftStr) {
      return null;
    }

    const draft: NoteDraft = JSON.parse(draftStr);
    
    // Vérifier si le brouillon n'a pas expiré
    const expiryTime = DRAFT_EXPIRY_HOURS * 60 * 60 * 1000;
    const age = Date.now() - draft.timestamp;
    
    if (age > expiryTime) {
      console.log('[Draft] ⏰ Brouillon expiré, suppression');
      clearDraft();
      return null;
    }

    console.log('[Draft] 📂 Brouillon chargé:', draft);
    return draft;
  } catch (error) {
    console.error('[Draft] ❌ Erreur lors du chargement:', error);
    return null;
  }
}

/**
 * Supprimer le brouillon de localStorage
 */
export function clearDraft(): void {
  try {
    localStorage.removeItem(DRAFT_KEY);
    console.log('[Draft] 🗑️ Brouillon supprimé');
  } catch (error) {
    console.error('[Draft] ❌ Erreur lors de la suppression:', error);
  }
}

/**
 * Vérifier si un brouillon existe
 */
export function hasDraft(): boolean {
  return loadDraft() !== null;
}

/**
 * Obtenir l'âge du brouillon en minutes
 */
export function getDraftAge(): number | null {
  const draft = loadDraft();
  if (!draft) return null;
  
  const ageMs = Date.now() - draft.timestamp;
  return Math.floor(ageMs / 60000); // Convertir en minutes
}
