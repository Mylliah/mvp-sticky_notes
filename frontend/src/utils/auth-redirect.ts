/**
 * Utilitaire pour gérer les erreurs d'authentification
 * et rediriger vers la page de login si nécessaire
 */

import { authService } from '../services/auth.service';

// Variable globale pour stocker le callback de sauvegarde d'urgence
let emergencySaveCallback: (() => void) | null = null;

/**
 * Enregistrer un callback à appeler avant la redirection (pour sauvegarder les données)
 */
export function setEmergencySaveCallback(callback: (() => void) | null): void {
  emergencySaveCallback = callback;
}

/**
 * Vérifie si une erreur est liée à l'authentification
 */
export function isAuthError(error: unknown): boolean {
  if (error instanceof Error) {
    const message = error.message.toLowerCase();
    return (
      message.includes('token') ||
      message.includes('401') ||
      message.includes('unauthorized') ||
      message.includes('log in again') ||
      message.includes('authentication')
    );
  }
  return false;
}

/**
 * Gère une erreur en redirigeant vers login si c'est une erreur d'auth
 * @returns true si c'était une erreur d'auth et qu'on a redirigé
 */
export function handleAuthError(error: unknown): boolean {
  if (isAuthError(error)) {
    console.warn('[Auth] ⚠️ Token expired or invalid, saving data and redirecting...');
    
    // Appeler le callback de sauvegarde d'urgence si disponible
    if (emergencySaveCallback) {
      try {
        console.log('[Auth] 💾 Sauvegarde d\'urgence en cours...');
        emergencySaveCallback();
      } catch (saveError) {
        console.error('[Auth] ❌ Erreur lors de la sauvegarde d\'urgence:', saveError);
      }
    }
    
    // Déconnecter l'utilisateur
    authService.logout();
    
    // Afficher un message à l'utilisateur
    const hasUnsavedData = emergencySaveCallback !== null;
    if (hasUnsavedData) {
      // Créer un toast/alert temporaire
      const alertDiv = document.createElement('div');
      alertDiv.style.cssText = `
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: #2196F3;
        color: white;
        padding: 16px 24px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 10000;
        font-size: 14px;
        font-weight: 500;
      `;
      alertDiv.textContent = '💾 Session expirée. Vos modifications sont sauvegardées !';
      document.body.appendChild(alertDiv);
      
      // Rediriger après 2 secondes pour que l'utilisateur voie le message
      setTimeout(() => {
        window.location.href = '/';
      }, 2000);
    } else {
      // Pas de données non sauvegardées, redirection immédiate
      window.location.href = '/';
    }
    
    return true;
  }
  return false;
}

/**
 * Wrapper pour les appels API qui gère automatiquement les erreurs d'auth
 */
export async function withAuthErrorHandling<T>(
  apiCall: () => Promise<T>,
  fallbackValue?: T
): Promise<T | undefined> {
  try {
    return await apiCall();
  } catch (error) {
    if (handleAuthError(error)) {
      // Redirection en cours, retourner undefined ou fallback
      return fallbackValue;
    }
    // Re-throw l'erreur si ce n'est pas une erreur d'auth
    throw error;
  }
}
