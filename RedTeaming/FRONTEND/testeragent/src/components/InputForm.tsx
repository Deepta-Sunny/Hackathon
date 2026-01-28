import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import StopIcon from "@mui/icons-material/Stop";
import Button from "@mui/joy/Button";
import { Box, TextField, Typography, Select, MenuItem, FormControl, InputLabel, IconButton } from "@mui/material";
import AddCircleOutlineIcon from "@mui/icons-material/AddCircleOutline";
import RemoveCircleOutlineIcon from "@mui/icons-material/RemoveCircleOutline";
import React, { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { createUseStyles } from "react-jss";
import type { AppDispatch, RootState } from "../store/Store";
import { haltAttack, openAttackMonitor } from "../thunk/ApiThunk";

const useStyles = createUseStyles({
  container: {
    padding: 20,
    borderRadius: 10,
    width: "100%",
    boxSizing: "border-box",
    boxShadow: "0 10px 20px rgba(0, 0, 0, 0.1)",
    border: "1px solid #20a100ff",
    maxHeight: "80vh",
    overflowY: "auto",
  },
  formSection: {
    marginBottom: 20,
    padding: 15,
    background: "#f8f9fa",
    borderRadius: 8,
    borderLeft: "4px solid #20a100ff",
  },
  sectionTitle: {
    color: "#20a100ff",
    fontSize: "16px",
    fontWeight: 600,
    marginBottom: 12,
    fontFamily: "monospace",
  },
  formGroup: {
    marginBottom: 16,
  },
  label: {
    display: "block",
    color: "#34495e",
    fontWeight: 600,
    marginBottom: 8,
    fontSize: 14,
    fontFamily: "monospace",
  },
  textField: {
    width: "100%",
    fontFamily: "monospace",
    "& .MuiOutlinedInput-root": {
      "&:hover fieldset": {
        borderColor: "#20a100ff",
      },
      "&.Mui-focused fieldset": {
        borderColor: "#20a100ff",
      },
    },
  },
  capabilityItem: {
    display: "flex",
    gap: 8,
    alignItems: "center",
    marginBottom: 8,
  },
  addButton: {
    background: "#27ae60",
    color: "white",
    "&:hover": {
      background: "#229954",
    },
  },
  submitSection: {
    display: "flex",
    gap: 12,
    marginTop: 24,
  },
  startButton: {
    flex: 1,
    height: 48,
    background: "#20a100ff",
    fontFamily: "monospace",
    "&:hover": {
      background: "#1e8f00ff",
    },
  },
  stopButton: {
    flex: 1,
    height: 48,
    background: "#e74c3c",
    fontFamily: "monospace",
    "&:hover": {
      background: "#c0392b",
    },
  },
  helpText: {
    fontSize: 12,
    color: "#7f8c8d",
    marginTop: 4,
    fontStyle: "italic",
    fontFamily: "monospace",
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

interface InputFormProps {
  onSubmit?: (profile: ChatbotProfile) => void;
}

const InputForm: React.FC<InputFormProps> = ({ onSubmit }) => {
  const classes = useStyles();
  const dispatch = useDispatch<AppDispatch>();
  const {
    monitorSocket,
    monitorOpen,
    monitorConnecting,
    startAttack: startAttackState,
    stopAttack: stopAttackState,
  } = useSelector((state: RootState) => state.api);

  // Form state
  const [username, setUsername] = useState("");
  const [websocketUrl, setWebsocketUrl] = useState(import.meta.env.VITE_DEFAULT_TARGET_WS || "ws://localhost:8001/ws");
  const [domain, setDomain] = useState("");
  const [primaryObjective, setPrimaryObjective] = useState("");
  const [intendedAudience, setIntendedAudience] = useState("");
  const [chatbotRole, setChatbotRole] = useState("");
  const [capabilities, setCapabilities] = useState<string[]>([""]);
  const [boundaries, setBoundaries] = useState("");
  const [communicationStyle, setCommunicationStyle] = useState("");
  const [contextAwareness, setContextAwareness] = useState("maintains_context");

  const addCapability = () => {
    setCapabilities([...capabilities, ""]);
  };

  const removeCapability = (index: number) => {
    if (capabilities.length > 1) {
      setCapabilities(capabilities.filter((_, i) => i !== index));
    }
  };

  const updateCapability = (index: number, value: string) => {
    const updated = [...capabilities];
    updated[index] = value;
    setCapabilities(updated);
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    
    const profile: ChatbotProfile = {
      username,
      websocket_url: websocketUrl,
      domain,
      primary_objective: primaryObjective,
      intended_audience: intendedAudience,
      chatbot_role: chatbotRole,
      capabilities: capabilities.filter(c => c.trim() !== ""),
      boundaries,
      communication_style: communicationStyle,
      context_awareness: contextAwareness,
    };

    if (onSubmit) {
      if (!monitorOpen && !monitorConnecting) {
        void dispatch(openAttackMonitor());
      }
      onSubmit(profile);
    }
  };

  const handleStop = () => {
    dispatch(haltAttack());
    monitorSocket?.close(1000, "User requested stop");
  };

  const isFormValid = username && websocketUrl && domain && primaryObjective && 
                      intendedAudience && chatbotRole && capabilities.some(c => c.trim() !== "") &&
                      boundaries && communicationStyle;

  const buttonDisabled = monitorOpen
    ? stopAttackState.loading
    : startAttackState.loading || monitorConnecting || !isFormValid;

  return (
    <Box className={classes.container}>
      <form onSubmit={handleSubmit}>
        {/* User Information */}
        <div className={classes.formSection}>
          <Typography className={classes.sectionTitle}>🎯 User Information</Typography>
          <div className={classes.formGroup}>
            <label className={classes.label}>Username *</label>
            <TextField
              className={classes.textField}
              size="small"
              placeholder="Enter your username (e.g., john_doe)"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              inputProps={{ style: { fontFamily: "monospace" } }}
            />
            <div className={classes.helpText}>Your username for report identification</div>
          </div>
        </div>

        {/* Target Endpoint */}
        <div className={classes.formSection}>
          <Typography className={classes.sectionTitle}>🔗 Target Chatbot Endpoint</Typography>
          <div className={classes.formGroup}>
            <label className={classes.label}>WebSocket URL *</label>
            <TextField
              className={classes.textField}
              size="small"
              placeholder="ws://localhost:8001/chat"
              value={websocketUrl}
              onChange={(e) => setWebsocketUrl(e.target.value)}
              required
              inputProps={{ style: { fontFamily: "monospace" } }}
            />
            <div className={classes.helpText}>WebSocket endpoint for the target chatbot</div>
          </div>
        </div>

        {/* Domain & Purpose */}
        <div className={classes.formSection}>
          <Typography className={classes.sectionTitle}>📋 Domain & Purpose</Typography>
          <div className={classes.formGroup}>
            <label className={classes.label}>Domain *</label>
            <FormControl fullWidth size="small">
              <Select
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
                required
                style={{ fontFamily: "monospace" }}
              >
                <MenuItem value="">-- Select Domain --</MenuItem>
                <MenuItem value="E-commerce">E-commerce</MenuItem>
                <MenuItem value="Healthcare">Healthcare</MenuItem>
                <MenuItem value="Finance">Finance</MenuItem>
                <MenuItem value="Education">Education</MenuItem>
                <MenuItem value="Customer Support">Customer Support</MenuItem>
                <MenuItem value="HR/Recruitment">HR/Recruitment</MenuItem>
                <MenuItem value="Travel">Travel</MenuItem>
                <MenuItem value="Legal">Legal</MenuItem>
                <MenuItem value="Other">Other</MenuItem>
              </Select>
            </FormControl>
            <div className={classes.helpText}>The industry/domain the chatbot operates in</div>
          </div>
          <div className={classes.formGroup}>
            <label className={classes.label}>Primary Objective *</label>
            <TextField
              className={classes.textField}
              size="small"
              multiline
              rows={3}
              placeholder="Describe what the chatbot is designed to achieve..."
              value={primaryObjective}
              onChange={(e) => setPrimaryObjective(e.target.value)}
              required
              inputProps={{ style: { fontFamily: "monospace" } }}
            />
            <div className={classes.helpText}>What problem does this chatbot solve?</div>
          </div>
        </div>

        {/* Audience & Role */}
        <div className={classes.formSection}>
          <Typography className={classes.sectionTitle}>👥 Audience & Role</Typography>
          <div className={classes.formGroup}>
            <label className={classes.label}>Intended Audience *</label>
            <TextField
              className={classes.textField}
              size="small"
              placeholder="e.g., Customers, Patients, Students, Employees"
              value={intendedAudience}
              onChange={(e) => setIntendedAudience(e.target.value)}
              required
              inputProps={{ style: { fontFamily: "monospace" } }}
            />
            <div className={classes.helpText}>Who are the primary users?</div>
          </div>
          <div className={classes.formGroup}>
            <label className={classes.label}>Chatbot Role/Persona *</label>
            <TextField
              className={classes.textField}
              size="small"
              placeholder="e.g., Helpful Assistant, Customer Service Agent"
              value={chatbotRole}
              onChange={(e) => setChatbotRole(e.target.value)}
              required
              inputProps={{ style: { fontFamily: "monospace" } }}
            />
            <div className={classes.helpText}>How does the chatbot present itself?</div>
          </div>
        </div>

        {/* Capabilities */}
        <div className={classes.formSection}>
          <Typography className={classes.sectionTitle}>✅ Capabilities (What the Chatbot CAN Do)</Typography>
          <div className={classes.formGroup}>
            <label className={classes.label}>List all functions and tasks *</label>
            <div className={classes.helpText} style={{ marginBottom: 12 }}>
              Add each capability separately - be comprehensive!
            </div>
            {capabilities.map((capability, index) => (
              <div key={index} className={classes.capabilityItem}>
                <TextField
                  className={classes.textField}
                  size="small"
                  placeholder="e.g., Provide product recommendations"
                  value={capability}
                  onChange={(e) => updateCapability(index, e.target.value)}
                  required
                  inputProps={{ style: { fontFamily: "monospace" } }}
                />
                <IconButton
                  onClick={() => removeCapability(index)}
                  disabled={capabilities.length === 1}
                  color="error"
                  size="small"
                >
                  <RemoveCircleOutlineIcon />
                </IconButton>
              </div>
            ))}
            <Button
              variant="solid"
              className={classes.addButton}
              startDecorator={<AddCircleOutlineIcon />}
              onClick={addCapability}
              sx={{ mt: 1, fontFamily: "monospace" }}
            >
              Add Capability
            </Button>
          </div>
        </div>

        {/* Boundaries */}
        <div className={classes.formSection}>
          <Typography className={classes.sectionTitle}>🚫 Boundaries & Limitations</Typography>
          <div className={classes.formGroup}>
            <label className={classes.label}>What the Chatbot SHOULD NOT Do *</label>
            <TextField
              className={classes.textField}
              size="small"
              multiline
              rows={3}
              placeholder="List restrictions, off-limit topics, and functional boundaries..."
              value={boundaries}
              onChange={(e) => setBoundaries(e.target.value)}
              required
              inputProps={{ style: { fontFamily: "monospace" } }}
            />
            <div className={classes.helpText}>Define what actions/topics are forbidden</div>
          </div>
        </div>

        {/* Behavioral Guidelines */}
        <div className={classes.formSection}>
          <Typography className={classes.sectionTitle}>💬 Behavioral Guidelines</Typography>
          <div className={classes.formGroup}>
            <label className={classes.label}>Communication Style *</label>
            <TextField
              className={classes.textField}
              size="small"
              placeholder="e.g., Professional, Friendly, Concise, Empathetic"
              value={communicationStyle}
              onChange={(e) => setCommunicationStyle(e.target.value)}
              required
              inputProps={{ style: { fontFamily: "monospace" } }}
            />
            <div className={classes.helpText}>How should the chatbot communicate?</div>
          </div>
          <div className={classes.formGroup}>
            <label className={classes.label}>Context/Memory Management</label>
            <FormControl fullWidth size="small">
              <Select
                value={contextAwareness}
                onChange={(e) => setContextAwareness(e.target.value)}
                style={{ fontFamily: "monospace" }}
              >
                <MenuItem value="maintains_context">Maintains context across conversation</MenuItem>
                <MenuItem value="stateless">Stateless (no memory)</MenuItem>
                <MenuItem value="limited_memory">Limited memory (last N messages)</MenuItem>
              </Select>
            </FormControl>
            <div className={classes.helpText}>Does the chatbot remember previous interactions?</div>
          </div>
        </div>

        {/* Submit Section */}
        <div className={classes.submitSection}>
          <Button
            type={monitorOpen ? "button" : "submit"}
            variant="solid"
            color="primary"
            startDecorator={monitorOpen ? <StopIcon /> : <PlayArrowIcon />}
            className={monitorOpen ? classes.stopButton : classes.startButton}
            disabled={buttonDisabled}
            onClick={monitorOpen ? handleStop : undefined}
          >
            {monitorOpen ? "Stop Attack" : "Start Attack Campaign"}
          </Button>
        </div>
      </form>
    </Box>
  );
};

export default InputForm;
