import React, { useState, useEffect } from 'react';
import './CodeView.css';

const CodeView = ({ projectFiles = null, isLoading = false, activeFile = null, onFileChange = null }) => {
  const [expandedFiles, setExpandedFiles] = useState(['index.html', 'style.css', 'script.js']);
  const [selectedFile, setSelectedFile] = useState(activeFile || 'index.html');
  
  // Update selected file when activeFile prop changes (when code generation starts)
  useEffect(() => {
    if (activeFile) {
      setSelectedFile(activeFile);
    }
  }, [activeFile]);

  // Ensure we always have file structure even if projectFiles is null
  const files = projectFiles && projectFiles.length > 0 ? projectFiles : [
    { filename: 'index.html', content: '' },
    { filename: 'style.css', content: '' },
    { filename: 'script.js', content: '' }
  ];

  const handleFileClick = (filename) => {
    setSelectedFile(filename);
    if (onFileChange) {
      onFileChange(filename);
    }
    if (!expandedFiles.includes(filename)) {
      setExpandedFiles(prev => [...prev, filename]);
    }
  };

  const selectedFileContent = files.find(f => f.filename === selectedFile)?.content || '';

  return (
    <div className="code-view">
      <div className="code-view-header">
        <div className="view-tabs">
          <button className="view-tab active">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="16 18 22 12 16 6"></polyline>
              <polyline points="8 6 2 12 8 18"></polyline>
            </svg>
            Code
          </button>
        </div>
        <div className="code-view-actions">
          <button className="icon-btn-small" title="Refresh">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="23 4 23 10 17 10"></polyline>
              <polyline points="1 20 1 14 7 14"></polyline>
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
            </svg>
          </button>
          <button className="icon-btn-small" title="External">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
              <polyline points="15 3 21 3 21 9"></polyline>
              <line x1="10" y1="14" x2="21" y2="3"></line>
            </svg>
          </button>
          <button className="icon-btn-small" title="Fullscreen">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"></path>
            </svg>
          </button>
        </div>
      </div>

      <div className="code-view-content">
        <>
          <div className="file-tree">
              <div className="file-tree-header">Project</div>
              <div className="file-tree-items">
                {files.map((file) => (
                  <div key={file.filename} className="file-tree-item">
                    <button
                      className={`file-tree-toggle ${selectedFile === file.filename ? 'active' : ''}`}
                      onClick={() => handleFileClick(file.filename)}
                    >
                      <span className="file-icon">
                        {file.filename.endsWith('.html') && '📄'}
                        {file.filename.endsWith('.css') && '🎨'}
                        {file.filename.endsWith('.js') && '⚡'}
                      </span>
                      <span className="file-name">{file.filename}</span>
                    </button>
                  </div>
                ))}
              </div>
            </div>
            <div className="code-editor-area">
              <div className="code-tabs">
                {files.map((file) => (
                  <button
                    key={file.filename}
                    className={`code-tab ${selectedFile === file.filename ? 'active' : ''}`}
                    onClick={() => handleFileClick(file.filename)}
                  >
                    {file.filename}
                  </button>
                ))}
              </div>
              <div className="code-display">
                <pre className="code-content">
                  <code>{selectedFileContent || (isLoading ? 'Generating...' : `// ${selectedFile} will appear here`)}</code>
                </pre>
              </div>
            </div>
          </>
      </div>
    </div>
  );
};

export default CodeView;

