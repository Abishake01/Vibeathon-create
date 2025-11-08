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
  const [thinkingMessage, setThinkingMessage] = useState('');

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
    setCurrentProject(null);
    setProjectFiles(null);
    setPreviewUrl(null);

    try {
      // Use streaming API
      await aiAPI.createProject(message, null, (streamData) => {
        switch (streamData.type) {
          case 'thinking':
            // Show thinking message
            setThinkingMessage(streamData.message);
            break;
          
          case 'todo_item':
            // Add todo item one by one (typing effect)
            setTodoList(prev => [...prev, streamData.todo]);
            break;
          
          case 'todo_complete':
            // All todos generated
            break;
          
          case 'description':
            // Set description
            setDescription(streamData.description);
            break;
          
          case 'project_created':
            // Project created
            setCurrentProject({ id: streamData.project_id });
            break;
          
          case 'task_start':
            // Task started
            break;
          
          case 'task_complete':
            // Mark task as completed
            setTodoList(prev => 
              prev.map(todo => 
                todo.id === streamData.task_id 
                  ? { ...todo, completed: true }
                  : todo
              )
            );
            break;
          
          case 'complete':
            // All done
            setCurrentProject({ id: streamData.project_id });
            setTodoList(streamData.todo_list || []);
            setDescription(streamData.description || '');
            setRemainingTokens(streamData.remaining_tokens);
            setThinkingMessage('');
            setIsLoading(false);
            
            // Load project files
            loadProjectFiles(streamData.project_id);
            break;
          
          case 'error':
            alert(`Error: ${streamData.message}`);
            setIsLoading(false);
            break;
        }
      });
    } catch (error) {
      console.error('Error creating project:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to create project';
      alert(`Error: ${errorMessage}\n\nPlease ensure:\n1. Backend server is running\n2. Groq API key is configured in backend/.env`);
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
            thinkingMessage={thinkingMessage}
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
