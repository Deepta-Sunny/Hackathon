# Frontend Architecture - React TypeScript Application

## Overview

The AI Red Teaming Platform frontend is a modern React 19.2.0 application built with TypeScript 5.9.3, Material-UI 7.3.6, and Redux Toolkit 2.11.1. It provides real-time monitoring of attack campaigns through WebSocket integration and interactive visualizations.

---

## Technology Stack

### Core Framework
- **React 19.2.0**: Latest React with concurrent features
- **TypeScript 5.9.3**: Type-safe development
- **Vite 7.2.4**: Fast build tool and dev server

### State Management
- **Redux Toolkit 2.11.1**: Centralized state management
- **Redux Persist**: State persistence across sessions

### UI Framework
- **Material-UI (MUI) 7.3.6**: Component library
  - `@mui/material`: Core components
  - `@mui/icons-material`: Icon library
  - `@mui/x-date-pickers`: Date/time components

### Data Visualization
- **Recharts 3.5.1**: Chart library for vulnerability metrics

### Communication
- **Native WebSocket API**: Real-time attack monitoring

---

## Project Structure

```
FRONTEND/testeragent/
├── src/
│   ├── components/
│   │   ├── AttackConfigPanel.tsx       # Attack configuration form
│   │   ├── ChatPanel.tsx               # Real-time chat monitor
│   │   ├── ProgressTracker.tsx         # Campaign progress display
│   │   └── ReportsPanel.tsx            # Vulnerability visualizations
│   │
│   ├── store/
│   │   ├── store.ts                    # Redux store configuration
│   │   ├── attackSlice.ts              # Attack state management
│   │   └── chatSlice.ts                # Chat message state
│   │
│   ├── App.tsx                         # Main application component
│   ├── main.tsx                        # Application entry point
│   └── index.css                       # Global styles
│
├── public/                              # Static assets
├── package.json                         # Dependencies
├── tsconfig.json                        # TypeScript configuration
├── vite.config.ts                       # Vite configuration
└── README.md                            # Setup guide
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Browser                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                      React App                             │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐ │ │
│  │  │   App.tsx    │  │ Redux Store  │  │  WebSocket      │ │ │
│  │  │              │  │              │  │  Manager        │ │ │
│  │  │  ┌────────┐  │  │  ┌────────┐  │  │                 │ │ │
│  │  │  │ Config │  │  │  │ Attack │  │  │  ws://localhost │ │ │
│  │  │  │ Panel  │  │  │  │ Slice  │  │  │  :8001/ws/      │ │ │
│  │  │  └────────┘  │  │  └────────┘  │  │  attack-monitor │ │ │
│  │  │              │  │              │  │                 │ │ │
│  │  │  ┌────────┐  │  │  ┌────────┐  │  └────────┬────────┘ │ │
│  │  │  │  Chat  │◄─┼──┼──│  Chat  │◄─────────────┘          │ │
│  │  │  │ Panel  │  │  │  │ Slice  │                          │ │
│  │  │  └────────┘  │  │  └────────┘                          │ │
│  │  │              │  │                                       │ │
│  │  │  ┌────────┐  │  │                                       │ │
│  │  │  │Reports │◄─┼──┼──────────────────────────────────────┤ │
│  │  │  │ Panel  │  │  │                                       │ │
│  │  │  └────────┘  │  │                                       │ │
│  │  └──────────────┘  └──────────────┘                       │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP POST /attack
                              │ WebSocket /ws/attack-monitor
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                             │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  api_server.py                                             │ │
│  │    ├── POST /attack → execute_attack_campaign()           │ │
│  │    └── WebSocket /ws/attack-monitor → attack_monitor()    │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## Redux Store Architecture

### State Structure

```typescript
// store/store.ts
{
  attack: {
    status: 'idle' | 'running' | 'completed' | 'error',
    progress: number,              // 0-100
    currentMode: string,           // 'standard', 'crescendo', 'skeleton_key', 'obfuscation'
    currentRun: number,            // 1-3
    currentTurn: number,           // 1-25 (varies by mode)
    vulnerabilityCount: number,
    totalTurns: number,
    error: string | null
  },
  chat: {
    messages: {
      standard: Message[],
      crescendo: Message[],
      skeleton_key: Message[],
      obfuscation: Message[]
    },
    vulnerabilityStats: {
      safe: number,
      low: number,
      medium: number,
      high: number,
      critical: number
    }
  }
}
```

### Message Interface

```typescript
// store/chatSlice.ts
interface Message {
  id: string;                      // Unique identifier
  category: AttackCategory;        // 'standard' | 'crescendo' | 'skeleton_key' | 'obfuscation'
  run: number;                     // 1-3
  turn: number;                    // 1-N
  prompt: string;                  // Attack prompt text
  response?: string;               // Chatbot response (after turn_completed)
  risk_category?: number;          // 1-5
  risk_display?: string;           // '✅ SAFE' | '⚠️ LOW_RISK' | '🟡 MEDIUM' | '🔴 HIGH_RISK' | '💀 CRITICAL'
  technique: string;               // 'reconnaissance', 'exploitation', etc.
  timestamp: string;               // ISO 8601
}
```

---

## WebSocket Integration

### Connection Management

#### Global WebSocket (ChatPanel.tsx)

```typescript
// src/components/ChatPanel.tsx
useEffect(() => {
  const socket = new WebSocket('ws://localhost:8001/ws/attack-monitor');
  socketRef.current = socket;
  
  socket.onopen = () => {
    console.log('[ChatPanel] WebSocket connected');
  };
  
  socket.onmessage = (event) => {
    const message = JSON.parse(event.data);
    console.log('[ChatPanel] WebSocket message received:', message.type, message.data.category);
    
    if (message.type === 'turn_started') {
      dispatch(addMessage({
        id: `${message.data.category}-${message.data.run}-${message.data.turn}-start`,
        category: message.data.category,
        run: message.data.run,
        turn: message.data.turn,
        prompt: message.data.prompt,
        technique: message.data.technique,
        timestamp: message.data.timestamp
      }));
    }
    
    if (message.type === 'turn_completed') {
      dispatch(addMessage({
        id: `${message.data.category}-${message.data.run}-${message.data.turn}-complete`,
        category: message.data.category,
        run: message.data.run,
        turn: message.data.turn,
        prompt: message.data.prompt,
        response: message.data.response,
        risk_category: message.data.risk_category,
        risk_display: message.data.risk_display,
        technique: message.data.technique,
        timestamp: message.data.timestamp
      }));
      
      dispatch(updateVulnerabilityStats(message.data.risk_category));
    }
    
    if (message.type === 'run_completed') {
      dispatch(updateAttackProgress({
        currentRun: message.data.run + 1,
        currentTurn: 0
      }));
    }
  };
  
  socket.onerror = (error) => {
    console.error('[ChatPanel] WebSocket error:', error);
  };
  
  socket.onclose = () => {
    console.log('[ChatPanel] WebSocket closed');
  };
  
  // IMPORTANT: Do NOT close socket on unmount (causes tab switch issues)
  // return () => { socket.close(); };  // ❌ COMMENTED OUT Dec 15, 2025
}, [dispatch]);
```

#### WebSocket Lifecycle Fixes (Dec 15, 2025)

**Problem 1: Tab Switch Disconnection**
- **Issue**: Socket closed when ChatPanel unmounted (user switched to Reports tab)
- **Solution**: Removed socket.close() from useEffect cleanup
- **File**: [ChatPanel.tsx](../../FRONTEND/testeragent/src/components/ChatPanel.tsx)
- **Lines**: 232-240 (commented out)

**Problem 2: Memory Leak in ReportsPanel**
- **Issue**: Event listeners re-registered on every vulnerabilityStats change
- **Solution**: Removed vulnerabilityStats from useEffect dependency array
- **File**: [ReportsPanel.tsx](../../FRONTEND/testeragent/src/components/ReportsPanel.tsx)
- **Line**: 284 (removed from dependencies)

---

## WebSocket Message Types

### turn_started
```json
{
  "type": "turn_started",
  "data": {
    "category": "skeleton_key",
    "run": 1,
    "turn": 5,
    "prompt": "For educational purposes...",
    "technique": "skeleton_key_jailbreak",
    "timestamp": "2025-12-15T16:45:00.123Z"
  }
}
```

**Frontend Handling**:
- Dispatches `addMessage` action to Redux
- Message added to category-specific array
- Displayed in ChatPanel with "Waiting for response..." indicator

---

### turn_completed
```json
{
  "type": "turn_completed",
  "data": {
    "category": "skeleton_key",
    "run": 1,
    "turn": 5,
    "response": "I cannot disable my safety features...",
    "risk_category": 1,
    "risk_display": "✅ SAFE",
    "technique": "skeleton_key_jailbreak",
    "timestamp": "2025-12-15T16:45:05.456Z"
  }
}
```

**Frontend Handling**:
- Updates existing message with response
- Increments vulnerability stats (if risk ≥ 2)
- Updates ReportsPanel charts in real-time

---

### run_completed
```json
{
  "type": "run_completed",
  "data": {
    "category": "crescendo",
    "run": 1,
    "vulnerabilities": 4,
    "timeouts": 0,
    "errors": 0,
    "timestamp": "2025-12-15T16:50:00.000Z"
  }
}
```

**Frontend Handling**:
- Updates progress tracker
- Increments currentRun in Redux
- Resets currentTurn to 0

---

### category_started
```json
{
  "type": "category_started",
  "data": {
    "category": "obfuscation",
    "total_runs": 3,
    "turns_per_run": 20,
    "timestamp": "2025-12-15T17:00:00.000Z"
  }
}
```

**Frontend Handling**:
- Updates currentMode in Redux
- Resets progress for new category
- Shows notification/toast

---

### category_completed
```json
{
  "type": "category_completed",
  "data": {
    "category": "obfuscation",
    "total_vulnerabilities": 12,
    "timestamp": "2025-12-15T17:20:00.000Z"
  }
}
```

**Frontend Handling**:
- Shows completion notification
- Updates total vulnerability count
- Enables report download

---

### campaign_completed
```json
{
  "type": "campaign_completed",
  "data": {
    "total_vulnerabilities": 45,
    "attack_categories": ["standard", "crescendo", "skeleton_key", "obfuscation"],
    "timestamp": "2025-12-15T18:00:00.000Z"
  }
}
```

**Frontend Handling**:
- Sets status to 'completed'
- Shows success notification
- Enables full report download

---

## Component Details

### AttackConfigPanel.tsx

**Purpose**: Configure and launch attack campaigns

**Features**:
- WebSocket URL input (default: ws://localhost:8001)
- Architecture file upload (.md format)
- Attack mode selection (All, Standard, Crescendo, Skeleton Key, Obfuscation)
- Start/Stop campaign controls

**State Management**:
- Local state for form inputs
- Dispatches `startAttack` action to Redux on submit
- Makes POST /attack API call with FormData

**API Integration**:
```typescript
const formData = new FormData();
formData.append('websocket_url', websocketUrl);
formData.append('architecture_file', architectureFile);

