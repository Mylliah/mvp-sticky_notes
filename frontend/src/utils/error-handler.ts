/**
 * Utilitaire pour gérer les messages d'erreur HTTP de manière plus explicite
 */

export interface ErrorResponse {
  message: string;
  action?: string;
  canRetry?: boolean;
}

export function getErrorMessage(error: any): ErrorResponse {
  // Si c'est une Error JavaScript simple (lancée par nos services)
  if (error instanceof Error && !(error as any).response) {
    const message = error.message;
    
    // Messages spécifiques du backend
    if (message.includes('Assignment already exists')) {
      return {
        message: 'Cette note est déjà assignée à ce contact.',
        action: 'Choisissez un autre contact ou modifiez l\'assignation existante.',
        canRetry: false
      };
    }
    
    if (message.includes('User is not in your contacts')) {
      return {
        message: 'Cet utilisateur n\'est pas dans vos contacts.',
        action: 'Ajoutez-le d\'abord à vos contacts avant d\'assigner une note.',
        canRetry: false
      };
    }
    
    if (message.includes('contact has not added you back')) {
      return {
        message: 'Ce contact ne vous a pas encore ajouté.',
        action: 'Attendez que le contact accepte votre demande.',
        canRetry: false
      };
    }
    
    if (message.includes('Only the creator can assign')) {
      return {
        message: 'Seul le créateur de la note peut l\'assigner.',
        action: 'Vous ne pouvez pas assigner cette note.',
        canRetry: false
      };
    }
    
    if (message.includes('Note not found')) {
      return {
        message: 'Cette note n\'existe pas ou a été supprimée.',
        action: 'Actualisez la page pour voir les dernières données.',
        canRetry: false
      };
    }
    
    // Erreur réseau (fetch failed)
    if (message.includes('Failed to fetch') || message.includes('Network')) {
      return {
        message: 'Impossible de se connecter au serveur. Vérifiez votre connexion internet.',
        action: 'Veuillez réessayer dans quelques instants.',
        canRetry: true
      };
    }
    
    // Autres erreurs
    return {
      message: message,
      action: 'Si le problème persiste, contactez le support.',
      canRetry: false
    };
  }

  // Erreur réseau (pas de réponse du serveur) - ancien format
  if (!error.response) {
    return {
      message: 'Impossible de se connecter au serveur. Vérifiez votre connexion internet.',
      action: 'Veuillez réessayer dans quelques instants.',
      canRetry: true
    };
  }

  const status = error.response?.status;
  const data = error.response?.data;

  switch (status) {
    case 400:
      return {
        message: data?.error || 'Requête invalide. Vérifiez les informations saisies.',
        action: 'Corrigez les données et réessayez.',
        canRetry: false
      };

    case 401:
      return {
        message: 'Votre session a expiré.',
        action: 'Vous allez être redirigé vers la page de connexion...',
        canRetry: false
      };

    case 403:
      return {
        message: 'Vous n\'avez pas la permission d\'effectuer cette action.',
        action: 'Contactez un administrateur si nécessaire.',
        canRetry: false
      };

    case 404:
      return {
        message: data?.error || 'La ressource demandée n\'existe pas ou a été supprimée.',
        action: 'Actualisez la page pour voir les dernières données.',
        canRetry: false
      };

    case 409:
      return {
        message: data?.error || 'Conflit : la ressource a été modifiée par quelqu\'un d\'autre.',
        action: 'Actualisez la page et réessayez.',
        canRetry: true
      };

    case 422:
      return {
        message: data?.error || 'Données invalides.',
        action: 'Vérifiez les informations saisies.',
        canRetry: false
      };

    case 429:
      return {
        message: 'Trop de requêtes. Ralentissez un peu !',
        action: 'Attendez quelques secondes avant de réessayer.',
        canRetry: true
      };

    case 500:
      return {
        message: 'Erreur interne du serveur.',
        action: 'Nos équipes ont été notifiées. Réessayez dans quelques instants.',
        canRetry: true
      };

    case 502:
    case 503:
    case 504:
      return {
        message: 'Le serveur est temporairement indisponible.',
        action: 'Réessayez dans quelques instants.',
        canRetry: true
      };

    default:
      return {
        message: data?.error || `Erreur ${status} : ${error.message}`,
        action: 'Si le problème persiste, contactez le support.',
        canRetry: true
      };
  }
}

/**
 * Formater le message d'erreur pour l'affichage
 */
export function formatErrorMessage(errorResponse: ErrorResponse): string {
  let message = errorResponse.message;
  if (errorResponse.action) {
    message += `\n${errorResponse.action}`;
  }
  return message;
}
