import React, { useState, useEffect } from 'react';
import './App.css';
import Header from './components/Header';
import ChatPanel from './components/ChatPanel';
import CodeView from './components/CodeView';
import PreviewPanel from './components/PreviewPanel';
import { projectsAPI, authAPI, aiAPI } from './services/api';

function App() {
  const [currentView, setCurrentView] = useState('preview'); // 'preview' or 'code'
  const [isLoading, setIsLoading] = useState(false);
  const [currentProject, setCurrentProject] = useState(null);
  const [projectFiles, setProjectFiles] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [todoList, setTodoList] = useState([]);
  const [description, setDescription] = useState('');
  const [remainingTokens, setRemainingTokens] = useState(null);

  useEffect(() => {
    // Load token info (no auth needed)
    loadTokenInfo();
  }, []);

  useEffect(() => {
    if (currentProject) {
      loadProjectFiles(currentProject.id);
    }
  }, [currentProject]);


  const loadTokenInfo = async () => {
    try {
      const tokenInfo = await aiAPI.getTokens();
      setRemainingTokens(tokenInfo.remaining);
    } catch (error) {
      console.error('Error loading token info:', error);
    }
  };

  const loadProjectFiles = async (projectId) => {
    try {
      setIsLoading(true);
      const data = await projectsAPI.getFiles(projectId);
      setProjectFiles(data.files);
      setPreviewUrl(projectsAPI.getPreviewUrl(projectId));
    } catch (error) {
      console.error('Error loading project files:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (message) => {
    if (!message.trim()) return;

    setIsLoading(true);
    setDescription('');
    setTodoList([]);

    try {
      // Create project with AI
      const response = await aiAPI.createProject(message);
      
      setCurrentProject({ id: response.project_id });
      setTodoList(response.todo_list || []);
      setDescription(response.description || '');
      setRemainingTokens(response.remaining_tokens);
      
      // Load project files
      await loadProjectFiles(response.project_id);
      
      // Update token info
      await loadTokenInfo();
    } catch (error) {
      console.error('Error creating project:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to create project';
      alert(`Error: ${errorMessage}\n\nPlease ensure:\n1. Backend server is running\n2. Groq API key is configured in backend/.env`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefresh = () => {
    if (currentProject && previewUrl) {
      setPreviewUrl(prev => prev.split('?')[0] + '?t=' + Date.now());
    }
  };

  return (
    <div className="app">
      <Header 
        projectName={currentProject?.name || 'New Project'} 
        onRefresh={handleRefresh}
        currentView={currentView}
        onViewChange={setCurrentView}
      />
      <div className="app-content">
        <div className="left-panel">
          <ChatPanel 
            onSendMessage={handleSendMessage} 
            isLoading={isLoading}
            todoList={todoList}
            description={description}
            remainingTokens={remainingTokens}
          />
        </div>
        <div className="right-panel">
          {currentView === 'preview' ? (
            <PreviewPanel 
              projectId={currentProject?.id}
              previewUrl={previewUrl}
              isLoading={isLoading}
            />
          ) : (
            <CodeView
              projectFiles={projectFiles}
              isLoading={isLoading}
            />
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
