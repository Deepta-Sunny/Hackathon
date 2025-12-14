import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import Button from "@mui/joy/Button";
import { Box, TextField, Typography } from "@mui/material";
import React, { useRef, useState } from "react";
import { createUseStyles } from "react-jss";

const useStyles = createUseStyles({
  container: {
    padding: 10,
    borderRadius: 10,
    width: "100%",
    boxSizing: "border-box",
    boxShadow: "0 10px 20px rgba(0, 0, 0, 0.1)",
    border: "1px solid #20a100ff",
  },
  formWrapper: {
    display: "flex",
    alignItems: "center",
    gap: "16px",
    flexWrap: "wrap",
    "@media (max-width: 768px)": {
      flexDirection: "column",
      alignItems: "stretch",
    },
  },
  uploadSection: {
    display: "flex",
    alignItems: "center",
    gap: "12px",
  },
  hiddenInput: {
    display: "none",
  },
  uploadButton: {
    minWidth: "140px",
    background: "#dbdbdbff",
    color: "#20a100ff",
    boxShadow: "0 10px 20px rgba(0, 0, 0, 0.1)",
    "&:hover": {
      background: "#c0c0c0ff",
    },
  },
  fileName: {
    color: "#6b7280",
    fontSize: "14px",
    maxWidth: "200px",
    overflow: "hidden",
    textOverflow: "ellipsis",
    whiteSpace: "nowrap",
  },
  textFieldWrapper: {
    flex: 1,
    color: "#ffffffff",
    minWidth: "200px",
    "& .MuiOutlinedInput-root": {
      "&:hover fieldset": {
        borderColor: "#20a100ff",
      },
      "&.Mui-focused fieldset": {
        borderColor: "#20a100ff",
      },
    },
    "@media (max-width: 768px)": {
      width: "100%",
    },
  },
  startButton: {
    minWidth: "120px",
    height: "40px",
    background: "#20a100ff",
    "&:hover": {
      background: "#1e8f00ff",
    },
  },
});

interface InputFormProps {
  onSubmit?: (data: { file: File | null; query: string }) => void;
}

const InputForm: React.FC<InputFormProps> = ({ onSubmit }) => {
  const classes = useStyles();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [query, setQuery] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] || null;
    setSelectedFile(file);
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (onSubmit) {
      onSubmit({ file: selectedFile, query });
    }
  };

  return (
    <Box className={classes.container}>
      <form onSubmit={handleSubmit}>
        <div className={classes.formWrapper}>
          <div className={classes.uploadSection}>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileSelect}
              className={classes.hiddenInput}
              accept=".pdf,.doc,.docx,.txt,.csv"
            />
            <Button
              variant="solid"
              startDecorator={<CloudUploadIcon />}
              onClick={handleUploadClick}
              className={classes.uploadButton}
            >
              <Typography
                variant="subtitle2"
                color={"#20a100ff"}
                fontFamily="monospace"
                fontWeight={500}
              >
                Upload .md
              </Typography>
            </Button>
            {selectedFile && (
              <Typography fontFamily="inherit" className={classes.fileName}>
                {selectedFile.name}
              </Typography>
            )}
          </div>

          <div className={classes.textFieldWrapper}>
            <TextField
              inputProps={{ style: { fontFamily: "inherit" } }}
              fullWidth
              size="small"
              variant="outlined"
              placeholder="api endpoint"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>

          <Button
            type="submit"
            variant="solid"
            color="primary"
            sx={{ fontFamily: "inherit" }}
            startDecorator={<PlayArrowIcon />}
            className={classes.startButton}
          >
            Start
          </Button>
        </div>
      </form>
    </Box>
  );
};

export default InputForm;