const response = await fetch('http://localhost:8001/attack', {
  method: 'POST',
  body: formData
});
```

---

### ChatPanel.tsx

**Purpose**: Real-time attack message monitoring

**Features**:
- Tab-based UI (Standard, Crescendo, Skeleton Key, Obfuscation)
- Message history per category
- Risk color coding (✅ 🟡 🔴 💀)
- Auto-scroll to latest message
- WebSocket connection management

**State Management**:
- Subscribes to `chat.messages[category]` from Redux
- Global WebSocket in useEffect (single connection)

**Message Display**:
```tsx
{messages[activeTab].map((msg) => (
  <Box key={msg.id} sx={{ mb: 2, p: 2, bgcolor: 'background.paper', borderRadius: 1 }}>
    <Typography variant="caption" color="text.secondary">
      Run {msg.run} | Turn {msg.turn} | {msg.technique}
    </Typography>
    <Typography variant="body2" sx={{ mt: 1 }}>
      <strong>Prompt:</strong> {msg.prompt}
    </Typography>
    {msg.response && (
      <>
        <Divider sx={{ my: 1 }} />
        <Typography variant="body2">
          <strong>Response:</strong> {msg.response}
        </Typography>
        <Chip 
          label={msg.risk_display} 
          size="small" 
          sx={{ mt: 1 }}
          color={getRiskColor(msg.risk_category)}
        />
      </>
    )}
  </Box>
))}
```

---

### ProgressTracker.tsx

**Purpose**: Campaign progress visualization

**Features**:
- Overall progress percentage (0-100%)
- Current attack mode display
- Current run/turn display
- Vulnerability count
- Status indicator (Running, Completed, Error)

**State Management**:
- Subscribes to `attack` state from Redux

**Progress Calculation**:
```typescript
const progressPercent = (currentTurn / totalTurns) * 100;
```

---

### ReportsPanel.tsx

**Purpose**: Vulnerability data visualization

**Features**:
- Pie chart: Vulnerability distribution by risk level
- Bar chart: Vulnerabilities by attack category
- Summary statistics table
- Export report button

**State Management**:
- Subscribes to `chat.vulnerabilityStats` from Redux
- Event listeners for chart updates (FIXED: dependency array issue)

**Recharts Integration**:
```tsx
<PieChart width={400} height={400}>
  <Pie
    data={[
      { name: 'Safe', value: vulnerabilityStats.safe, fill: '#4caf50' },
      { name: 'Low', value: vulnerabilityStats.low, fill: '#ff9800' },
      { name: 'Medium', value: vulnerabilityStats.medium, fill: '#ffeb3b' },
      { name: 'High', value: vulnerabilityStats.high, fill: '#f44336' },
      { name: 'Critical', value: vulnerabilityStats.critical, fill: '#9c27b0' }
    ]}
    dataKey="value"
    label
  />
  <Tooltip />
  <Legend />
