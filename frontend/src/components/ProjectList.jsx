import React, { useState, useEffect } from 'react';
import './ProjectList.css';

const ProjectList = ({ projects, onSelectProject, onCreateProject, currentProjectId }) => {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [projectName, setProjectName] = useState('');

  const handleCreate = (e) => {
    e.preventDefault();
    if (projectName.trim()) {
      onCreateProject(projectName.trim());
      setProjectName('');
      setShowCreateForm(false);
    }
  };

  return (
    <div className="project-list">
      <div className="project-list-header">
        <h3>Projects</h3>
        <button
          className="create-btn"
          onClick={() => setShowCreateForm(!showCreateForm)}
          title="Create New Project"
        >
          +
        </button>
      </div>

      {showCreateForm && (
        <form className="create-form" onSubmit={handleCreate}>
          <input
            type="text"
            placeholder="Project name..."
            value={projectName}
            onChange={(e) => setProjectName(e.target.value)}
            className="create-input"
            autoFocus
          />
          <div className="create-form-actions">
            <button type="submit" className="submit-btn">Create</button>
            <button
              type="button"
              className="cancel-btn"
              onClick={() => {
                setShowCreateForm(false);
                setProjectName('');
              }}
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      <div className="projects-container">
        {projects.length === 0 ? (
          <div className="empty-state">
            <p>No projects yet</p>
            <p className="empty-hint">Create a new project to get started</p>
          </div>
        ) : (
          <ul className="projects-list">
            {projects.map((project) => (
              <li
                key={project.id}
                className={`project-item ${currentProjectId === project.id ? 'active' : ''}`}
                onClick={() => onSelectProject(project.id)}
              >
                <div className="project-icon">📁</div>
                <div className="project-info">
                  <div className="project-name">{project.name}</div>
                  {project.description && (
                    <div className="project-description">{project.description}</div>
                  )}
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default ProjectList;

