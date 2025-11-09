import React, { useState, useEffect, useRef } from 'react';
import Header from '../components/Header';
import ChatPanel from '../components/ChatPanel';
import CodeView from '../components/CodeView';
import PreviewPanel from '../components/PreviewPanel';
import { projectsAPI, aiAPI } from '../services/api';
import { useLocation, useNavigate } from 'react-router-dom';

function Build() {
  const location = useLocation();
  const navigate = useNavigate();
  const [currentView, setCurrentView] = useState('preview'); // 'preview' or 'code'
  const [isLoading, setIsLoading] = useState(false);
  const [currentProject, setCurrentProject] = useState(null);
  const [projectFiles, setProjectFiles] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [todoList, setTodoList] = useState([]);
  const [description, setDescription] = useState('');
  const [remainingTokens, setRemainingTokens] = useState(null);
  const [tokenLimit, setTokenLimit] = useState(null);
  const [efficiency, setEfficiency] = useState(null);
  const [thinkingMessage, setThinkingMessage] = useState('');
  const [aiProvider, setAiProvider] = useState('groq');
  const [activeCodeFile, setActiveCodeFile] = useState('index.html');
  const loadingFilesRef = useRef(new Set()); // Track which project IDs are currently loading

  // Get initial prompt from location state (passed from Chatbot page)
  useEffect(() => {
    const initialPrompt = location.state?.prompt;
    if (initialPrompt) {
      // Auto-start building with the prompt from Chatbot page
      handleSendMessage(initialPrompt);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.state?.prompt]);

  useEffect(() => {
    // Load token info (no auth needed)
    loadTokenInfo();
  }, []);

  const loadTokenInfo = async () => {
    try {
      const tokenInfo = await aiAPI.getTokens();
      setRemainingTokens(tokenInfo.remaining);
      setTokenLimit(tokenInfo.limit);
    } catch (error) {
      console.error('Error loading token info:', error);
    }
  };

  const loadProjectFiles = async (projectId, retryCount = 0) => {
    if (!projectId) {
      console.error('No project ID provided');
      return;
    }
    
    // Prevent duplicate loading calls for the same project
    if (loadingFilesRef.current.has(projectId) && retryCount === 0) {
      console.log(`Already loading files for project ${projectId}, skipping...`);
      return;
    }
    
    // Maximum 3 retries with exponential backoff
    const MAX_RETRIES = 3;
    if (retryCount >= MAX_RETRIES) {
      console.error('Max retries reached for loading project files');
      loadingFilesRef.current.delete(projectId);
      setIsLoading(false);
      return;
    }
    
    // Mark as loading
    if (retryCount === 0) {
      loadingFilesRef.current.add(projectId);
    }
    
    try {
      // Don't set loading if we're retrying (to avoid UI flicker)
      if (retryCount === 0) {
        setIsLoading(true);
      }
      
      // Try to get files directly - no need to check if project exists first
      const data = await projectsAPI.getFiles(projectId);
      setProjectFiles(data.files);
      setPreviewUrl(projectsAPI.getPreviewUrl(projectId));
      setIsLoading(false);
      loadingFilesRef.current.delete(projectId);
    } catch (error) {
      // Only log and retry if it's a 404 or network error
      if (error.response?.status === 404 || error.code === 'ERR_NETWORK') {
        if (retryCount < MAX_RETRIES - 1) {
          console.log(`Project files not ready yet (attempt ${retryCount + 1}/${MAX_RETRIES}), retrying...`);
          // Retry with exponential backoff: 1s, 2s, 4s
          const delay = Math.pow(2, retryCount) * 1000;
          setTimeout(() => {
            loadProjectFiles(projectId, retryCount + 1);
          }, delay);
        } else {
          // Last retry failed
          console.error('Max retries reached for loading project files');
          loadingFilesRef.current.delete(projectId);
          setIsLoading(false);
        }
      } else {
        // Other errors - don't retry
        console.error('Error loading project files:', error);
        loadingFilesRef.current.delete(projectId);
        setIsLoading(false);
      }
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
      await aiAPI.createProject(message, null, aiProvider, (streamData) => {
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
            // Project created - set project but don't load files yet (wait for code generation)
            setCurrentProject({ id: streamData.project_id });
            break;
          
          case 'task_start':
            // Task started - mark as generating
            setTodoList(prev => 
              prev.map(todo => 
                todo.id === streamData.task_id 
                  ? { ...todo, generating: true, completed: false }
                  : todo
              )
            );
            break;
          
          case 'task_complete':
            // Mark task as completed - remove generating flag
            setTodoList(prev => 
              prev.map(todo => 
                todo.id === streamData.task_id 
                  ? { ...todo, completed: true, generating: false }
                  : { ...todo, generating: false }
              )
            );
            break;
          
          case 'code_start':
            // Code generation started for a file - initialize empty file
            setProjectFiles(prev => {
              const files = prev || [];
              const existing = files.find(f => f.filename === streamData.file);
              if (!existing) {
                return [...files, { filename: streamData.file, content: '' }];
              }
              return files.map(f => 
                f.filename === streamData.file 
                  ? { ...f, content: '' } 
                  : f
              );
            });
            // Auto-switch to the file being generated in CodeView
            setActiveCodeFile(streamData.file);
            // Ensure CodeView is visible (switch to code view)
            setCurrentView('code');
            break;
          
          case 'code_line':
            // Stream code line by line
            setProjectFiles(prev => {
              const files = prev || [];
              const file = files.find(f => f.filename === streamData.file);
              if (file) {
                return files.map(f => 
                  f.filename === streamData.file 
                    ? { ...f, content: f.content + streamData.line } 
                    : f
                );
              } else {
                return [...files, { filename: streamData.file, content: streamData.line }];
              }
            });
            break;
          
          case 'code_complete':
            // Code generation completed for a file - ensure full content is set
            if (streamData.content) {
              setProjectFiles(prev => {
                const files = prev || [];
                const file = files.find(f => f.filename === streamData.file);
                if (file) {
                  return files.map(f => 
                    f.filename === streamData.file 
                      ? { ...f, content: streamData.content } 
                      : f
                  );
                } else {
                  return [...files, { filename: streamData.file, content: streamData.content }];
                }
              });
              // Ensure CodeView is showing this file
              setActiveCodeFile(streamData.file);
              // Force a small delay to ensure React has rendered the content
              setTimeout(() => {
                // Content should now be visible in CodeView
                console.log(`Code complete for ${streamData.file}, content length: ${streamData.content.length}`);
              }, 100);
            }
            break;
          
          case 'code_generated':
            // Code has been generated and saved - now load files
            if (streamData.project_id || currentProject?.id) {
              const projectId = streamData.project_id || currentProject.id;
              // Wait longer to ensure files are saved and project is committed
              setTimeout(() => {
                loadProjectFiles(projectId);
              }, 1500);
            }
            break;
          
          case 'complete':
            // All done
            setCurrentProject({ id: streamData.project_id });
            setTodoList(streamData.todo_list || []);
            setDescription(streamData.description || '');
            setRemainingTokens(streamData.remaining_tokens);
            setTokenLimit(streamData.token_limit);
            setThinkingMessage('');
            setIsLoading(false);
            
            // Load project files after a delay to ensure files are saved and project is committed
            setTimeout(() => {
              loadProjectFiles(streamData.project_id);
            }, 2000);
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
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-[#0a0a0a] text-white">
      <Header 
        projectName={currentProject?.name || 'New Project'} 
        onRefresh={handleRefresh}
        currentView={currentView}
        onViewChange={setCurrentView}
      />
      <div className="flex flex-1 overflow-hidden">
        <div className="w-1/3 min-w-[350px] max-w-[450px] flex flex-col overflow-hidden border-r border-[#2a2a2a]">
          <ChatPanel 
            onSendMessage={handleSendMessage} 
            isLoading={isLoading}
            todoList={todoList}
            description={description}
            remainingTokens={remainingTokens}
            tokenLimit={tokenLimit}
            thinkingMessage={thinkingMessage}
            efficiency={efficiency}
            aiProvider={aiProvider}
            onProviderChange={setAiProvider}
          />
        </div>
        <div className="flex-1 flex flex-col overflow-hidden">
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
              activeFile={activeCodeFile}
              onFileChange={setActiveCodeFile}
            />
          )}
        </div>
      </div>
    </div>
  );
}

export default Build;

