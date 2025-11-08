import React, { useState, useEffect, useRef } from 'react';
import './CodeEditor.css';

const CodeEditor = ({ projectId, onFileChange, initialFiles = null }) => {
  const [activeTab, setActiveTab] = useState('index.html');
  const [files, setFiles] = useState({
    'index.html': '',
    'style.css': '',
    'script.js': '',
  });
  const [hasChanges, setHasChanges] = useState(false);
  const textareaRef = useRef(null);

  useEffect(() => {
    if (initialFiles) {
      const fileMap = {};
      initialFiles.forEach(file => {
        fileMap[file.filename] = file.content || '';
      });
      setFiles(fileMap);
    }
  }, [initialFiles]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [files[activeTab], activeTab]);

  const handleChange = (value) => {
    setFiles(prev => ({
      ...prev,
      [activeTab]: value
    }));
    setHasChanges(true);
    if (onFileChange) {
      onFileChange(activeTab, value);
    }
  };

  const tabs = [
    { id: 'index.html', label: 'HTML', icon: '📄' },
    { id: 'style.css', label: 'CSS', icon: '🎨' },
    { id: 'script.js', label: 'JS', icon: '⚡' },
  ];

  return (
    <div className="code-editor">
      <div className="editor-tabs">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <span className="tab-icon">{tab.icon}</span>
            <span className="tab-label">{tab.label}</span>
            {hasChanges && activeTab === tab.id && (
              <span className="unsaved-indicator">●</span>
            )}
          </button>
        ))}
      </div>
      <div className="editor-content">
        <textarea
          ref={textareaRef}
          className="code-textarea"
          value={files[activeTab] || ''}
          onChange={(e) => handleChange(e.target.value)}
          placeholder={`Enter your ${activeTab.split('.')[1].toUpperCase()} code here...`}
          spellCheck={false}
        />
      </div>
      <div className="editor-footer">
        <span className="file-info">{activeTab}</span>
        {hasChanges && (
          <span className="changes-indicator">Unsaved changes</span>
        )}
      </div>
    </div>
  );
};

export default CodeEditor;

