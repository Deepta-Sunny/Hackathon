import {
    Paper,
    Typography
} from "@mui/material";
import React from "react";
import { createUseStyles } from "react-jss";

const useStyles = createUseStyles({
  container: {
    border: '1px solid #20a100ff',
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
    borderBottom: '1px solid #00000010',
  },
  headerTitle: {
    fontWeight: 600,
    fontSize: "18px",
  },
});

const ReportsPanel: React.FC = () => {
  const classes = useStyles();

  return (
    <Paper className={classes.container} elevation={2}>
      <div className={classes.header}>
        <Typography fontFamily="inherit" className={classes.headerTitle}>
          Reports
        </Typography>
      </div>
    </Paper>
  );
};

export default ReportsPanel;