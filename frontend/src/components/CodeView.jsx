import React, { useState, useEffect } from 'react';

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
    <div className="flex flex-col h-full bg-[#0a0a0a]">
      <div className="flex items-center justify-between px-4 py-3 bg-[#1a1a1a] border-b border-[#2a2a2a]">
        <div className="flex gap-1">
          <button className="flex items-center gap-1.5 px-3 py-1.5 bg-[#1e3a5f] rounded-md text-blue-500 text-[13px]">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="16 18 22 12 16 6"></polyline>
              <polyline points="8 6 2 12 8 18"></polyline>
            </svg>
            Code
          </button>
        </div>
        <div className="flex gap-2">
          <button className="w-7 h-7 border-none bg-transparent text-[#888] cursor-pointer rounded flex items-center justify-center transition-all hover:bg-[#2a2a2a] hover:text-white" title="Refresh">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="23 4 23 10 17 10"></polyline>
              <polyline points="1 20 1 14 7 14"></polyline>
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
            </svg>
          </button>
          <button className="w-7 h-7 border-none bg-transparent text-[#888] cursor-pointer rounded flex items-center justify-center transition-all hover:bg-[#2a2a2a] hover:text-white" title="External">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
              <polyline points="15 3 21 3 21 9"></polyline>
              <line x1="10" y1="14" x2="21" y2="3"></line>
            </svg>
          </button>
          <button className="w-7 h-7 border-none bg-transparent text-[#888] cursor-pointer rounded flex items-center justify-center transition-all hover:bg-[#2a2a2a] hover:text-white" title="Fullscreen">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"></path>
            </svg>
          </button>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        <div className="w-[200px] bg-[#1a1a1a] border-r border-[#2a2a2a] overflow-y-auto p-3">
          <div className="text-[#888] text-[11px] font-semibold uppercase mb-2 px-2">Project</div>
          <div className="flex flex-col gap-0.5">
            {files.map((file) => (
              <div key={file.filename} className="w-full">
                <button
                  className={`w-full flex items-center gap-2 px-2 py-1.5 bg-transparent border-none rounded text-[#ccc] text-[13px] cursor-pointer text-left transition-colors hover:bg-[#2a2a2a] ${selectedFile === file.filename ? 'bg-[#1e3a5f] text-blue-500' : ''}`}
                  onClick={() => handleFileClick(file.filename)}
                >
                  <span className="text-sm">
                    {file.filename.endsWith('.html') && '📄'}
                    {file.filename.endsWith('.css') && '🎨'}
                    {file.filename.endsWith('.js') && '⚡'}
                  </span>
                  <span className="flex-1">{file.filename}</span>
                </button>
              </div>
            ))}
          </div>
        </div>
        <div className="flex-1 flex flex-col overflow-hidden">
          <div className="flex bg-[#1a1a1a] border-b border-[#2a2a2a] px-2 overflow-x-auto">
            {files.map((file) => (
              <button
                key={file.filename}
                className={`px-4 py-2 bg-transparent border-none border-b-2 border-transparent text-[#888] text-xs cursor-pointer whitespace-nowrap transition-all hover:text-white hover:bg-[#2a2a2a] ${selectedFile === file.filename ? 'text-white border-b-blue-500 bg-[#0a0a0a]' : ''}`}
                onClick={() => handleFileClick(file.filename)}
              >
                {file.filename}
              </button>
            ))}
          </div>
          <div className="flex-1 overflow-auto bg-[#0a0a0a]">
            <pre className="m-0 p-4 text-[#d4d4d4] font-mono text-[13px] leading-relaxed whitespace-pre-wrap break-words">
              <code className="font-mono text-inherit">{selectedFileContent || (isLoading ? 'Generating...' : `// ${selectedFile} will appear here`)}</code>
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CodeView;
