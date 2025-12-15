import { Box, Paper, Typography, Tabs, Tab } from "@mui/material";
import React, { useEffect, useRef, useState } from "react";
import { createUseStyles } from "react-jss";
import { useDispatch, useSelector } from "react-redux";
import type { AppDispatch, RootState } from "../store/Store";
import { clearMonitor, setMonitorOpen } from "../store/Slice";
import { openAttackMonitor } from "../thunk/ApiThunk";

const useStyles = createUseStyles({
  container: {
    border: "1px solid #20a100ff",
    display: "flex",
    flexDirection: "column",
    height: "100%",
    width: "100%",
    backgroundColor: "#ffffff",
    borderRadius: "8px",
    minHeight: 0,
    overflow: "hidden",
  },
  header: {
    padding: "16px 20px",
    backgroundColor: "#dbdbdbff",
    color: "#20a100ff",
    boxShadow: "0 10px 10px rgba(0, 0, 0, 0.1)",
    textAlign: "left",
    borderBottom: "1px solid #00000010",
  },
  headerTitle: {
    fontWeight: 600,
    fontSize: "18px",
  },
  status: {
    padding: "12px 16px",
    borderBottom: "1px solid #00000010",
    height: "10px",
    display: "flex",
    alignItems: "center",
  },
  messages: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    gap: "12px",
    padding: "16px",
    overflowY: "auto",
    backgroundColor: "#f8f9fa",
  },
  message: {
    padding: "12px 16px",
    borderRadius: "10px",
    maxWidth: "85%",
    boxShadow: "0 4px 12px rgba(0, 0, 0, 0.06)",
    display: "flex",
    flexDirection: "column",
    gap: "8px",
  },
  agentMessage: {
    alignSelf: "flex-start",
    backgroundColor: "#e6f4ea",
    color: "#0f5132",
  },
  aiMessage: {
    alignSelf: "flex-end",
    backgroundColor: "#e8f0fe",
    color: "#1a237e",
  },
  messageTitle: {
    fontWeight: 600,
    fontSize: "14px",
  },
  messageText: {
    fontSize: "14px",
    lineHeight: 1.5,
    whiteSpace: "pre-wrap",
  },
  messageMeta: {
    fontSize: "12px",
    opacity: 0.7,
  },
  emptyState: {
    marginTop: "auto",
    marginBottom: "auto",
    textAlign: "center",
    opacity: 0.6,
  },
  tabsContainer: {
    borderBottom: "1px solid #00000010",
    backgroundColor: "#ffffff",
  },
  tab: {
    textTransform: "none",
    fontFamily: "inherit",
    fontWeight: 500,
    minHeight: "48px",
  },
});

type ChatMessage = {
  id: string;
  sender: "agent" | "ai";
  content: string;
  category?: string;
  run?: number;
  turn?: number;
  riskDisplay?: string;
  timestamp?: string;
};

