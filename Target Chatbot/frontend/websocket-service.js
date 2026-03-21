/**
 * WebSocket Service for Target Chatbot Communication
 * Handles connection, message sending, and reconnection logic
 */

class WebSocketService {
    constructor(url = 'ws://localhost:8001/ws') {
        this.url = url;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000; // 3 seconds
        this.messageQueue = [];
        this.isConnecting = false;
        this.listeners = {
            onOpen: [],
            onClose: [],
            onError: [],
            onMessage: []
        };
    }

    /**
     * Connect to the WebSocket server
     */
    connect() {
        if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
            return Promise.resolve();
        }

        return new Promise((resolve, reject) => {
            try {
                this.isConnecting = true;
                this.ws = new WebSocket(this.url);

                this.ws.onopen = () => {
                    console.log('✅ WebSocket connected to ' + this.url);
                    this.isConnecting = false;
                    this.reconnectAttempts = 0;

                    // Process queued messages
                    while (this.messageQueue.length > 0) {
                        const message = this.messageQueue.shift();
                        this.send(message);
                    }

                    this.emit('onOpen');
                    resolve();
                };

                this.ws.onmessage = (event) => {
                    // Backend sends plain text responses (not JSON-wrapped)
                    let data;
                    try {
                        data = JSON.parse(event.data);
                    } catch (_) {
                        // Plain text response — wrap it for uniform handling
                        data = { type: 'response', content: event.data };
                    }
                    this.emit('onMessage', data);
                };

                this.ws.onerror = (error) => {
                    console.error('❌ WebSocket error:', error);
                    this.isConnecting = false;
                    this.emit('onError', error);
                    reject(error);
                };

                this.ws.onclose = () => {
                    console.log('⚠️ WebSocket disconnected');
                    this.isConnecting = false;
                    this.emit('onClose');
                    this.attemptReconnect();
                };

                // Timeout for connection
                setTimeout(() => {
                    if (this.isConnecting) {
                        reject(new Error('Connection timeout'));
                    }
                }, 10000);

            } catch (error) {
                this.isConnecting = false;
                console.error('Error creating WebSocket:', error);
                reject(error);
            }
        });
    }

    /**
     * Send a message to the server
     */
    send(message) {
        if (!this.ws) {
            this.messageQueue.push(message);
            this.connect().catch(error => console.error('Failed to connect:', error));
            return;
        }

        if (this.ws.readyState === WebSocket.OPEN) {
            try {
                this.ws.send(JSON.stringify(message));
                console.log('📤 Message sent:', message);
            } catch (error) {
                console.error('Error sending message:', error);
                this.messageQueue.push(message);
            }
        } else if (this.ws.readyState === WebSocket.CONNECTING) {
            this.messageQueue.push(message);
        } else {
            this.messageQueue.push(message);
            this.connect().catch(error => console.error('Failed to reconnect:', error));
        }
    }

    /**
     * Send a chat message with optional image.
     * Backend reads the 'message' key from JSON.
     */
    sendChatMessage(text, imageData = null) {
        const payload = {
            message: text,
            timestamp: new Date().toISOString()
        };
        if (imageData) {
            payload.image = imageData;
        }
        this.send(payload);
    }

    /**
     * Register event listener
     */
    on(event, callback) {
        if (this.listeners[event]) {
            this.listeners[event].push(callback);
        }
    }

    /**
     * Unregister event listener
     */
    off(event, callback) {
        if (this.listeners[event]) {
            this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
        }
    }

    /**
     * Emit event to all listeners
     */
    emit(event, data = null) {
        if (this.listeners[event]) {
            this.listeners[event].forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error('Error in listener:', error);
                }
            });
        }
    }

    /**
     * Attempt to reconnect with exponential backoff
     */
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = this.reconnectDelay * Math.pow(1.5, this.reconnectAttempts - 1);
            console.log(`🔄 Reconnecting in ${delay / 1000}s (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
            setTimeout(() => {
                this.connect().catch(error => console.error('Reconnection failed:', error));
            }, delay);
        } else {
            console.error('❌ Max reconnection attempts reached');
        }
    }

    /**
     * Close the connection
     */
    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }

    /**
     * Check if connected
     */
    isConnected() {
        return this.ws && this.ws.readyState === WebSocket.OPEN;
    }

    /**
     * Get connection state
     */
    getState() {
        if (!this.ws) return 'DISCONNECTED';
        switch (this.ws.readyState) {
            case WebSocket.CONNECTING:
                return 'CONNECTING';
            case WebSocket.OPEN:
                return 'CONNECTED';
            case WebSocket.CLOSING:
                return 'CLOSING';
            case WebSocket.CLOSED:
                return 'DISCONNECTED';
            default:
                return 'UNKNOWN';
        }
    }
}

// Export for use
export default WebSocketService;
