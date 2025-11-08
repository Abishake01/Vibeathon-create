import React from 'react';
import './Header.css';

const Header = ({ projectName = 'New Project', isLocked = false, onRefresh, currentView = 'preview', onViewChange }) => {
  return (
    <header className="app-header">
      <div className="header-left">
        <div className="logo">b</div>
        <div className="separator"></div>
        <div className="avatar-icon">A</div>
        <div className="separator"></div>
        <div className="diamond-icon">◆</div>
        <span className="project-name">{projectName}</span>
        {isLocked && <span className="lock-icon">🔒</span>}
      </div>

      <div className="header-center">
        <div className="icon-group">
          <button 
            className={`icon-btn ${currentView === 'preview' ? 'active' : ''}`} 
            title="Preview"
            onClick={() => onViewChange && onViewChange('preview')}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
              <circle cx="12" cy="12" r="3"></circle>
            </svg>
          </button>
          <button 
            className={`icon-btn ${currentView === 'code' ? 'active' : ''}`} 
            title="Code"
            onClick={() => onViewChange && onViewChange('code')}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="16 18 22 12 16 6"></polyline>
              <polyline points="8 6 2 12 8 18"></polyline>
            </svg>
          </button>
 
        </div>
      </div>

      <div className="header-right">
        <button className="icon-btn" title="Refresh" onClick={onRefresh || (() => {})}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="23 4 23 10 17 10"></polyline>
            <polyline points="1 20 1 14 7 14"></polyline>
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
          </svg>
        </button>
        <button 
          className="icon-btn" 
          title="Expand Fullscreen"
          onClick={() => {
            if (!document.fullscreenElement) {
              document.documentElement.requestFullscreen().catch(err => {
                console.error('Error attempting to enable fullscreen:', err);
              });
            } else {
              document.exitFullscreen();
            }
          }}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"></path>
          </svg>
        </button>
         
      
      </div>
    </header>
  );
};

export default Header;

