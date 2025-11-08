import React, { useState, useRef, useEffect } from 'react';
import './ChatPanel.css';

const ChatPanel = ({ onSendMessage, isLoading, todoList = [], description = '', remainingTokens = null, thinkingMessage = '' }) => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const messagesEndRef = useRef(null);
  const [currentThinking, setCurrentThinking] = useState('');

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading, todoList]);

  useEffect(() => {
    if (description && todoList.length > 0) {
      // Update or add AI message with description and todos
      setMessages(prev => {
        const lastMessage = prev[prev.length - 1];
        if (lastMessage && lastMessage.type === 'ai' && lastMessage.isStreaming) {
          // Update existing streaming message
          return prev.map((msg, idx) => 
            idx === prev.length - 1 
              ? { ...msg, content: description, todoList: todoList, isStreaming: false }
              : msg
          );
        } else {
          // Add new message
          return [...prev, {
            type: 'ai',
            content: description,
            todoList: todoList,
            isStreaming: false
          }];
        }
      });
    }
  }, [description, todoList]);

  useEffect(() => {
    setCurrentThinking(thinkingMessage);
  }, [thinkingMessage]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = {
      type: 'user',
      content: input.trim(),
    };

    setMessages(prev => [...prev, userMessage]);
    onSendMessage(input.trim());
    setInput('');
  };

  return (
    <div className="chat-panel">
      <div className="chat-header">
        <div className="chat-header-left">
          <span className="logo-small">b</span>
          <span className="separator">/</span>
          <span className="avatar-small">A</span>
          <span className="separator">/</span>
          <span className="project-title">Coffee Shop Page</span>
        </div>
        <button className="eye-icon-btn" title="Preview">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
            <circle cx="12" cy="12" r="3"></circle>
          </svg>
        </button>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="suggestion-chip-container">
            <button
              className="suggestion-chip"
              onClick={() => {
                setMessages([{ type: 'user', content: 'create a coffee shop page' }]);
                onSendMessage('create a coffee shop page');
              }}
              disabled={isLoading}
            >
              create a coffee shop page
            </button>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.type}`}>
            {msg.type === 'user' ? (
              <div className="message-content user-message">{msg.content}</div>
            ) : (
              <div className="message-content ai-message">
                <div className="ai-name">
                  <strong>bolt</strong>
                  <span className="thinking-dots">...</span>
                </div>
                <div className="ai-text">{msg.content}</div>
                {msg.todoList && msg.todoList.length > 0 && (
                  <div className="todo-list">
                    <div className="todo-header">
                      <span>{msg.todoList.length} actions taken</span>
                      <span className="todo-toggle">▼</span>
                    </div>
                    <ul className="todo-items">
                      {msg.todoList.map((todo) => (
                        <li key={todo.id} className={`todo-item ${todo.completed ? 'completed' : ''}`}>
                          <span className="todo-checkbox">
                            {todo.completed ? '✓' : '○'}
                          </span>
                          <span className="todo-text">{todo.task}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="message ai">
            <div className="message-content ai-message">
              <div className="ai-name">
                <strong>bolt</strong>
                <span className="thinking-dots">...</span>
              </div>
              {currentThinking ? (
                <div className="thinking-indicator">
                  <span className="brain-icon">🧠</span>
                  {currentThinking}
                </div>
              ) : (
                <div className="thinking-indicator">
                  <span className="brain-icon">🧠</span>
                  Thinking...
                </div>
              )}
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-container">
        {remainingTokens !== null && (
          <div className="token-info">
            Remaining tokens: {remainingTokens.toLocaleString()}
          </div>
        )}
        <form onSubmit={handleSubmit} className="chat-input-form">
          <div className="input-actions">
            <button type="button" className="action-btn">Let's build</button>
            <button type="button" className="action-btn icon-only">+</button>
            <button type="button" className="action-btn">Select</button>
            <button type="button" className="action-btn">
              <span className="lightbulb-icon">💡</span>
              Plan
            </button>
            <button type="button" className="action-btn toggle-btn"></button>
          </div>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Let's build"
            className="chat-input"
            disabled={isLoading}
          />
        </form>
      </div>
    </div>
  );
};

export default ChatPanel;
