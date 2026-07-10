import React, { useState, useEffect, useRef, useCallback } from 'react';
import ReactDOM from 'react-dom/client';
import WebSocketService from './websocket-service.js';

const WS_URL = 'ws://localhost:8005/ws';

// Renders message text preserving newlines
function MessageText({ text }) {
    return (
        <span style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
            {text}
        </span>
    );
}

function ChatbotUI() {
    const [messages, setMessages]         = useState([]);
    const [inputText, setInputText]       = useState('');
    const [isConnected, setIsConnected]   = useState(false);
    const [isLoading, setIsLoading]       = useState(false);
    const [statusText, setStatusText]     = useState('Connecting...');
    const [selectedImages, setSelectedImages] = useState([]);
    const [isDragging, setIsDragging]     = useState(false);
    const [errorBanner, setErrorBanner]   = useState('');

    const messagesEndRef = useRef(null);
    const fileInputRef   = useRef(null);
    const wsRef          = useRef(null);
    const containerRef   = useRef(null);

    // ------------------------------------------------------------------ //
    //  WebSocket setup
    // ------------------------------------------------------------------ //
    useEffect(() => {
        const ws = new WebSocketService(WS_URL);
        wsRef.current = ws;

        ws.on('onOpen', () => {
            setIsConnected(true);
            setStatusText('Connected');
            setErrorBanner('');
        });

        ws.on('onClose', () => {
            setIsConnected(false);
            setStatusText('Disconnected — reconnecting…');
        });

        ws.on('onError', () => {
            setStatusText('Connection error');
        });

        ws.on('onMessage', (data) => {
            // Backend sends plain text; websocket-service wraps it as { type: 'response', content }
            const text = data.content ?? data.message ?? data.response ?? JSON.stringify(data);
            setMessages(prev => [...prev, {
                id: Date.now(),
                role: 'assistant',
                text,
                timestamp: new Date(),
            }]);
            setIsLoading(false);
        });

        ws.connect().catch(() => {
            setStatusText('Cannot reach backend');
            setErrorBanner('Cannot connect to chatbot backend at ws://localhost:8005/ws. Make sure the backend is running.');
        });

        return () => ws.disconnect();
    }, []);

    // Auto-scroll on new messages or loading state change
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, isLoading]);

    // ------------------------------------------------------------------ //
    //  Image helpers
    // ------------------------------------------------------------------ //
    const addImageFiles = useCallback((files) => {
        const allowed = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
        Array.from(files).forEach(file => {
            if (!allowed.includes(file.type)) {
                showError(`Unsupported file type: ${file.type}`);
                return;
            }
            if (file.size > 5 * 1024 * 1024) {
                showError('Image must be smaller than 5 MB');
                return;
            }
            const reader = new FileReader();
            reader.onload = (e) => {
                setSelectedImages(prev => [...prev, {
                    id: Date.now() + Math.random(),
                    name: file.name,
                    dataUrl: e.target.result,
                }]);
            };
            reader.readAsDataURL(file);
        });
        // reset input so same file can be re-selected
        if (fileInputRef.current) fileInputRef.current.value = '';
    }, []);

    const removeImage = (id) => setSelectedImages(prev => prev.filter(img => img.id !== id));

    // ------------------------------------------------------------------ //
    //  Drag-and-drop
    // ------------------------------------------------------------------ //
    const onDragOver  = (e) => { e.preventDefault(); setIsDragging(true); };
    const onDragLeave = (e) => { e.preventDefault(); setIsDragging(false); };
    const onDrop      = (e) => {
        e.preventDefault();
        setIsDragging(false);
        if (e.dataTransfer.files.length) addImageFiles(e.dataTransfer.files);
    };

    // ------------------------------------------------------------------ //
    //  Send message
    // ------------------------------------------------------------------ //
    const showError = (msg) => {
        setErrorBanner(msg);
        setTimeout(() => setErrorBanner(''), 4000);
    };

    const sendMessage = (e) => {
        e?.preventDefault();
        const text = inputText.trim();

        if (!text && selectedImages.length === 0) return;

        if (!isConnected) {
            showError('Not connected to chatbot. Please wait…');
            return;
        }

        // Add user message to chat
        setMessages(prev => [...prev, {
            id: Date.now(),
            role: 'user',
            text: text || '(image)',
            images: selectedImages.length > 0 ? [...selectedImages] : null,
            timestamp: new Date(),
        }]);

        // Send to backend — backend reads the 'message' key
        wsRef.current.sendChatMessage(
            text,
            selectedImages.length > 0 ? selectedImages[0].dataUrl : null
        );

        setInputText('');
        setSelectedImages([]);
        setIsLoading(true);
    };

    const onKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    // ------------------------------------------------------------------ //
    //  Render
    // ------------------------------------------------------------------ //
    return (
        <div
            ref={containerRef}
            className="chatbot-container"
            onDragOver={onDragOver}
            onDragLeave={onDragLeave}
            onDrop={onDrop}
        >
            {/* ---- Header ---- */}
            <header className="chat-header">
                <div className="header-title">
                    <span className="header-icon">🛒</span>
                    <div>
                        <h1>E-Commerce Assistant</h1>
                        <p className="header-subtitle">Powered by Azure OpenAI</p>
                    </div>
                </div>
                <div className="connection-status">
                    <div className={`status-dot ${isConnected ? 'connected' : 'disconnected'}`} />
                    <span>{statusText}</span>
                </div>
            </header>

            {/* ---- Error banner ---- */}
            {errorBanner && (
                <div className="error-banner">
                    ⚠️ {errorBanner}
                </div>
            )}

            {/* ---- Messages ---- */}
            <div className="chat-messages" id="chat-messages-container">
                {messages.length === 0 && !isLoading && (
                    <div className="empty-state">
                        <div className="empty-icon">💬</div>
                        <p>How can I help you today?</p>
                        <div className="suggestions">
                            {[
                                'What products do you have?',
                                'Track my order',
                                'What is your return policy?',
                            ].map(s => (
                                <button
                                    key={s}
                                    className="suggestion-chip"
                                    onClick={() => { setInputText(s); }}
                                >
                                    {s}
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {messages.map((msg, index) => (
                    <div 
                        key={msg.id} 
                        className={`message-row ${msg.role}`}
                        id={msg.role === 'assistant' ? `bot-message-${index}` : `user-message-${index}`}
                    >
                        <div className="avatar">
                            {msg.role === 'assistant' ? '🤖' : '👤'}
                        </div>
                        <div className="bubble-group">
                            <div className="bubble" id={msg.role === 'assistant' ? `bot-bubble-${index}` : undefined}>
                                <MessageText text={msg.text} />
                                {msg.images && msg.images.map(img => (
                                    <img
                                        key={img.id}
                                        src={img.dataUrl}
                                        alt={img.name}
                                        className="message-img"
                                    />
                                ))}
                            </div>
                            <time className="timestamp">
                                {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </time>
                        </div>
                    </div>
                ))}

                {/* Typing indicator */}
                {isLoading && (
                    <div className="message-row assistant" id="bot-typing-indicator">
                        <div className="avatar">🤖</div>
                        <div className="bubble-group">
                            <div className="bubble typing-bubble">
                                <span className="dot" /><span className="dot" /><span className="dot" />
                            </div>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* ---- Image previews ---- */}
            {selectedImages.length > 0 && (
                <div className="image-preview-bar">
                    {selectedImages.map(img => (
                        <div key={img.id} className="preview-thumb">
                            <img src={img.dataUrl} alt={img.name} />
                            <button className="remove-thumb" onClick={() => removeImage(img.id)}>✕</button>
                        </div>
                    ))}
                </div>
            )}

            {/* ---- Input ---- */}
            <form className="input-bar" onSubmit={sendMessage}>
                <button
                    type="button"
                    className="attach-btn"
                    id="attach-button"
                    title="Attach image"
                    onClick={() => fileInputRef.current?.click()}
                >
                    📎
                </button>
                <input
                    ref={fileInputRef}
                    id="image-input"
                    type="file"
                    accept="image/*"
                    multiple
                    style={{ display: 'none' }}
                    onChange={(e) => addImageFiles(e.target.files)}
                />
                <textarea
                    id="chat-textarea"
                    className="chat-input"
                    rows={1}
                    placeholder={isConnected ? 'Type a message… (Enter to send)' : 'Waiting for connection…'}
                    value={inputText}
                    disabled={!isConnected}
                    onChange={(e) => setInputText(e.target.value)}
                    onKeyDown={onKeyDown}
                />
                <button
                    type="submit"
                    id="send-button"
                    className="send-btn"
                    disabled={!isConnected || isLoading || (!inputText.trim() && selectedImages.length === 0)}
                    title="Send"
                >
                    ➤
                </button>
            </form>

            {/* Drag overlay */}
            {isDragging && (
                <div className="drag-overlay">
                    <div className="drag-label">📤 Drop images here</div>
                </div>
            )}
        </div>
    );
}

ReactDOM.createRoot(document.getElementById('root')).render(<ChatbotUI />);
