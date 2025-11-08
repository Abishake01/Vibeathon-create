import React, { useState, useRef, useEffect } from 'react';
import './ChatPanel.css';

const ChatPanel = ({ onSendMessage, isLoading, todoList = [], description = '', remainingTokens = null, tokenLimit = null, thinkingMessage = '', efficiency = null, aiProvider, onProviderChange }) => {
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
    if (description) {
      // Update or add AI message with description
      setMessages(prev => {
        const lastMessage = prev[prev.length - 1];
        if (lastMessage && lastMessage.type === 'ai' && lastMessage.isStreaming) {
          // Update existing streaming message
          return prev.map((msg, idx) => 
            idx === prev.length - 1 
              ? { ...msg, content: description, isStreaming: false }
              : msg
          );
        } else if (lastMessage && lastMessage.type === 'ai' && !lastMessage.content) {
          // Update empty AI message
          return prev.map((msg, idx) => 
            idx === prev.length - 1 
              ? { ...msg, content: description }
              : msg
          );
        } else {
          // Add new message
          return [...prev, {
            type: 'ai',
            content: description,
            isStreaming: false
          }];
        }
      });
    }
  }, [description]);

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
                  {!msg.content && !msg.todoList && <span className="thinking-dots">...</span>}
                </div>
                {msg.content && <div className="ai-text">{msg.content}</div>}
                {todoList && todoList.length > 0 && (
                  <div className="todo-list">
                    <div className="todo-header">
                      <span>{todoList.length} actions taken</span>
                      <span className="todo-toggle">▼</span>
                    </div>
                    <ul className="todo-items">
                      {todoList.map((todo) => (
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
        <div style={{ display: 'flex', gap: '8px', marginBottom: '8px', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <label style={{ fontSize: '12px', color: '#666' }}>AI Provider:</label>
            <select 
              value={aiProvider} 
              onChange={(e) => onProviderChange && onProviderChange(e.target.value)}
              disabled={isLoading}
              style={{ 
                padding: '4px 8px', 
                borderRadius: '4px', 
                border: '1px solid #ddd',
                fontSize: '12px',
                cursor: isLoading ? 'not-allowed' : 'pointer',
                backgroundColor: '#1f1f1e'
              }}
            >
              <option value="groq">Groq</option>
              <option value="openai">OpenAI</option>
              <option value="ollama">Ollama</option>
            </select>
          </div>
          {tokenLimit !== null && (
            <div style={{ fontSize: '12px', color: '#666' }}>
              Tokens: {remainingTokens !== null ? remainingTokens.toLocaleString() : 'N/A'} / {tokenLimit.toLocaleString()}
            </div>
          )}
        </div>
        <form onSubmit={handleSubmit} className="chat-input-form">
          <div className="input-actions">
           
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
