import React, { useState, useEffect } from 'react';
import './PreviewPanel.css';

const PreviewPanel = ({ projectId, previewUrl, isLoading }) => {
  const [iframeKey, setIframeKey] = useState(0);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (previewUrl) {
      setIframeKey((prev) => prev + 1);
      setError(null);
    }
  }, [previewUrl]);

  const handleIframeError = () => {
    setError('Failed to load preview. Please try refreshing.');
  };

  return (
    <div className="preview-panel">
      {isLoading ? (
        <div className="preview-placeholder">
          <div className="loading-spinner"></div>
          <p className="placeholder-text">Creating project...</p>
        </div>
      ) : error ? (
        <div className="preview-placeholder">
          <div className="placeholder-logo">⚠</div>
          <p className="placeholder-text">{error}</p>
          <button onClick={() => window.location.reload()} style={{ marginTop: '10px', padding: '8px 16px', cursor: 'pointer' }}>
            Refresh
          </button>
        </div>
      ) : previewUrl ? (
        <iframe
          key={iframeKey}
          src={previewUrl}
          className="preview-iframe"
          title="Preview"
          sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
          onError={handleIframeError}
          onLoad={() => setError(null)}
        />
      ) : (
        <div className="preview-placeholder">
           
          <p className="placeholder-text">Your preview will appear here</p>
        </div>
      )}
    
    </div>
  );
};

export default PreviewPanel;

