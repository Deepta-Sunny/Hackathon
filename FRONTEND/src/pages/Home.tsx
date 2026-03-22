import { Box, Paper, Typography, Chip } from "@mui/material";
import { useCallback, useEffect, useState } from "react";
import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import { createUseStyles } from "react-jss";
import Header from "../components/Header";
import ChatPanel from "../components/ChatPanel";
import ReportsPanel from "../components/ReportsPanel";
import type { AppDispatch } from "../store/Store";
import { initiateAttack, openAttackMonitor, haltAttack } from "../thunk/ApiThunk";
import Button from "@mui/joy/Button";
import EditIcon from "@mui/icons-material/Edit";

const useStyles = createUseStyles({
  profileCard: {
    padding: 12,
    marginBottom: 12,
    background: "#fff",
    color: "#222",
    borderRadius: 16,
    borderTop: "4px solid #0f62fe",
    boxShadow: "0 4px 20px rgba(0,0,0,0.05)",
    fontFamily: "sans-serif",
  },
  profileHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 8,
    borderBottom: "1px solid #eee",
    paddingBottom: 8,
    fontFamily: "sans-serif",
  },
  profileTitle: {
    fontSize: 28,
    fontWeight: 700,
    fontFamily: "sans-serif",
    color: "#0f62fe",
    display: "flex",
    alignItems: "center",
    gap: 12,
    letterSpacing: "-0.5px",
  },
  profileInfo: {
    display: "grid",
    gridTemplateColumns: "repeat(5, 1fr)",
    gap: 16,
    fontFamily: "sans-serif",
  },
  infoItem: {
    background: "#f9fafb",
    padding: 12,
    borderRadius: 12,
    border: "1px solid #e5e7eb",
    transition: "all 0.12s",
    fontFamily: "sans-serif",
    "&:hover": {
      borderColor: "#0f62fe",
      transform: "translateY(-1px)",
      boxShadow: "0 4px 12px rgba(15,98,254,0.08)",
    },
  },
  infoLabel: {
    fontSize: 12,
    color: "#6b7280",
    marginBottom: 4,
    fontFamily: "sans-serif",
    textTransform: "uppercase",
    letterSpacing: "0.5px",
    fontWeight: 600,
  },
  infoValue: {
    fontSize: 15,
    fontWeight: 700,
    fontFamily: "sans-serif",
    color: "#222",
  },
  startButton: {
    background: "#0f62fe !important",
    color: "white !important",
    fontFamily: "sans-serif !important",
    fontWeight: "700 !important",
    padding: "8px 16px !important",
    minWidth: "110px",
    height: "40px",
    fontSize: "15px !important",
    borderRadius: "8px !important",
    transition: "all 0.2s !important",
    border: "none !important",
    boxShadow: "0 2px 10px rgba(15,98,254,0.10)",
    "&:hover": {
      background: "#0353e9 !important",
      transform: "translateY(-1px)",
      boxShadow: "0 4px 16px rgba(15, 98, 254, 0.18)",
    },
  },
  editButton: {
    background: "#f3f4f6 !important",
    color: "#555 !important",
    fontFamily: "sans-serif !important",
    padding: "8px 16px !important",
    minWidth: "110px",
    height: "40px",
    fontSize: "15px !important",
    borderRadius: "8px !important",
    border: "1px solid #e5e7eb !important",
    "&:hover": {
      background: "#e0e7ef !important",
      borderColor: "#0f62fe !important",
    },
  },
});

interface ChatbotProfile {
  username: string;
  websocket_url: string;
  domain: string;
  primary_objective: string;
  intended_audience: string;
  chatbot_role: string;
  capabilities: string[];
  agent_type?: string;
  boundaries: string;
  communication_style: string;
  context_awareness: string;
}

