import React from 'react';
import './Sidebar.css';

interface SidebarProps {
  onNewNote: () => void;
  onShowAllNotes: () => void;
  onManageContacts?: () => void;
  activeView?: 'all' | 'filtered';
}

const Sidebar: React.FC<SidebarProps> = ({ onNewNote, onShowAllNotes, onManageContacts, activeView = 'all' }) => {
  return (
    <div className="sidebar">
      <div className="sidebar-top">
        {/* Logo */}
        <div className="sidebar-logo">
          <div className="logo-placeholder">LOGO</div>
        </div>

        {/* Bouton Nouvelle note */}
        <button className="sidebar-button new-note-button" onClick={onNewNote}>
          <span className="button-icon">+</span>
        </button>

        {/* Bouton Toutes mes notes */}
        <button 
          className={`sidebar-button all-notes-button ${activeView === 'all' ? 'active' : ''}`}
          onClick={onShowAllNotes}
        >
          <span className="button-icon">📋</span>
        </button>
      </div>

      <div className="sidebar-bottom">
        {/* Bouton Contacts */}
        <button 
          className="sidebar-button contacts-button" 
          onClick={onManageContacts}
          title="Gérer mes contacts"
        >
          <span className="button-icon">👥</span>
        </button>

        {/* Bouton Profil */}
        <button className="sidebar-button profile-button" title="Mon profil">
          <span className="button-icon">M</span>
        </button>

        {/* Bouton Paramètres */}
        <button className="sidebar-button settings-button" title="Paramètres">
          <span className="button-icon">⚙️</span>
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
