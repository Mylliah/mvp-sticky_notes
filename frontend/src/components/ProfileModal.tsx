import { useState, FormEvent } from 'react';
import { authService } from '../services/auth.service';
import { userService } from '../services/user.service';
import { useToast } from './ToastContainer';
import { getErrorMessage, formatErrorMessage } from '../utils/error-handler';
import './ProfileModal.css';

interface ProfileModalProps {
  onClose: () => void;
}

export default function ProfileModal({ onClose }: ProfileModalProps) {
  const currentUser = authService.getCurrentUser();
  const { addToast } = useToast();
  
  const [username, setUsername] = useState(currentUser?.username || '');
  const [email, setEmail] = useState(currentUser?.email || '');
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'profile' | 'password'>('profile');

  const handleUpdateProfile = async (e: FormEvent) => {
    e.preventDefault();
    
    if (!username.trim() || !email.trim()) {
      addToast({
        message: 'Le nom d\'utilisateur et l\'email sont obligatoires',
        type: 'error',
        duration: 3000,
      });
      return;
    }

    setIsLoading(true);

    try {
      await userService.updateUser(currentUser!.id, {
        username: username.trim(),
        email: email.trim(),
      });

      // Mettre à jour le localStorage
      const updatedUser = {
        ...currentUser!,
        username: username.trim(),
        email: email.trim(),
      };
      localStorage.setItem('user', JSON.stringify(updatedUser));

      addToast({
        message: 'Profil mis à jour avec succès ✓',
        type: 'success',
        duration: 3000,
      });

      // Recharger la page pour mettre à jour l'affichage
      setTimeout(() => {
        window.location.reload();
      }, 1000);
    } catch (err) {
      const errorResponse = getErrorMessage(err);
      addToast({
        message: formatErrorMessage(errorResponse),
        type: 'error',
        duration: 5000,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleChangePassword = async (e: FormEvent) => {
    e.preventDefault();

    if (!currentPassword || !newPassword || !confirmPassword) {
      addToast({
        message: 'Veuillez remplir tous les champs',
        type: 'error',
        duration: 3000,
      });
      return;
    }

    if (newPassword !== confirmPassword) {
      addToast({
        message: 'Les nouveaux mots de passe ne correspondent pas',
        type: 'error',
        duration: 3000,
      });
      return;
    }

    if (newPassword.length < 8) {
      addToast({
        message: 'Le mot de passe doit contenir au moins 8 caractères',
        type: 'error',
        duration: 3000,
      });
      return;
    }

    setIsLoading(true);

    try {
      await userService.updateUser(currentUser!.id, {
        current_password: currentPassword,
        new_password: newPassword,
      });

      addToast({
        message: 'Mot de passe modifié avec succès ✓',
        type: 'success',
        duration: 3000,
      });

      // Reset les champs
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
      
      setActiveTab('profile');
    } catch (err) {
      const errorResponse = getErrorMessage(err);
      addToast({
        message: formatErrorMessage(errorResponse),
        type: 'error',
        duration: 5000,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="modal-content profile-modal">
        <div className="modal-header">
          <h2>👤 Mon Profil</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <div className="modal-tabs">
          <button
            className={`tab-btn ${activeTab === 'profile' ? 'active' : ''}`}
            onClick={() => setActiveTab('profile')}
          >
            📝 Informations
          </button>
          <button
            className={`tab-btn ${activeTab === 'password' ? 'active' : ''}`}
            onClick={() => setActiveTab('password')}
          >
            🔐 Mot de passe
          </button>
        </div>

        <div className="modal-body">
          {activeTab === 'profile' ? (
            <form onSubmit={handleUpdateProfile} className="profile-form">
              <div className="form-section">
                <h3>Informations personnelles</h3>
                
                <div className="form-group">
                  <label htmlFor="username">Nom d'utilisateur</label>
                  <input
                    id="username"
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    disabled={isLoading}
                    placeholder="Votre nom d'utilisateur"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="email">Email</label>
                  <input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    disabled={isLoading}
                    placeholder="votre@email.com"
                  />
                </div>

                <div className="info-box">
                  <p>📊 <strong>Rôle :</strong> {currentUser?.role || 'user'}</p>
                  <p>📅 <strong>Membre depuis :</strong> {new Date().toLocaleDateString('fr-FR')}</p>
                </div>
              </div>

              <div className="form-actions">
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={onClose}
                  disabled={isLoading}
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="btn-primary"
                  disabled={isLoading}
                >
                  {isLoading ? 'Enregistrement...' : 'Enregistrer'}
                </button>
              </div>
            </form>
          ) : (
            <form onSubmit={handleChangePassword} className="password-form">
              <div className="form-section">
                <h3>Modifier le mot de passe</h3>
                
                <div className="form-group">
                  <label htmlFor="currentPassword">Mot de passe actuel</label>
                  <input
                    id="currentPassword"
                    type="password"
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                    disabled={isLoading}
                    placeholder="••••••••"
                    autoComplete="current-password"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="newPassword">Nouveau mot de passe</label>
                  <input
                    id="newPassword"
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    disabled={isLoading}
                    placeholder="••••••••"
                    autoComplete="new-password"
                  />
                  <small>Minimum 8 caractères</small>
                </div>

                <div className="form-group">
                  <label htmlFor="confirmPassword">Confirmer le nouveau mot de passe</label>
                  <input
                    id="confirmPassword"
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    disabled={isLoading}
                    placeholder="••••••••"
                    autoComplete="new-password"
                  />
                </div>
              </div>

              <div className="form-actions">
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={onClose}
                  disabled={isLoading}
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="btn-primary"
                  disabled={isLoading}
                >
                  {isLoading ? 'Modification...' : 'Changer le mot de passe'}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
