import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Add welcome message on component mount
  useEffect(() => {
    setMessages([
      {
        id: 1,
        text: "Hello! I'm your E-commerce Customer Support Chatbot. I can help you with:",
        isUser: false,
        data: null
      },
      {
        id: 2,
        text: "• Top selling products\n• Order status\n• Product stock levels\n\nTry asking me something!",
        isUser: false,
        data: null
      }
    ]);
  }, []);

  const exampleQueries = [
    "What are the top 5 most sold products?",
    "Show me the status of order ID 12345",
    "How many Classic T-Shirts are left in stock?"
  ];

  const handleExampleClick = (query) => {
    setInputValue(query);
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      text: inputValue,
      isUser: true,
      data: null
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await axios.get(`/chatbot/query?query=${encodeURIComponent(inputValue)}`);
      
      const botMessage = {
        id: Date.now() + 1,
        text: response.data.response,
        isUser: false,
        data: response.data.data
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        text: "Sorry, I'm having trouble connecting to the server. Please try again later.",
        isUser: false,
        data: null
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const renderData = (data) => {
    if (!data) return null;

    if (Array.isArray(data)) {
      return (
        <div className="data-display">
          <table className="data-table">
            <thead>
              <tr>
                {Object.keys(data[0] || {}).map(key => (
                  <th key={key}>{key.replace(/_/g, ' ').toUpperCase()}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((item, index) => (
                <tr key={index}>
                  {Object.values(item).map((value, i) => (
                    <td key={i}>{value}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    }

    if (typeof data === 'object') {
      return (
        <div className="data-display">
          <table className="data-table">
            <tbody>
              {Object.entries(data).map(([key, value]) => (
                <tr key={key}>
                  <th>{key.replace(/_/g, ' ').toUpperCase()}</th>
                  <td>{value}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    }

    return null;
  };

  return (
    <div className="app">
      <header className="header">
        <h1>🛍️ E-commerce Customer Support Chatbot</h1>
      </header>
      
      <div className="chat-container">
        <div className="example-queries">
          <h3>💡 Try these example queries:</h3>
          <ul>
            {exampleQueries.map((query, index) => (
              <li key={index} onClick={() => handleExampleClick(query)}>
                {query}
              </li>
            ))}
          </ul>
        </div>

        <div className="messages">
          {messages.map((message) => (
            <div key={message.id}>
              <div className={`message ${message.isUser ? 'user-message' : 'bot-message'}`}>
                {message.text.split('\n').map((line, index) => (
                  <div key={index}>{line}</div>
                ))}
              </div>
              {renderData(message.data)}
            </div>
          ))}
          
          {isLoading && (
            <div className="message bot-message">
              <div className="loading">
                <div className="spinner"></div>
                Thinking...
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        <div className="input-container">
          <input
            type="text"
            className="input-field"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me about products, orders, or stock levels..."
            disabled={isLoading}
          />
          <button
            className="send-button"
            onClick={handleSendMessage}
            disabled={isLoading || !inputValue.trim()}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

export default App; 