# Target Chatbot Frontend

Modern React-based UI for the Target Chatbot with WebSocket communication and image upload support.

## Features

- ✅ Real-time chat via WebSocket
- ✅ Image file uploads (drag & drop support)
- ✅ Responsive design
- ✅ Connection status indicator
- ✅ Automatic reconnection
- ✅ Beautiful gradient UI
- ✅ Message timestamps
- ✅ Loading states

## Installation

### Prerequisites
- Node.js 14+ or later
- npm or yarn

### Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Or with yarn
yarn install
```

## Running the Frontend

### Development Mode (with Vite)
```bash
npm run dev
```
This will start the development server at `http://localhost:5173`

### Build for Production
```bash
npm run build
```

### Preview Built App
```bash
npm run preview
```

## File Structure

```
frontend/
├── index.html                 # Main HTML file
├── app.jsx                    # Main React component
├── websocket-service.js       # WebSocket communication service
├── image-handler.js           # Image upload and validation
├── styles.css                 # Application styling
├── package.json              # Dependencies
└── README.md                 # This file
```

## Configuration

### WebSocket URL

By default, the frontend connects to `ws://localhost:8001/ws`. To change this:

1. Open `app.jsx`
2. Find the line: `const wsRef = useRef(null);`
3. Change the WebSocket URL in `useEffect`:

```javascript
wsRef.current = new WebSocketService('ws://your-server:port/ws');
```

## Features Explanation

### Image Upload

1. **Click Button**: Click the 🖼️ button to select images
2. **Drag & Drop**: Drag images onto the chat window to upload
3. **Preview**: Selected images show as thumbnails
4. **Remove**: Click ✕ button on thumbnail to remove image

### Message Format

Messages are sent as JSON with the following structure:

```json
{
    "type": "message",
    "content": "Your message text",
    "timestamp": "2024-03-21T12:00:00Z",
    "image": "base64-encoded-image-data"
}
```

### WebSocket Connection

- **Automatic Connection**: Connects on app load
- **Reconnection**: Auto-reconnects with exponential backoff
- **Connection Status**: Visual indicator in header
- **Message Queue**: Messages sent while disconnected are queued

## API Integration

The WebSocket service handles:
- Connection establishment
- Message sending/receiving
- Error handling
- Automatic reconnection with exponential backoff
- Message queueing during disconnection

## Styling

The UI uses a modern gradient design with:
- Animated message transitions
- Responsive layout (works on mobile)
- Accessibility considerations
- Dark mode compatible

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Modern mobile browsers

## Troubleshooting

### Cannot Connect to Backend

1. Ensure backend WebSocket server is running on `ws://localhost:8001`
2. Check firewall settings
3. Verify CORS is configured if needed
4. Check browser console for error messages

### Images Not Uploading

1. Check file size (max 5MB)
2. Verify file format (JPEG, PNG, GIF, WebP)
3. Check browser console for errors
4. Ensure WebSocket connection is active

### Performance Issues

1. Clear chat history for long sessions
2. Reduce maximum image size
3. Use production build: `npm run build`

## Development

### Adding New Features

1. Create new components in separate files
2. Import into `app.jsx`
3. Update styles in `styles.css` if needed
4. Test in development mode

### Code Organization

- `app.jsx`: Main React component with state management
- `websocket-service.js`: WebSocket communication logic
- `image-handler.js`: Image file handling and validation
- `styles.css`: All styling

## Building for Production

```bash
npm run build-vite
# or
npm run build
```

Output files will be in the `dist/` folder. Deploy these files to your web server.

## License

Part of the Target Chatbot suite for Red Team Testing.
