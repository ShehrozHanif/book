import React, { useState, useRef, useEffect } from 'react';
import styles from './styles.module.css';

const API_URL = process.env.NODE_ENV === 'production'
  ? '/api' // In production, use relative path or configure your API URL
  : 'http://localhost:8000';

function ChatMessage({ message, isUser }) {
  return (
    <div className={`${styles.message} ${isUser ? styles.userMessage : styles.botMessage}`}>
      <div className={styles.messageContent}>
        {message.text}
        {message.citations && message.citations.length > 0 && (
          <div className={styles.citations}>
            <strong>Sources:</strong>
            {message.citations.map((citation, idx) => (
              <div key={idx} className={styles.citation}>
                • {citation.chapter} — {citation.section}
              </div>
            ))}
          </div>
        )}
        {message.warning && (
          <div className={styles.warning}>
            ⚠️ {message.warning}
          </div>
        )}
      </div>
    </div>
  );
}

export default function ChatBot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      text: "Hello! I'm the Physical AI Textbook assistant. Ask me any question about the textbook content, and I'll provide answers with citations. I only know what's in the textbook—I won't make things up!",
      isUser: false,
      citations: [],
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState('unknown'); // 'unknown', 'online', 'offline'
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Check API health on mount
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch(`${API_URL}/health`);
        if (response.ok) {
          setApiStatus('online');
        } else {
          setApiStatus('offline');
        }
      } catch (error) {
        setApiStatus('offline');
      }
    };
    checkHealth();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');

    // Add user message
    setMessages(prev => [...prev, { text: userMessage, isUser: true }]);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_URL}/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: userMessage }),
      });

      if (!response.ok) {
        throw new Error('API request failed');
      }

      const data = await response.json();

      setMessages(prev => [...prev, {
        text: data.answer,
        isUser: false,
        citations: data.citations || [],
        warning: data.warning,
        responseType: data.response_type,
      }]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        text: "I'm sorry, I couldn't connect to the backend service. Please make sure the RAG API is running (uvicorn api:app --reload --port 8000).",
        isUser: false,
        citations: [],
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <>
      {/* Chat Toggle Button */}
      <button
        className={styles.chatToggle}
        onClick={() => setIsOpen(!isOpen)}
        aria-label={isOpen ? 'Close chat' : 'Open chat'}
      >
        {isOpen ? '✕' : '💬'}
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className={styles.chatWindow}>
          <div className={styles.chatHeader}>
            <span className={styles.chatTitle}>Physical AI Assistant</span>
            <span className={`${styles.statusDot} ${styles[apiStatus]}`}
                  title={`API Status: ${apiStatus}`} />
          </div>

          <div className={styles.messagesContainer}>
            {messages.map((msg, idx) => (
              <ChatMessage key={idx} message={msg} isUser={msg.isUser} />
            ))}
            {isLoading && (
              <div className={styles.loadingIndicator}>
                <span className={styles.dot}></span>
                <span className={styles.dot}></span>
                <span className={styles.dot}></span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={handleSubmit} className={styles.inputContainer}>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about Physical AI, ROS 2, simulation..."
              className={styles.input}
              disabled={isLoading}
            />
            <button
              type="submit"
              className={styles.sendButton}
              disabled={isLoading || !input.trim()}
            >
              Send
            </button>
          </form>
        </div>
      )}
    </>
  );
}
