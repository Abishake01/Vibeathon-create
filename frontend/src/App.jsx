import React, { useState, useEffect, useCallback } from 'react';
import './App.css';
import Header from './components/Header';
import ProjectList from './components/ProjectList';
import CodeEditor from './components/CodeEditor';
import PreviewPanel from './components/PreviewPanel';
import { projectsAPI, authAPI } from './services/api';

function App() {
  const [projects, setProjects] = useState([]);
  const [currentProject, setCurrentProject] = useState(null);
  const [projectFiles, setProjectFiles] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [autoSaveTimer, setAutoSaveTimer] = useState(null);

  useEffect(() => {
    // Auto-authenticate
    if (!authAPI.isAuthenticated()) {
      handleAutoAuth();
    } else {
      loadProjects();
    }
  }, []);

  useEffect(() => {
    if (currentProject) {
      loadProjectFiles(currentProject.id);
    }
  }, [currentProject]);

  const handleAutoAuth = async () => {
    try {
      const demoEmail = 'demo@example.com';
      const demoPassword = 'demo123456';
      
      try {
        await authAPI.login(demoEmail, demoPassword);
      } catch (error) {
        if (error.response?.status === 401 || error.response?.status === 404) {
          await authAPI.register(demoEmail, 'demo', demoPassword);
          await authAPI.login(demoEmail, demoPassword);
        }
      }
      loadProjects();
    } catch (error) {
      console.error('Auth error:', error);
    }
  };

  const loadProjects = async () => {
    try {
      const data = await projectsAPI.list();
      setProjects(data);
    } catch (error) {
      console.error('Error loading projects:', error);
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

  const handleCreateProject = async (name) => {
    try {
      const project = await projectsAPI.create(name, '');
      setProjects(prev => [...prev, project]);
      setCurrentProject(project);
      await loadProjectFiles(project.id);
    } catch (error) {
      console.error('Error creating project:', error);
      alert('Failed to create project');
    }
  };

  const handleSelectProject = async (projectId) => {
    const project = projects.find(p => p.id === projectId);
    if (project) {
      setCurrentProject(project);
    }
  };

  const handleFileChange = useCallback((filename, content) => {
    if (!currentProject) return;

    // Clear existing timer
    if (autoSaveTimer) {
      clearTimeout(autoSaveTimer);
    }

    // Update local state immediately
    setProjectFiles(prev => {
      const updated = prev.map(file => 
        file.filename === filename ? { ...file, content } : file
      );
      return updated;
    });

    // Auto-save after 1 second of inactivity
    const timer = setTimeout(async () => {
      try {
        await projectsAPI.updateFile(currentProject.id, filename, content);
        // Refresh preview
        if (previewUrl) {
          setPreviewUrl(prev => prev + '?t=' + Date.now());
        }
      } catch (error) {
        console.error('Error saving file:', error);
      }
    }, 1000);

    setAutoSaveTimer(timer);
  }, [currentProject, autoSaveTimer, previewUrl]);

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
      />
      <div className="app-content">
        <div className="sidebar">
          <ProjectList
            projects={projects}
            onSelectProject={handleSelectProject}
            onCreateProject={handleCreateProject}
            currentProjectId={currentProject?.id}
          />
        </div>
        <div className="editor-panel">
          {currentProject ? (
            <CodeEditor
              projectId={currentProject.id}
              onFileChange={handleFileChange}
              initialFiles={projectFiles}
            />
          ) : (
            <div className="empty-editor">
              <div className="empty-logo">b</div>
              <p>Select a project or create a new one to start coding</p>
            </div>
          )}
        </div>
        <div className="preview-panel">
          <PreviewPanel 
            projectId={currentProject?.id}
            previewUrl={previewUrl}
            isLoading={isLoading}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
