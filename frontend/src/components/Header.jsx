import React from 'react';

const Header = ({ projectName = 'New Project', isLocked = false, onRefresh, currentView = 'preview', onViewChange }) => {
  return (
    <header className="flex items-center justify-between px-5 py-3 bg-[#1a1a1a] border-b border-[#2a2a2a] h-14 sticky top-0 z-[100]">
      <div className="flex items-center gap-3 flex-1"> 
        <span className="text-white text-sm font-medium">{projectName}</span>
        {isLocked && <span className="ml-2 text-sm opacity-70">🔒</span>}
      </div>

      <div className="flex items-center gap-3 flex-1 justify-center">
        <div className="flex gap-1">
          <button 
            className={`w-8 h-8 border-none bg-transparent text-[#888] cursor-pointer rounded-md flex items-center justify-center transition-all hover:bg-[#2a2a2a] hover:text-white ${currentView === 'preview' ? 'text-blue-500 bg-[#1e3a5f]' : ''}`} 
            title="Preview"
            onClick={() => onViewChange && onViewChange('preview')}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
              <circle cx="12" cy="12" r="3"></circle>
            </svg>
          </button>
          <button 
            className={`w-8 h-8 border-none bg-transparent text-[#888] cursor-pointer rounded-md flex items-center justify-center transition-all hover:bg-[#2a2a2a] hover:text-white ${currentView === 'code' ? 'text-blue-500 bg-[#1e3a5f]' : ''}`} 
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

      <div className="flex items-center gap-3 flex-1 justify-end">
        <button className="w-8 h-8 border-none bg-transparent text-[#888] cursor-pointer rounded-md flex items-center justify-center transition-all hover:bg-[#2a2a2a] hover:text-white" title="Refresh" onClick={onRefresh || (() => {})}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="23 4 23 10 17 10"></polyline>
            <polyline points="1 20 1 14 7 14"></polyline>
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
          </svg>
        </button>
        <button 
          className="w-8 h-8 border-none bg-transparent text-[#888] cursor-pointer rounded-md flex items-center justify-center transition-all hover:bg-[#2a2a2a] hover:text-white" 
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