function Home() {
  const classes = useStyles();
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const [profile, setProfile] = useState<ChatbotProfile | null>(null);
  const [attackStarted, setAttackStarted] = useState(false);
  const [isStarting, setIsStarting] = useState(false);

  useEffect(() => {
    // Try to load saved dashboard state first
    const loadDashboardState = async () => {
      try {
        const response = await fetch('http://localhost:8080/api/dashboard/load');
        const data = await response.json();
        
        if (data.found && data.state) {
          // Use saved state
          setProfile(data.state);
          sessionStorage.setItem("chatbotProfile", JSON.stringify(data.state));
          return;
        }
      } catch (error) {
        console.log("No saved dashboard state found, checking sessionStorage");
      }
      
      // Fallback to sessionStorage
      const savedProfile = sessionStorage.getItem("chatbotProfile");
      if (savedProfile) {
        setProfile(JSON.parse(savedProfile));
      } else {
        // Redirect to profile setup if no profile found
        navigate("/");
      }
    };
    
    loadDashboardState();
  }, [navigate]);

  // Open WebSocket monitor when component mounts
  useEffect(() => {
    dispatch(openAttackMonitor());
  }, [dispatch]);

  const handleStartAttack = useCallback(
    async () => {
      if (profile) {
        setIsStarting(true);
        try {
          // Save dashboard state before starting
          await fetch('http://localhost:8080/api/dashboard/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(profile)
          });
        } catch (error) {
          console.error("Failed to save dashboard state:", error);
        }
        
        // Open WebSocket monitor first
        await dispatch(openAttackMonitor());

        // Start testing with profile
        dispatch(initiateAttack(profile));
        setAttackStarted(true);
      }
      setIsStarting(false);
    },
    [dispatch, profile]
  );

  const handleStopAttack = useCallback(async () => {
    try {
      await dispatch(haltAttack());
    } finally {
      setAttackStarted(false);
    }
  }, [dispatch]);

  const handleEditProfile = () => {
    if (attackStarted) return; // prevent navigation while testing
    navigate("/");
  };

  if (!profile) {
    return null; // Will redirect in useEffect
  }

  return (
    <Box>
      <Header />
      <Box display={"flex"} flexDirection={"column"} gap={0.5} marginTop={1}>
        {/* Profile Information Card */}
          <Paper className={classes.profileCard} elevation={8}>
          <div className={classes.profileHeader} />
          <div className={classes.profileInfo}>
            <div className={classes.infoItem}>
              <div className={classes.infoLabel}>Username</div>
              <div className={classes.infoValue}>{profile.username || '-'}</div>
            </div>
            <div className={classes.infoItem}>
              <div className={classes.infoLabel}>WebSocket Endpoint</div>
              <div className={classes.infoValue}>{profile.websocket_url || 'ws://localhost:8001/ws'}</div>
            </div>
            <div className={classes.infoItem}>
              <div className={classes.infoLabel}>Domain</div>
              <div className={classes.infoValue}>{profile.domain || '-'}</div>
            </div>
            <div className={classes.infoItem}>
              <div className={classes.infoLabel}>Capabilities</div>
              <div className={classes.infoValue}>
                <Chip 
                  label={`${profile.capabilities.length} defined`} 
                  size="small" 
                  style={{ color: "#0f62fe", background: "#edf5ff", fontWeight: 600 }}
                />
              </div>
            </div>
            <div className={classes.infoItem}>
              <div className={classes.infoLabel} style={{visibility: 'hidden'}}>actions</div>
              <div style={{display: 'flex', flexDirection: 'row', gap: 8, alignItems: 'center', justifyContent: 'center'}}>
                <Button
                  variant="solid"
                  className={classes.editButton}
                  startDecorator={<EditIcon />}
                  onClick={handleEditProfile}
                  disabled={attackStarted}
                >
                  Edit
                </Button>
                {!attackStarted ? (
                  <Button
                    variant="solid"
                    className={classes.startButton}
                    onClick={handleStartAttack}
                    loading={isStarting}
                    style={isStarting ? { background: "#ff9800" } : {}}
                  >
                    Start
                  </Button>
                ) : (
                  <Button
                    variant="solid"
                    color="neutral"
                    className={classes.startButton}
                    onClick={handleStopAttack}
                    style={{ background: "#c62828" }}
                  >
                    Stop
                  </Button>
                )}
              </div>
            </div>
          </div>
        </Paper>
        
        {/* Two main panels: Chat with tabs and Reports */}
        <Box display={"flex"} gap={2} height={"70vh"}>
          <Box flex={1} display={"flex"}>
            <ChatPanel />
          </Box>
          <Box flex={1} display={"flex"}>
            <ReportsPanel />
          </Box>
        </Box>
      </Box>
    </Box>
  );
}

export default Home;
