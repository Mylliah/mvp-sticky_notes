import React from 'react';
import './Sidebar.css';
import myLogo from '../assets/logo_TNote.png';
import newNoteIcon from '../assets/new_note.png';
import allNotesIcon from '../assets/all_sticky_notes.png';
import archiveIcon from '../assets/archives.png';
import contactsIcon from '../assets/contacts.png';
import profileIcon from '../assets/profil_.png';
import settingsIcon from '../assets/settings.png';

interface SidebarProps {
  onNewNote: () => void;
  onShowAllNotes: () => void;
  onManageContacts?: () => void;
  onShowArchive?: () => void;
  onShowProfile?: () => void;
  onShowSettings?: () => void;
  activeView?: 'all' | 'filtered' | 'archive';
}

const Sidebar: React.FC<SidebarProps> = ({ 
  onNewNote, 
  onShowAllNotes, 
  onManageContacts, 
  onShowArchive, 
  onShowProfile,
  onShowSettings,
  activeView = 'all' 
}) => {
  return (
    <div className="sidebar">
      <div className="sidebar-top">
        {/* Logo personnalisé*/}
        <div className="sidebar-logo">
          <img 
            src={myLogo} 
            alt="TNote Logo" 
            className="sidebar-logo-img" 
          />
        </div>

        {/* Bouton Nouvelle note */}
        <button className="sidebar-button new-note-button" onClick={onNewNote}>
          <img src={newNoteIcon} alt="Nouvelle note" className="button-icon-img" />
        </button>

        {/* Bouton Toutes mes notes */}
        <button 
          className={`sidebar-button all-notes-button ${activeView === 'all' ? 'active' : ''}`}
          onClick={onShowAllNotes}
        >
          <img src={allNotesIcon} alt="Toutes mes notes" className="button-icon-img" />
        </button>

        {/* Bouton Archive */}
        <button 
          className={`sidebar-button archive-button ${activeView === 'archive' ? 'active' : ''}`}
          onClick={onShowArchive}
          title="Notes sans assignation"
        >
          <img src={archiveIcon} alt="Archive" className="button-icon-img" />
        </button>
      </div>

      <div className="sidebar-bottom">
        {/* Bouton Contacts */}
        <button 
          className="sidebar-button contacts-button" 
          onClick={onManageContacts}
          title="Gérer mes contacts"
        >
          <img src={contactsIcon} alt="Contacts" className="button-icon-img" />
        </button>

        {/* Bouton Profil */}
        <button className="sidebar-button profile-button" title="Mon profil" onClick={onShowProfile}>
          <img src={profileIcon} alt="Profil" className="button-icon-img" />
        </button>

        {/* Bouton Paramètres */}
        <button className="sidebar-button settings-button" title="Paramètres" onClick={onShowSettings}>
          <img src={settingsIcon} alt="Paramètres" className="button-icon-img" />
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
