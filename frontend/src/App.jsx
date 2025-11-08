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
  const [efficiency, setEfficiency] = useState(null);
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
    if (!projectId) {
      console.error('No project ID provided');
      return;
    }
    
    try {
      setIsLoading(true);
      // First verify project exists
      try {
        await projectsAPI.get(projectId);
      } catch (error) {
        console.error('Project not found, retrying...', error);
        // Retry after a short delay
        setTimeout(() => {
          loadProjectFiles(projectId);
        }, 1000);
        return;
      }
      
      const data = await projectsAPI.getFiles(projectId);
      setProjectFiles(data.files);
      setPreviewUrl(projectsAPI.getPreviewUrl(projectId));
    } catch (error) {
      console.error('Error loading project files:', error);
      // Retry once after delay
      if (projectId) {
        setTimeout(() => {
          loadProjectFiles(projectId);
        }, 2000);
      }
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
          
          case 'conversation':
            // User just wants to chat or get ideas
            setThinkingMessage('');
            setIsLoading(false);
            // Add conversation message to chat
            setDescription(streamData.message || 'How can I help you create a webpage?');
            break;
          
          case 'todo_typing':
            // Update typing todo item
            setTodoList(prev => {
              const existing = prev.find(t => t.id === streamData.todo_id);
              if (existing) {
                return prev.map(t => 
                  t.id === streamData.todo_id 
                    ? { ...t, task: streamData.partial_task }
                    : t
                );
              } else {
                return [...prev, { id: streamData.todo_id, task: streamData.partial_task, completed: false }];
              }
            });
            break;
          
          case 'todo_item':
            // Add complete todo item
            setTodoList(prev => {
              const existing = prev.find(t => t.id === streamData.todo.id);
              if (existing) {
                return prev.map(t => 
                  t.id === streamData.todo.id ? streamData.todo : t
                );
              } else {
                return [...prev, streamData.todo];
              }
            });
            break;
          
          case 'todo_complete':
            // All todos generated
            break;
          
          case 'description':
            // Set description
            setDescription(streamData.description);
            break;
          
          case 'project_created':
            // Project created - set project and load files after a delay
            setCurrentProject({ id: streamData.project_id });
            // Wait a bit for database to be ready
            setTimeout(() => {
              loadProjectFiles(streamData.project_id);
            }, 500);
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
          
          case 'code_generated':
            // Code has been generated and saved
            if (currentProject?.id) {
              // Reload files to show the generated code
              setTimeout(() => {
                loadProjectFiles(currentProject.id);
              }, 500);
            }
            break;
          
          case 'complete':
            // All done
            setCurrentProject({ id: streamData.project_id });
            setTodoList(streamData.todo_list || []);
            setDescription(streamData.description || '');
            setRemainingTokens(streamData.remaining_tokens);
            setEfficiency({
              saved: streamData.efficiency_saved || 0,
              percent: streamData.efficiency_percent || 0
            });
            setThinkingMessage('');
            setIsLoading(false);
            
            // Load project files after a short delay to ensure files are saved
            setTimeout(() => {
              loadProjectFiles(streamData.project_id);
            }, 500);
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
            efficiency={efficiency}
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
