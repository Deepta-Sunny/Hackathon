import { Box, Paper, Typography, Chip } from "@mui/material";
import { useCallback, useEffect, useState } from "react";
import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import { createUseStyles } from "react-jss";
import Header from "../components/Header";
import ChatPanel from "../components/ChatPanel";
import ReportsPanel from "../components/ReportsPanel";
import type { AppDispatch } from "../store/Store";
import { initiateAttack, openAttackMonitor } from "../thunk/ApiThunk";
import Button from "@mui/joy/Button";
import RocketLaunchIcon from "@mui/icons-material/RocketLaunch";
import EditIcon from "@mui/icons-material/Edit";

const useStyles = createUseStyles({
  profileCard: {
    padding: 24,
    marginBottom: 20,
    background: "#fff",
    color: "#2c3e50",
    borderRadius: 12,
    borderTop: "4px solid #20a100",
    boxShadow: "0 4px 12px rgba(0,0,0,0.05)",
  },
  profileHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 20,
    borderBottom: "1px solid #eee",
    paddingBottom: 16,
  },
  profileTitle: {
    fontSize: 24,
    fontWeight: 700,
    fontFamily: "monospace",
    color: "#20a100",
    display: "flex",
    alignItems: "center",
    gap: 12,
  },
  profileInfo: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
    gap: 16,
  },
  infoItem: {
    background: "#f8f9fa",
    padding: 16,
    borderRadius: 8,
    border: "1px solid #eee",
    transition: "all 0.2s",
    "&:hover": {
      borderColor: "#20a100",
      transform: "translateY(-2px)",
      boxShadow: "0 4px 12px rgba(0,0,0,0.05)",
    },
  },
  infoLabel: {
    fontSize: 12,
    color: "#888",
    marginBottom: 4,
    fontFamily: "monospace",
    textTransform: "uppercase",
    letterSpacing: "1px",
  },
  infoValue: {
    fontSize: 16,
    fontWeight: 600,
    fontFamily: "monospace",
    color: "#333",
  },
  startButton: {
    background: "#20a100 !important",
    color: "white !important",
    fontFamily: "monospace !important",
    fontWeight: "700 !important",
    padding: "10px 24px !important",
    fontSize: "14px !important",
    borderRadius: "6px !important",
    transition: "all 0.2s !important",
    border: "none !important",
    "&:hover": {
      background: "#1a8f00 !important",
      transform: "translateY(-1px)",
      boxShadow: "0 4px 12px rgba(32, 161, 0, 0.3)",
    },
  },
  editButton: {
    background: "#f1f1f1 !important",
    color: "#555 !important",
    fontFamily: "monospace !important",
    padding: "10px 20px !important",
    fontSize: "14px !important",
    borderRadius: "6px !important",
    border: "1px solid #ddd !important",
    "&:hover": {
      background: "#e0e0e0 !important",
      borderColor: "#ccc !important",
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

  useEffect(() => {
    // Load profile from sessionStorage
    const savedProfile = sessionStorage.getItem("chatbotProfile");
    if (savedProfile) {
      setProfile(JSON.parse(savedProfile));
    } else {
      // Redirect to profile setup if no profile found
      navigate("/");
    }
  }, [navigate]);

  const handleStartAttack = useCallback(
    async () => {
      if (profile) {
        // Open WebSocket monitor first
        await dispatch(openAttackMonitor());
        
        // Start attack with profile
        dispatch(initiateAttack(profile));
        setAttackStarted(true);
      }
    },
    [dispatch, profile]
  );

  const handleEditProfile = () => {
    navigate("/");
  };

  if (!profile) {
    return null; // Will redirect in useEffect
  }

  return (
    <Box>
      <Header />
      <Box display={"flex"} flexDirection={"column"} gap={2} marginTop={4}>
        {/* Profile Information Card */}
        <Paper className={classes.profileCard} elevation={8}>
          <div className={classes.profileHeader}>
            <Typography className={classes.profileTitle}>
              🎯 Target: {profile.chatbot_role}
            </Typography>
            <Box display="flex" gap={2}>
              <Button
                variant="solid"
                className={classes.editButton}
                startDecorator={<EditIcon />}
                onClick={handleEditProfile}
              >
                Edit Profile
              </Button>
              {!attackStarted && (
                <Button
                  variant="solid"
                  className={classes.startButton}
                  startDecorator={<RocketLaunchIcon />}
                  onClick={handleStartAttack}
                >
                  Start Attack
                </Button>
              )}
            </Box>
          </div>
          <div className={classes.profileInfo}>
            <div className={classes.infoItem}>
              <div className={classes.infoLabel}>Username</div>
              <div className={classes.infoValue}>{profile.username}</div>
            </div>
            <div className={classes.infoItem}>
              <div className={classes.infoLabel}>WebSocket Endpoint</div>
              <div className={classes.infoValue}>{profile.websocket_url}</div>
            </div>
            <div className={classes.infoItem}>
              <div className={classes.infoLabel}>Domain</div>
              <div className={classes.infoValue}>{profile.domain}</div>
            </div>
            <div className={classes.infoItem}>
              <div className={classes.infoLabel}>Capabilities</div>
              <div className={classes.infoValue}>
                <Chip 
                  label={`${profile.capabilities.length} defined`} 
                  size="small" 
                  style={{ color: "#20a100", background: "rgba(32, 161, 0, 0.1)", fontWeight: 600 }}
                />
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