const ChatPanel: React.FC = () => {
  const classes = useStyles();
  const dispatch = useDispatch<AppDispatch>();
  const { monitorSocket, monitorConnecting, monitorError } = useSelector(
    (state: RootState) => state.api
  );
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [categoryTab, setCategoryTab] = useState("all");
  const [runFilter, setRunFilter] = useState<number | "all">("all");
  const listRef = useRef<HTMLDivElement | null>(null);

  // Get unique categories and runs from messages
  const categories = ["all", ...Array.from(new Set(messages.map(m => m.category).filter(Boolean)))];
  const runs = Array.from(new Set(messages.filter(m => categoryTab === "all" || m.category === categoryTab).map(m => m.run).filter((r): r is number => typeof r === "number")));
  runs.sort((a, b) => a - b);

  useEffect(() => {
    if (!monitorSocket) {
      return;
    }
    if (monitorSocket.readyState === WebSocket.OPEN) {
      dispatch(setMonitorOpen(true));
    }

    const handleMessage = (event: MessageEvent) => {
      try {
        const payload = JSON.parse(event.data) as {
          type: string;
          data?: Record<string, unknown>;
        };

        if (payload.type === "attack_started") {
          setMessages([]);
          return;
        }

        if (payload.type === "turn_started" && payload.data) {
          const data = payload.data as Record<string, unknown>;
          setMessages((prev) => [
            ...prev,
            {
              id: `agent-${data.category}-${data.run}-${data.turn}-${
                data.timestamp ?? Date.now()
              }`,
              sender: "agent",
              content: String(data.prompt ?? ""),
              category: String(data.category ?? ""),
              run: Number(data.run ?? 0),
              turn: Number(data.turn ?? 0),
              timestamp:
                typeof data.timestamp === "string" ? data.timestamp : undefined,
            },
          ]);
        } else if (payload.type === "turn_completed" && payload.data) {
          const data = payload.data as Record<string, unknown>;
          
          // Extract text from response - handle both plain text and JSON/dict format
          let responseText = String(data.response ?? "");
          
          // Check if it starts with a dict/JSON format
          if (responseText.trim().startsWith('{') && responseText.includes('response')) {
            // Try to parse as JSON first
            try {
              const parsed = JSON.parse(responseText);
              if (parsed && typeof parsed === 'object' && 'response' in parsed) {
                responseText = String(parsed.response);
              }
            } catch {
              // If JSON parse fails, handle Python dict-like format {'response': '...'}
              // This regex handles both single and double quotes, and extracts everything after 'response':
              const match = responseText.match(/['"]response['"]\s*:\s*["'](.+?)["'](?:\s*[,}]|$)/s);
              if (match) {
                responseText = match[1];
              } else {
                // Try without quotes around the value (edge case)
                const noQuoteMatch = responseText.match(/['"]response['"]\s*:\s*(.+?)(?:\s*[,}]|$)/s);
                if (noQuoteMatch) {
                  responseText = noQuoteMatch[1].trim();
                } else {
                  // Last resort: remove the leading dict syntax
                  responseText = responseText.replace(/^\s*\{\s*['"]response['"]\s*:\s*['"]/, '').replace(/['"]\s*\}\s*$/, '');
                }
              }
              
              // Unescape common escape sequences
              responseText = responseText
                .replace(/\\n/g, '\n')
                .replace(/\\t/g, '\t')
                .replace(/\\r/g, '\r')
                .replace(/\\'/g, "'")
                .replace(/\\"/g, '"')
                .replace(/\\\\/g, '\\');
            }
          }
          
          setMessages((prev) => [
            ...prev,
            {
              id: `ai-${data.category}-${data.run}-${data.turn}-${
                data.timestamp ?? Date.now()
              }`,
              sender: "ai",
              content: responseText,
              category: String(data.category ?? ""),
              run: Number(data.run ?? 0),
              turn: Number(data.turn ?? 0),
              riskDisplay:
                typeof data.risk_display === "string"
                  ? data.risk_display
                  : typeof data.riskDisplay === "string"
                  ? data.riskDisplay
                  : undefined,
              timestamp:
                typeof data.timestamp === "string" ? data.timestamp : undefined,
            },
          ]);
        }
      } catch (error) {
        console.warn("Failed to parse attack-monitor message", error);
      }
    };

    const handleOpen = () => {
      dispatch(setMonitorOpen(true));
    };

    const handleClose = (event: CloseEvent) => {
      const intentionalStop =
        event.code === 1000 &&
        (event.reason === "User requested stop" ||
          event.reason === "component-disconnect");
      dispatch(clearMonitor());
      if (!intentionalStop) {
        void dispatch(openAttackMonitor());
      }
    };

    monitorSocket.addEventListener("open", handleOpen);
    monitorSocket.addEventListener("message", handleMessage);
    monitorSocket.addEventListener("close", handleClose);
    return () => {
      monitorSocket.removeEventListener("open", handleOpen);
      monitorSocket.removeEventListener("message", handleMessage);
      monitorSocket.removeEventListener("close", handleClose);
    };
  }, [dispatch, monitorSocket]);

  useEffect(() => {
    if (!listRef.current) {
      return;
    }
    listRef.current.scrollTop = listRef.current.scrollHeight;
  }, [messages]);

  useEffect(() => {
    return () => {
      if (monitorSocket) {
        monitorSocket.close(1000, "component-disconnect");
        dispatch(clearMonitor());
      }
    };
  }, [dispatch, monitorSocket]);

  const formatMeta = (message: ChatMessage) => {
    const metaParts: string[] = [];
    if (message.category) {
      metaParts.push(message.category.replace(/_/g, " ").toUpperCase());
    }
    if (typeof message.turn === "number" && !Number.isNaN(message.turn)) {
      metaParts.push(`Turn ${message.turn}`);
    }
    if (message.sender === "ai" && message.riskDisplay) {
      metaParts.push(message.riskDisplay);
    }
    if (message.timestamp) {
      const timeString = new Date(message.timestamp).toLocaleTimeString();
      metaParts.push(timeString);
    }
    return metaParts.join(" • ");
  };

  const showIdle = !monitorConnecting && !monitorError && messages.length === 0;

  // Filter messages by selected category and run
  const filteredMessages = messages.filter(msg => {
    const categoryMatch = categoryTab === "all" || msg.category === categoryTab;
    const runMatch = runFilter === "all" || msg.run === runFilter;
    return categoryMatch && runMatch;
  });

  return (
    <Paper className={classes.container} elevation={2}>
      <Box className={classes.header}>
        <Typography fontFamily="inherit" className={classes.headerTitle}>
          Chat Monitor
        </Typography>
      </Box>
      
      {/* Category Tabs */}
      <Box className={classes.tabsContainer}>
        <Tabs
          value={categoryTab}
          onChange={(_, newValue) => {
            setCategoryTab(newValue);
            setRunFilter("all");
          }}
          variant="scrollable"
          scrollButtons="auto"
          sx={{
            '& .MuiTab-root': {
              fontFamily: 'inherit',
              textTransform: 'none',
            },
            '& .Mui-selected': {
              color: '#20a100ff',
            },
            '& .MuiTabs-indicator': {
              backgroundColor: '#20a100ff',
            },
          }}
        >
          <Tab className={classes.tab} label="All" value="all" />
          <Tab className={classes.tab} label="Standard" value="standard" />
          <Tab className={classes.tab} label="Crescendo" value="crescendo" />
          <Tab className={classes.tab} label="Skeleton Key" value="skeleton_key" />
          <Tab className={classes.tab} label="Obfuscation" value="obfuscation" />
        </Tabs>
      </Box>
      
      {/* Run Filter Tabs (Each attack has 3 runs) */}
      {runs.length > 0 && (
        <Box className={classes.tabsContainer}>
          <Tabs
            value={runFilter}
            onChange={(_, newValue) => setRunFilter(newValue)}
            variant="scrollable"
            scrollButtons="auto"
            sx={{
              '& .MuiTab-root': {
                fontFamily: 'inherit',
                textTransform: 'none',
                minWidth: 80,
              },
              '& .Mui-selected': {
                color: '#20a100ff',
              },
              '& .MuiTabs-indicator': {
                backgroundColor: '#20a100ff',
              },
            }}
          >
            <Tab className={classes.tab} label="All Runs" value="all" />
            {runs.map(run => (
              <Tab key={run} className={classes.tab} label={`Run ${run}`} value={run} />
            ))}
          </Tabs>
        </Box>
      )}
      <Box className={classes.status}>
        {monitorConnecting && (
          <Typography fontSize={14} color="#555555">
            Connecting to attack monitor…
          </Typography>
        )}
        {monitorError && (
          <Typography fontSize={14} color="#e53935">
            {monitorError}
          </Typography>
        )}
        {showIdle && (
          <Typography fontSize={14} color="#555555">
            Waiting for attack activity…
          </Typography>
        )}
      </Box>
      <Box ref={listRef} className={classes.messages}>
        {filteredMessages.map((message) => (
          <Box
            key={message.id}
            className={`${classes.message} ${
              message.sender === "agent"
                ? classes.aiMessage
                : classes.agentMessage
            }`}
          >
            <Typography className={classes.messageTitle}>
              {message.sender === "agent" ? "Botman" : "AI Response"}
            </Typography>
            <Typography className={classes.messageText}>
              {message.content}
            </Typography>
            <Typography className={classes.messageMeta}>
              {formatMeta(message)}
            </Typography>
          </Box>
        ))}
        {filteredMessages.length === 0 && !monitorConnecting && !monitorError && (
          <Typography className={classes.emptyState}>
            No messages yet.
          </Typography>
        )}
      </Box>
    </Paper>
  );
};

export default ChatPanel;
