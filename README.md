"# AI Red Teaming Platform - Hackathon Project

## Overview

AI Red Teaming Platform for automated security testing of AI chatbots using multi-mode attack strategies (Standard, Crescendo, Skeleton Key, Obfuscation).

---

## Quick Links

### 📖 Documentation
- **[Main Documentation Index](./RedTeaming/BACKEND/doc/README.md)** - Complete documentation hub
- **[Attack Modes Guide](./RedTeaming/BACKEND/doc/07_ATTACK_MODES_GUIDE.md)** - Comprehensive attack strategy comparison
- **[Frontend Architecture](./RedTeaming/BACKEND/doc/08_FRONTEND_ARCHITECTURE.md)** - React/TypeScript/Redux details

### 🚀 Getting Started
- **[Setup Guide](./RedTeaming/SETUP_GUIDE.md)** - Installation and configuration
- **[Quick Start](./RedTeaming/QUICKSTART.md)** - Running your first attack
- **[Technical Execution](./RedTeaming/TECHNICAL_EXECUTION.md)** - Advanced usage

### 🎯 Attack Modes
- **[Crescendo](./RedTeaming/BACKEND/doc/attack_modes/CRESCENDO.md)** - Personality-based social engineering (3×15 turns)
- **[Skeleton Key](./RedTeaming/BACKEND/doc/attack_modes/SKELETON_KEY.md)** - Jailbreak attacks (3×10 turns)
- **[Obfuscation](./RedTeaming/BACKEND/doc/attack_modes/OBFUSCATION.md)** - Filter bypass (3×20 turns)
- **[Standard](./RedTeaming/BACKEND/doc/attack_modes/STANDARD.md)** - Multi-phase attacks (3×25 turns)

---

## Technology Stack

### Backend
- **Python 3.9+**: FastAPI, Uvicorn
- **AI**: Azure OpenAI GPT-4o
- **Database**: DuckDB via PyRIT
- **Communication**: WebSocket (native)

### Frontend
- **React 19.2.0** + TypeScript 5.9.3
- **Redux Toolkit 2.11.1** for state management
- **Material-UI 7.3.6** for UI components
- **Recharts 3.5.1** for data visualization
- **Vite 7.2.4** for build tooling

---

## Project Structure

```
Hackathon/
├── README.md                                    # This file
├── RedTeaming/
│   ├── BACKEND/
│   │   ├── doc/                                 # 📖 Main documentation
│   │   │   ├── README.md                        # Documentation index
│   │   │   ├── 01_HIGH_LEVEL_DESIGN.md
│   │   │   ├── 02_LOW_LEVEL_DESIGN.md
│   │   │   ├── 03_ARCHITECTURE_DECISION_RECORDS.md
│   │   │   ├── 04_C4_DIAGRAMS.md
│   │   │   ├── 05_SEQUENCE_DIAGRAMS.md
│   │   │   ├── 06_FUNCTIONAL_DOCUMENTATION.md
│   │   │   ├── 07_ATTACK_MODES_GUIDE.md        # ⭐ Attack comparison
│   │   │   ├── 08_FRONTEND_ARCHITECTURE.md     # ⭐ React/Redux guide
│   │   │   └── attack_modes/
│   │   │       ├── CRESCENDO.md
│   │   │       ├── SKELETON_KEY.md
│   │   │       ├── OBFUSCATION.md
│   │   │       └── STANDARD.md
│   │   ├── core/                                # Orchestrators & clients
│   │   ├── attack_strategies/                   # Strategy implementations
│   │   ├── config/                              # Settings
│   │   ├── main.py                              # CLI entry point
│   │   └── api_server.py                        # FastAPI server
│   ├── FRONTEND/
│   │   └── testeragent/                         # React app
│   │       ├── src/
│   │       │   ├── components/                  # React components
│   │       │   ├── store/                       # Redux store
│   │       │   └── App.tsx
│   │       └── package.json
│   ├── SETUP_GUIDE.md
│   ├── QUICKSTART.md
│   └── TECHNICAL_EXECUTION.md
└── GTM_ONE_PAGER.md
```

---

## Latest Updates (Dec 15, 2025)

### ✅ WebSocket Fixes
- **Skeleton Key & Obfuscation**: Added missing `turn_started` and `turn_completed` broadcasts
- **ChatPanel**: Removed socket.close() on unmount (fixed tab switch disconnection)
- **ReportsPanel**: Fixed memory leak by removing vulnerabilityStats from useEffect dependencies

### ✅ Documentation Consolidation
- Merged `/doc` and `/docs` folders into single `/doc` location
- Created organized `/doc/attack_modes/` subdirectory
- Added comprehensive guides: `07_ATTACK_MODES_GUIDE.md`, `08_FRONTEND_ARCHITECTURE.md`
- Deprecated old `/docs` folder with migration notice

### ✅ Frontend Upgrade
- Migrated from plain HTML/JS to React 19 + TypeScript
- Implemented Redux Toolkit for state management
- Added Material-UI components and Recharts visualizations
- Real-time WebSocket integration with tab-based UI

---

## Development

### Backend Setup
```bash
cd RedTeaming/BACKEND
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt

# Configure .env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_DEPLOYMENT=gpt-4o
CHATBOT_WEBSOCKET_URL=ws://localhost:8001

# Run API server
python api_server.py
```

### Frontend Setup
```bash
cd RedTeaming/FRONTEND/testeragent
npm install
npm run dev
# Opens http://localhost:5173
```

---

## Usage

### Full Campaign (All Modes)
```bash
# Start backend
python api_server.py

# Open frontend
http://localhost:5173

# Upload architecture file and start attack
```

### Single Mode (CLI)
```bash
python main.py
# Select mode: 1=Standard, 2=Crescendo, 3=Skeleton Key, 4=Obfuscation
```

---

## Contributing

See [TECHNICAL_EXECUTION.md](./RedTeaming/TECHNICAL_EXECUTION.md) for development guidelines.

---

## Documentation

**Primary**: [📖 Documentation Index](./RedTeaming/BACKEND/doc/README.md)

**Deprecated**: `RedTeaming/BACKEND/docs/` - See [_DEPRECATION_NOTICE.md](./RedTeaming/BACKEND/docs/_DEPRECATION_NOTICE.md)

---

## License

[Add license information]

---

**Last Updated**: December 15, 2025  
**Version**: 1.2
"