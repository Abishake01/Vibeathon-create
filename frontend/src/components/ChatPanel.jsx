import React, { useState, useRef, useEffect } from 'react';

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
    <div className="flex flex-col h-full bg-[#1e1e1e] border-r border-[#2a2a2a]">
      <div className="flex-1 overflow-y-auto p-5 flex flex-col gap-4">
        {messages.length === 0 && (
          <div className="flex justify-start mb-2">
            <button
              className="bg-[#2a2a2a] border border-[#3a3a3a] rounded-full px-4 py-2 text-white text-sm cursor-pointer transition-all self-start hover:bg-[#3a3a3a] hover:border-[#4a4a4a] disabled:opacity-50 disabled:cursor-not-allowed"
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
          <div key={idx} className={`flex flex-col ${msg.type === 'user' ? 'items-end' : 'items-start'}`}>
            {msg.type === 'user' ? (
              <div className="max-w-[85%] break-words bg-[#2a2a2a] px-3.5 py-2.5 rounded-xl text-white text-sm">{msg.content}</div>
            ) : (
              <div className="max-w-[85%] break-words bg-transparent p-0">
                <div className="text-base font-bold text-white mb-2">
                  <strong>Generate</strong>
                  {!msg.content && !msg.todoList && <span className="ml-1 animate-pulse">...</span>}
                </div>
                {msg.content && <div className="text-[#ccc] text-sm leading-relaxed mb-3">{msg.content}</div>}
                {todoList && todoList.length > 0 && (
                  <div className="mt-3 bg-[#2a2a2a] rounded-lg p-3">
                    <div className="flex items-center justify-between text-[#888] text-xs mb-2 cursor-pointer">
                      <span>{todoList.length} actions taken</span>
                      <span className="text-[10px]">▼</span>
                    </div>
                    <ul className="list-none p-0 m-0">
                      {todoList.map((todo) => (
                        <li key={todo.id} className={`flex items-start gap-2 py-1.5 text-[#ccc] text-[13px] ${todo.completed ? 'text-[#888] line-through' : ''}`}>
                          <span className={`w-[18px] h-[18px] flex items-center justify-center rounded border flex-shrink-0 text-xs ${todo.completed ? 'bg-blue-500 border-blue-500 text-white' : todo.generating ? 'bg-[#1a1a1a] border-blue-500 text-blue-500' : 'bg-[#1a1a1a] border-[#3a3a3a]'}`}>
                            {todo.completed ? '✓' : todo.generating ? (
                              <span className="inline-block animate-spin text-sm">⟳</span>
                            ) : '○'}
                          </span>
                          <span className="flex-1 leading-snug">{todo.task}</span>
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
          <div className="flex flex-col items-start">
            <div className="max-w-[85%] break-words bg-transparent p-0">
              <div className="text-base font-bold text-white mb-2">
                <strong>AIGen</strong>
                <span className="ml-1 animate-pulse">...</span>
              </div>
              {currentThinking ? (
                <div className="flex items-center gap-2 mt-2 text-[#888] text-[13px]">
                  <span className="text-base">🧠</span>
                  {currentThinking}
                </div>
              ) : (
                <div className="flex items-center gap-2 mt-2 text-[#888] text-[13px]">
                  <span className="text-base">🧠</span>
                  Thinking...
                </div>
              )}
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-3 bg-[#1a1a1a] border-t border-[#2a2a2a]">
        <div className="flex gap-2 mb-2 items-center justify-between flex-wrap">
          <div className="flex gap-2 items-center">
            <label className="text-xs text-[#666]">AI Provider:</label>
            <select 
              value={aiProvider} 
              onChange={(e) => onProviderChange && onProviderChange(e.target.value)}
              disabled={isLoading}
              className="px-2 py-1 rounded border border-[#ddd] text-xs cursor-pointer bg-[#1f1f1e] text-white disabled:cursor-not-allowed disabled:opacity-50"
            >
              <option value="ollama">Ollama - FREE</option>
              <option value="groq">Groq</option>
              <option value="openai">OpenAI</option>
            </select>
          </div>
          {tokenLimit !== null && remainingTokens !== null && (
            <div className="text-xs text-[#666] font-medium">
              Tokens: {remainingTokens.toLocaleString()} / {tokenLimit.toLocaleString()}
            </div>
          )}
        </div>
        <form onSubmit={handleSubmit} className="flex flex-col gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Let's build"
            className="w-full bg-[#2a2a2a] border border-[#3a3a3a] rounded-lg px-3.5 py-2.5 text-white text-sm outline-none transition-colors focus:border-blue-500 disabled:opacity-50 disabled:cursor-not-allowed placeholder:text-[#666]"
            disabled={isLoading}
          />
        </form>
      </div>
    </div>
  );
};

export default ChatPanel;
