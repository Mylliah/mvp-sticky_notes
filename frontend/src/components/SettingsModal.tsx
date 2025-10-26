import { useState } from 'react';
import './SettingsModal.css';

interface SettingsModalProps {
  onClose: () => void;
  onLogout: () => void;
  darkMode: boolean;
  onToggleDarkMode: () => void;
}

export default function SettingsModal({ 
  onClose, 
  onLogout, 
  darkMode, 
  onToggleDarkMode 
}: SettingsModalProps) {
  const [notificationsEnabled, setNotificationsEnabled] = useState(() => {
    const saved = localStorage.getItem('notificationsEnabled');
    return saved ? JSON.parse(saved) : true;
  });

  const [soundEnabled, setSoundEnabled] = useState(() => {
    const saved = localStorage.getItem('soundEnabled');
    return saved ? JSON.parse(saved) : false;
  });

  const handleToggleNotifications = () => {
    const newValue = !notificationsEnabled;
    setNotificationsEnabled(newValue);
    localStorage.setItem('notificationsEnabled', JSON.stringify(newValue));
  };

  const handleToggleSound = () => {
    const newValue = !soundEnabled;
    setSoundEnabled(newValue);
    localStorage.setItem('soundEnabled', JSON.stringify(newValue));
  };

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const handleLogout = () => {
    if (window.confirm('Êtes-vous sûr de vouloir vous déconnecter ?')) {
      onLogout();
    }
  };

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="modal-content settings-modal">
        <div className="modal-header">
          <h2>⚙️ Paramètres</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">
          {/* Section Apparence */}
          <div className="settings-section">
            <h3>🎨 Apparence</h3>
            
            <div className="setting-item">
              <div className="setting-info">
                <strong>Mode sombre</strong>
                <p>Utiliser le thème sombre pour réduire la fatigue oculaire</p>
              </div>
              <label className="toggle-switch">
                <input
                  type="checkbox"
                  checked={darkMode}
                  onChange={onToggleDarkMode}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>
          </div>

          {/* Section Notifications */}
          <div className="settings-section">
            <h3>🔔 Notifications</h3>
            
            <div className="setting-item">
              <div className="setting-info">
                <strong>Activer les notifications</strong>
                <p>Recevoir des notifications pour les nouvelles assignations</p>
              </div>
              <label className="toggle-switch">
                <input
                  type="checkbox"
                  checked={notificationsEnabled}
                  onChange={handleToggleNotifications}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>

            <div className="setting-item">
              <div className="setting-info">
                <strong>Sons</strong>
                <p>Jouer un son lors des notifications</p>
              </div>
              <label className="toggle-switch">
                <input
                  type="checkbox"
                  checked={soundEnabled}
                  onChange={handleToggleSound}
                  disabled={!notificationsEnabled}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>
          </div>

          {/* Section Compte */}
          <div className="settings-section">
            <h3>👤 Compte</h3>
            
            <div className="setting-item">
              <div className="setting-info">
                <strong>Déconnexion</strong>
                <p>Se déconnecter de votre compte</p>
              </div>
              <button className="logout-btn-settings" onClick={handleLogout}>
                ⏻ Déconnexion
              </button>
            </div>
          </div>

          {/* Section À propos */}
          <div className="settings-section about-section">
            <h3>ℹ️ À propos</h3>
            <div className="about-info">
              <p><strong>Sticky Notes MVP</strong></p>
              <p>Version 1.0.0</p>
              <p className="copyright">© 2025 - Tous droits réservés</p>
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn-secondary" onClick={onClose}>
            Fermer
          </button>
        </div>
      </div>
    </div>
  );
}
