import { Box, Paper, Chip } from "@mui/material";
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

type AttackStrategy = "all" | "standard" | "crescendo" | "skeleton_key" | "obfuscation";
type AttackMode = Exclude<AttackStrategy, "all">;

const ATTACK_STRATEGY_OPTIONS: { value: AttackMode; label: string }[] = [
  { value: "standard", label: "Standard" },
  { value: "crescendo", label: "Crescendo" },
  { value: "skeleton_key", label: "Skeleton Key" },
  { value: "obfuscation", label: "Obfuscation" },
];

const DEFAULT_ATTACK_STRATEGIES: AttackMode[] = ATTACK_STRATEGY_OPTIONS.map(
  (option) => option.value
);

const normalizeAttackStrategies = (profile: ChatbotProfile): AttackMode[] => {
  const validOptions = new Set<AttackMode>(DEFAULT_ATTACK_STRATEGIES);
  const profileStrategies = Array.isArray(profile.attack_strategies)
    ? profile.attack_strategies.filter(
        (strategy): strategy is AttackMode => validOptions.has(strategy as AttackMode)
      )
    : [];

  if (profileStrategies.length > 0) {
    return Array.from(new Set(profileStrategies));
  }

  if (profile.attack_strategy && profile.attack_strategy !== "all") {
    return [profile.attack_strategy];
  }

  return [...DEFAULT_ATTACK_STRATEGIES];
};

const ensureAttackStrategies = (profile: ChatbotProfile): ChatbotProfile => ({
  ...profile,
  attack_strategies: normalizeAttackStrategies(profile),
});