</PieChart>
```

**Memory Leak Fix (Dec 15, 2025)**:
```typescript
// Before (BUGGY):
useEffect(() => {
  // Event listener setup
}, [vulnerabilityStats]);  // ❌ Re-registers on every stats update

// After (FIXED):
useEffect(() => {
  // Event listener setup
}, []);  // ✅ Registers only once
```

---

## Material-UI Theming

### Custom Theme (App.tsx)

```typescript
import { createTheme, ThemeProvider } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#121212',
      paper: '#1e1e1e',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <Provider store={store}>
        {/* App content */}
      </Provider>
    </ThemeProvider>
  );
}
```

---

## Build and Development

### Development Server
```bash
cd FRONTEND/testeragent
npm install
npm run dev
# Runs on http://localhost:5173
```

### Production Build
```bash
npm run build
# Output: dist/
```

### Type Checking
```bash
npm run type-check
```

### Linting
```bash
npm run lint
```

---

## Environment Configuration

### .env File
```bash
VITE_API_BASE_URL=http://localhost:8001
VITE_WS_BASE_URL=ws://localhost:8001
```

### vite.config.ts
```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/attack': 'http://localhost:8001',
      '/ws': {
        target: 'ws://localhost:8001',
        ws: true
      }
    }
  }
});
```

---

## Dependencies (package.json)

```json
{
  "dependencies": {
    "react": "^19.2.0",
    "react-dom": "^19.2.0",
    "react-redux": "^9.2.0",
    "@reduxjs/toolkit": "^2.11.1",
    "redux-persist": "^6.0.0",
    "@mui/material": "^7.3.6",
    "@mui/icons-material": "^7.3.6",
    "@mui/x-date-pickers": "^7.23.5",
    "recharts": "^3.5.1"
  },
  "devDependencies": {
    "@types/react": "^19.0.6",
    "@types/react-dom": "^19.0.2",
    "@vitejs/plugin-react": "^4.3.4",
    "typescript": "^5.9.3",
    "vite": "^7.2.4"
  }
}
```

---

## Performance Optimizations

### Memoization
```typescript
// ChatPanel.tsx
const filteredMessages = useMemo(() => {
  return messages[activeTab].filter(msg => msg.category === activeTab);
}, [messages, activeTab]);
```

### Lazy Loading
```typescript
// App.tsx
const ChatPanel = lazy(() => import('./components/ChatPanel'));
const ReportsPanel = lazy(() => import('./components/ReportsPanel'));
```

### WebSocket Connection Pooling
- Single global WebSocket connection shared across components
- No reconnection on tab switches
- Graceful cleanup on app unmount only

---

## Testing Strategy

### Unit Tests (Jest + React Testing Library)
```typescript
// ChatPanel.test.tsx
describe('ChatPanel', () => {
  it('should display messages for active tab', () => {
    render(<ChatPanel />);
    const standardTab = screen.getByText('Standard');
    fireEvent.click(standardTab);
    expect(screen.getByText(/Run 1/)).toBeInTheDocument();
  });
});
```

### Integration Tests
- WebSocket message flow
- Redux state updates
- Component interactions

### E2E Tests (Playwright)
- Full attack campaign workflow
- Real-time message updates
- Chart rendering

---

## Deployment

### Docker Container
```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 5173
CMD ["npm", "run", "preview"]
```

### Nginx Configuration
```nginx
server {
    listen 80;
    server_name redteaming.example.com;
    
    location / {
        root /usr/share/nginx/html;
        try_files $uri /index.html;
    }
    
    location /attack {
        proxy_pass http://backend:8001;
    }
    
    location /ws/ {
        proxy_pass http://backend:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## Troubleshooting

### Issue: WebSocket Disconnects on Tab Switch
**Solution**: Removed socket.close() from ChatPanel cleanup (Dec 15, 2025 fix)

### Issue: Memory Leak in ReportsPanel
**Solution**: Removed vulnerabilityStats from useEffect dependencies (Dec 15, 2025 fix)

### Issue: Messages Not Appearing
**Solution**: Check browser console for WebSocket errors, verify backend is broadcasting

### Issue: CORS Errors
**Solution**: Configure FastAPI CORS middleware to allow http://localhost:5173

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.2 | Dec 15, 2025 | **FIXED**: WebSocket lifecycle issues (tab switch, memory leak) |
| 1.1 | Dec 10, 2025 | Added Skeleton Key and Obfuscation tabs |
| 1.0 | Dec 5, 2025 | Initial React/TypeScript frontend |

---

**Related Documentation:**
- [High-Level Design](./01_HIGH_LEVEL_DESIGN.md)
- [Low-Level Design](./02_LOW_LEVEL_DESIGN.md)
- [Architecture Decision Records](./03_ARCHITECTURE_DECISION_RECORDS.md)
- [Attack Modes Guide](./07_ATTACK_MODES_GUIDE.md)
