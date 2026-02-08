# Red Teaming Workflow Diagram

```mermaid
flowchart TD
    A[User Interface - Profile Setup] --> B[Backend API Server]
    B --> C[Attack Orchestrator]
    C --> D[Target Chatbot]
    D --> E[Attack Results Storage]
    E --> F[Real-time Updates to UI]
    C --> F
    B --> G[WebSocket Broadcasting]
    G --> F
```

This diagram represents the high-level abstract flow of the red teaming system:

- **User Interface**: Where users configure chatbot profiles and initiate attacks
- **Backend API Server**: Handles requests, manages attack execution
- **Attack Orchestrator**: Coordinates different attack strategies (standard, crescendo, skeleton key, obfuscation)
- **Target Chatbot**: The system being tested via WebSocket communication
- **Attack Results Storage**: Stores vulnerability findings and reports
- **Real-time Updates**: Live feedback to the user interface during attacks