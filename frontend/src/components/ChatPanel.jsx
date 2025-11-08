import React, { useState, useRef, useEffect } from 'react';
import './ChatPanel.css';

const ChatPanel = ({ onSendMessage, isLoading }) => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([
    {
      type: 'suggestion',
      content: 'create a coffee shop page',
    },
  ]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = {
      type: 'user',
      content: input.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);
    onSendMessage(input.trim());
    setInput('');
  };

  const handleSuggestionClick = (suggestion) => {
    if (isLoading) return;
    setMessages((prev) => [
      ...prev,
      { type: 'user', content: suggestion },
    ]);
    onSendMessage(suggestion);
  };


  return (
    <div className="chat-panel">
      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.type}`}>
            {msg.type === 'suggestion' ? (
              <button
                className="suggestion-chip"
                onClick={() => handleSuggestionClick(msg.content)}
                disabled={isLoading}
              >
                {msg.content}
              </button>
            ) : msg.type === 'user' ? (
              <div className="message-content">{msg.content}</div>
            ) : (
              <div className="message-content">
                <strong>bolt</strong>
                <span className="thinking-dots">...</span>
                <br />
                {msg.content}
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="message ai">
            <div className="message-content">
              <strong>bolt</strong>
              <span className="thinking-dots">...</span>
              <br />
              <div className="thinking-indicator">
                <span className="brain-icon">🧠</span>
                Thinking...
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-container">
        <form onSubmit={handleSubmit} className="chat-input-form">
          <div className="input-actions">
            <button type="button" className="action-btn">
              Let's build
            </button>
            <button type="button" className="action-btn icon-only">+</button>
            <button type="button" className="action-btn">Select</button>
            <button type="button" className="action-btn">Plan</button>
            <button type="button" className="action-btn toggle-btn"></button>
          </div>
          <div className="input-wrapper">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              className="chat-input"
              disabled={isLoading}
            />
          </div>
        </form>
      </div>
    </div>
  );
};

export default ChatPanel;

