import React, { useState, useEffect } from 'react';
import './App.css';
import Header from './components/Header';
import ChatPanel from './components/ChatPanel';
import PreviewPanel from './components/PreviewPanel';
import { projectsAPI, authAPI } from './services/api';

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [currentProject, setCurrentProject] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);

  useEffect(() => {
    // Check if user is authenticated, if not, auto-register/login
    if (!authAPI.isAuthenticated()) {
      // Auto-register a demo user (in production, implement proper auth flow)
      handleAutoAuth();
    }
  }, []);

  const handleAutoAuth = async () => {
    try {
      // Try to login with demo credentials
      const demoEmail = 'demo@example.com';
      const demoPassword = 'demo123456';
      
      try {
        await authAPI.login(demoEmail, demoPassword);
      } catch (error) {
        // If login fails, register the user
        if (error.response?.status === 401 || error.response?.status === 404) {
          await authAPI.register(demoEmail, 'demo', demoPassword);
          await authAPI.login(demoEmail, demoPassword);
        }
      }
    } catch (error) {
      console.error('Auth error:', error);
    }
  };

  const handleSendMessage = async (message) => {
    if (!message.trim()) return;

    setIsLoading(true);

    try {
      // Extract project name from message or use default
      const projectName = message.length > 30 
        ? message.substring(0, 30) + '...' 
        : message;

      // Create project via API
      const response = await projectsAPI.create(
        projectName,
        message,
        `Generated from prompt: ${message}`
      );

      setCurrentProject(response.project_id);
      setPreviewUrl(projectsAPI.getPreviewUrl(response.project_id));
    } catch (error) {
      console.error('Error creating project:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to create project';
      alert(`Error: ${errorMessage}\n\nPlease ensure:\n1. Backend server is running on http://localhost:8000\n2. OpenAI API key is configured in backend/.env`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app">
      <Header projectName={currentProject ? 'Coffee Shop Page' : 'New Project'} />
      <div className="app-content">
        <div className="left-panel">
          <ChatPanel 
            onSendMessage={handleSendMessage} 
            isLoading={isLoading}
          />
        </div>
        <div className="right-panel">
          <PreviewPanel 
            projectId={currentProject}
            previewUrl={previewUrl}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