const useStyles = createUseStyles({
  profileCard: {
    padding: 10,
    paddingBottom: 14,
    marginBottom: 8,
    background: "#fff",
    color: "#222",
    borderRadius: 12,
    borderTop: "4px solid #0f62fe",
    boxShadow: "0 4px 20px rgba(0,0,0,0.05)",
    fontFamily: "sans-serif",
  },
  topRow: {
    display: "flex",
    alignItems: "center",
    flexWrap: "wrap",
    gap: 8,
  },
  metaBadge: {
    display: "flex",
    alignItems: "center",
    gap: 6,
    background: "#f9fafb",
    border: "1px solid #e5e7eb",
    borderRadius: 999,
    padding: "6px 10px",
    minHeight: 34,
  },
  metaLabel: {
    fontSize: 11,
    color: "#6b7280",
    fontFamily: "sans-serif",
    textTransform: "uppercase",
    letterSpacing: "0.4px",
    fontWeight: 600,
    whiteSpace: "nowrap",
  },
  metaValue: {
    fontSize: 13,
    fontWeight: 700,
    fontFamily: "sans-serif",
    color: "#222",
    maxWidth: 210,
    overflow: "hidden",
    textOverflow: "ellipsis",
    whiteSpace: "nowrap",
  },
  actionsWrap: {
    display: "flex",
    alignItems: "center",
    gap: 8,
    marginLeft: "auto",
  },
  strategyRow: {
    display: "flex",
    alignItems: "center",
    gap: 8,
    marginBottom: 8,
    borderBottom: "1px solid #eee",
    paddingBottom: 8,
    marginTop: 8,
  },
  strategyLabel: {
    fontSize: 11,
    color: "#6b7280",
    fontFamily: "sans-serif",
    textTransform: "uppercase",
    letterSpacing: "0.4px",
    fontWeight: 600,
    whiteSpace: "nowrap",
  },
  startButton: {
    background: "#0f62fe !important",
    color: "white !important",
    fontFamily: "sans-serif !important",
    fontWeight: "700 !important",
    padding: "6px 14px !important",
    minWidth: "96px",
    height: "34px",
    fontSize: "13px !important",
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
    padding: "6px 14px !important",
    minWidth: "96px",
    height: "34px",
    fontSize: "13px !important",
    borderRadius: "8px !important",
    border: "1px solid #e5e7eb !important",
    "&:hover": {
      background: "#e0e7ef !important",
      borderColor: "#0f62fe !important",
    },
  },
  strategySection: {
    marginTop: 0,
    background: "transparent",
    border: "none",
    borderRadius: 0,
    padding: 0,
  },
  strategyButtonsRow: {
    display: "flex",
    flexWrap: "nowrap",
    gap: 6,
    overflowX: "auto",
  },
  strategyButton: {
    minWidth: 110,
    height: 32,
    whiteSpace: "nowrap",
    fontFamily: "sans-serif !important",
    fontWeight: "700 !important",
    fontSize: "12px !important",
    borderRadius: "8px !important",
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
  attack_strategy?: AttackStrategy;
  attack_strategies?: AttackMode[];
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
          const normalizedProfile = ensureAttackStrategies(data.state);
          setProfile(normalizedProfile);
          sessionStorage.setItem("chatbotProfile", JSON.stringify(normalizedProfile));
          return;
        }
      } catch (error) {
        console.log("No saved dashboard state found, checking sessionStorage");
      }
      
      // Fallback to sessionStorage
      const savedProfile = sessionStorage.getItem("chatbotProfile");
      if (savedProfile) {
        setProfile(ensureAttackStrategies(JSON.parse(savedProfile)));
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
        const profileWithStrategies = ensureAttackStrategies(profile);
        setProfile(profileWithStrategies);
        try {
          // Save dashboard state before starting
          await fetch('http://localhost:8080/api/dashboard/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(profileWithStrategies)
          });
        } catch (error) {
          console.error("Failed to save dashboard state:", error);
        }
        
        // Open WebSocket monitor first
        await dispatch(openAttackMonitor());

        // Start testing with profile
        dispatch(initiateAttack(profileWithStrategies));
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

  const handleAttackStrategyToggle = (value: AttackMode) => {
    setProfile((currentProfile) => {
      if (!currentProfile) return currentProfile;
      const currentStrategies = normalizeAttackStrategies(currentProfile);
      const isSelected = currentStrategies.includes(value);
      const updatedStrategies = isSelected
        ? currentStrategies.filter((strategy) => strategy !== value)
        : [...currentStrategies, value];
      const finalStrategies =
        updatedStrategies.length > 0 ? updatedStrategies : currentStrategies;
      const updatedProfile = {
        ...currentProfile,
        attack_strategies: finalStrategies,
      };
      sessionStorage.setItem("chatbotProfile", JSON.stringify(updatedProfile));
      return updatedProfile;
    });
  };

  if (!profile) {
    return null; // Will redirect in useEffect
  }
  const selectedStrategies = normalizeAttackStrategies(profile);

  return (
    <Box>
      <Header />
      <Box display={"flex"} flexDirection={"column"} gap={2} marginTop={4}>
        {/* Profile Information Card */}
          <Paper className={classes.profileCard} elevation={8}>
          <div className={classes.topRow}>
            <div className={classes.metaBadge} title={profile.username || "-"}>
              <div className={classes.metaLabel}>Username</div>
              <div className={classes.metaValue}>{profile.username || "-"}</div>
            </div>
            <div
              className={classes.metaBadge}
              title={profile.websocket_url || "ws://localhost:8001/ws"}
            >
              <div className={classes.metaLabel}>WebSocket Endpoint</div>
              <div className={classes.metaValue}>
                {profile.websocket_url || "ws://localhost:8001/ws"}
              </div>
            </div>
            <div className={classes.metaBadge} title={profile.domain || "-"}>
              <div className={classes.metaLabel}>Domain</div>
              <div className={classes.metaValue}>{profile.domain || "-"}</div>
            </div>
            <div className={classes.metaBadge}>
              <div className={classes.metaLabel}>Capabilities</div>
              <div>
                <Chip 
                  label={`${profile.capabilities.length} defined`} 
                  size="small" 
                  style={{ color: "#0f62fe", background: "#edf5ff", fontWeight: 600 }}
                />
              </div>
            </div>
            <div className={classes.actionsWrap}>
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
          <div className={classes.strategySection}>
            <div className={classes.strategyRow}>
              <div className={classes.strategyLabel}>Testing Strategies</div>
              <div className={classes.strategyButtonsRow}>
              {ATTACK_STRATEGY_OPTIONS.map((option) => {
                const selected = selectedStrategies.includes(option.value);
                return (
                  <Button
                    key={option.value}
                    variant={selected ? "solid" : "outlined"}
                    color={selected ? "primary" : "neutral"}
                    className={classes.strategyButton}
                    disabled={attackStarted || isStarting}
                    onClick={() => handleAttackStrategyToggle(option.value)}
                  >
                    {option.label}
                  </Button>
                );
              })}
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
