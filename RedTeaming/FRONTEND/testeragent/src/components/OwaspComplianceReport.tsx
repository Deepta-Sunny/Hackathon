import React, { useEffect, useState, useCallback } from "react";
import {
  Box,
  Typography,
  LinearProgress,
  Chip,
  Paper,
  CircularProgress,
} from "@mui/material";
import { createUseStyles } from "react-jss";

const API_BASE_URL = "http://localhost:8080";

// OWASP Category interface
interface OwaspCategory {
  id: string;
  name: string;
  description: string;
  total_tests: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  safe_count: number;
  compliance_percentage: number;
  status: "PASSED" | "REVIEW" | "FAILED";
}

// Summary interface
interface OwaspSummary {
  total_tests: number;
  tests_passed: number;
  tests_failed: number;
  critical_issues: number;
  high_issues: number;
  medium_issues: number;
  overall_compliance: number;
  overall_status: "PASSED" | "REVIEW" | "FAILED";
  risk_level: "HIGH RISK" | "MODERATE RISK" | "LOW RISK";
  last_updated: string;
}

// Full report interface
interface OwaspReport {
  summary: OwaspSummary;
  categories: OwaspCategory[];
}

const useStyles = createUseStyles({
  container: {
    display: "flex",
    flexDirection: "column",
    gap: "12px",
    padding: "8px",
    height: "100%",
  },
  heroCard: {
    display: "grid",
    gridTemplateColumns: "140px 1fr 1fr 1fr",
    gap: "12px",
    padding: "12px 16px",
    backgroundColor: "#f8f9fa",
    borderRadius: "8px",
    border: "1px solid #e0e0e0",
    minHeight: "fit-content",
  },
  scoreCircle: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    position: "relative",
  },
  scoreCircleOuter: {
    width: "100px",
    height: "100px",
    borderRadius: "50%",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    position: "relative",
  },
  scoreCircleInner: {
    width: "76px",
    height: "76px",
    borderRadius: "50%",
    backgroundColor: "#fff",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    boxShadow: "inset 0 2px 8px rgba(0,0,0,0.1)",
  },
  scoreValue: {
    fontSize: "16px",
    fontWeight: "bold",
    lineHeight: 1,
  },
  scoreLabel: {
    fontSize: "8px",
    color: "#666",
    marginTop: "2px",
  },
  metricCard: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    padding: "8px 12px",
    backgroundColor: "#fff",
    borderRadius: "6px",
    border: "1px solid #e0e0e0",
    transition: "box-shadow 0.2s",
    "&:hover": {
      boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
    },
  },
  metricValue: {
    fontSize: "18px",
    fontWeight: "bold",
    marginBottom: "2px",
  },
  metricLabel: {
    fontSize: "9px",
    color: "#666",
    textTransform: "uppercase",
    letterSpacing: "0.5px",
    textAlign: "center",
  },
  categoryList: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    gap: "6px",
    overflowY: "auto",
    minHeight: 0,
  },
  categoryCard: {
    display: "grid",
    gridTemplateColumns: "55px 1fr 100px 70px",
    alignItems: "center",
    gap: "10px",
    padding: "8px 12px",
    backgroundColor: "#fff",
    borderRadius: "5px",
    border: "1px solid #e0e0e0",
    transition: "all 0.2s",
    flexShrink: 0,
    "&:hover": {
      borderColor: "#0f62fe",
      boxShadow: "0 2px 8px rgba(15, 98, 254, 0.1)",
    },
  },
  categoryId: {
    fontSize: "10px",
    fontWeight: 600,
    color: "#0f62fe",
    backgroundColor: "#edf5ff",
    padding: "2px 6px",
    borderRadius: "3px",
    textAlign: "center",
  },
  categoryInfo: {
    display: "flex",
    flexDirection: "column",
    gap: "1px",
  },
  categoryName: {
    fontSize: "11px",
    fontWeight: 600,
    color: "#333",
  },
  categoryDescription: {
    fontSize: "9px",
    color: "#666",
    lineHeight: 1.2,
  },
  categoryProgress: {
    display: "flex",
    flexDirection: "column",
    gap: "1px",
  },
  progressBar: {
    height: "5px",
    borderRadius: "2px",
    backgroundColor: "#e0e0e0",
  },
  progressText: {
    fontSize: "8px",
    color: "#666",
    textAlign: "right",
  },
  statusChip: {
    fontWeight: 600,
    fontSize: "9px",
  },
  loadingContainer: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    minHeight: "400px",
    gap: "16px",
  },
  errorContainer: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    minHeight: "400px",
    gap: "16px",
    color: "#d32f2f",
  },
  noDataContainer: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    minHeight: "400px",
    gap: "16px",
  },
  issuesBadges: {
    display: "flex",
    gap: "4px",
    marginTop: "2px",
    flexWrap: "wrap",
  },
  issueBadge: {
    fontSize: "9px",
    padding: "1px 5px",
    borderRadius: "3px",
    fontWeight: 500,
  },
});

// Helper function to get status chip color
const getStatusColor = (status: string): "success" | "warning" | "error" => {
  switch (status) {
    case "PASSED":
      return "success";
    case "REVIEW":
      return "warning";
    case "FAILED":
      return "error";
    default:
      return "warning";
  }
};

// Helper function to get risk level color
const getRiskColor = (risk: string): string => {
  switch (risk) {
    case "LOW RISK":
      return "#4caf50";
    case "MODERATE RISK":
      return "#ff9800";
    case "HIGH RISK":
      return "#d32f2f";
    default:
      return "#666";
  }
};

// Helper function to get score circle gradient
const getScoreGradient = (score: number): string => {
  if (score >= 85) {
    return "linear-gradient(135deg, #4caf50, #81c784)";
  } else if (score >= 60) {
    return "linear-gradient(135deg, #ff9800, #ffb74d)";
  } else {
    return "linear-gradient(135deg, #d32f2f, #ef5350)";
  }
};

// Helper function to get score text color
const getScoreColor = (score: number): string => {
  if (score >= 85) {
    return "#2e7d32";
  } else if (score >= 60) {
    return "#e65100";
  } else {
    return "#c62828";
  }
};

// Helper to get progress bar color
const getProgressColor = (percentage: number): "success" | "warning" | "error" => {
  if (percentage >= 85) return "success";
  if (percentage >= 60) return "warning";
  return "error";
};

const OwaspComplianceReport: React.FC = () => {
  const classes = useStyles();
  const [report, setReport] = useState<OwaspReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchReport = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/owasp/report`);
      if (!response.ok) {
        throw new Error(`Failed to fetch OWASP report: ${response.statusText}`);
      }
      const data = await response.json();
      setReport(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error occurred");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchReport();
    
    // Poll for updates every 5 seconds
    const interval = setInterval(fetchReport, 5000);
    
    return () => clearInterval(interval);
  }, [fetchReport]);

  if (loading) {
    return (
      <Box className={classes.loadingContainer}>
        <CircularProgress style={{ color: "#0f62fe" }} />
        <Typography style={{ color: "#666" }}>
          Loading OWASP Compliance Report...
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box className={classes.errorContainer}>
        <span style={{ fontSize: "48px" }}>⚠️</span>
        <Typography style={{ fontWeight: 600, fontSize: "18px" }}>
          Error Loading Report
        </Typography>
        <Typography style={{ color: "#666", textAlign: "center", maxWidth: "400px" }}>
          {error}
        </Typography>
        <button
          onClick={() => {
            setLoading(true);
            fetchReport();
          }}
          style={{
            padding: "8px 24px",
            backgroundColor: "#0f62fe",
            color: "#fff",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
            fontSize: "14px",
            fontWeight: 600,
          }}
        >
          Retry
        </button>
      </Box>
    );
  }

  if (!report || report.summary.total_tests === 0) {
    return (
      <Box className={classes.noDataContainer}>
        <span style={{ fontSize: "64px" }}>🔍</span>
        <Typography style={{ fontWeight: 600, fontSize: "20px", color: "#333" }}>
          No Test Data Available
        </Typography>
        <Typography style={{ color: "#666", textAlign: "center", maxWidth: "400px" }}>
          Run attack tests to generate OWASP LLM Top 10 compliance data.
          Results will appear here automatically.
        </Typography>
      </Box>
    );
  }

  const { summary, categories } = report;

  return (
    <Box className={classes.container}>
      {/* Hero Card with Overall Score */}
      <Paper className={classes.heroCard} elevation={0}>
        {/* Circular Score */}
        <Box className={classes.scoreCircle}>
          <Box
            className={classes.scoreCircleOuter}
            style={{ background: getScoreGradient(summary.overall_compliance) }}
          >
            <Box className={classes.scoreCircleInner}>
              <Typography
                className={classes.scoreValue}
                style={{ color: getScoreColor(summary.overall_compliance) }}
              >
                {summary.overall_compliance.toFixed(1)}%
              </Typography>
              <Typography className={classes.scoreLabel}>
                Compliance
              </Typography>
            </Box>
          </Box>
          <Chip
            label={summary.risk_level}
            size="small"
            style={{
              marginTop: "8px",
              backgroundColor: getRiskColor(summary.risk_level),
              color: "#fff",
              fontWeight: 600,
              fontSize: "10px",
              height: "20px",
            }}
          />
        </Box>

        {/* Tests Passed */}
        <Box className={classes.metricCard}>
          <Typography
            className={classes.metricValue}
            style={{ color: "#4caf50" }}
          >
            {summary.tests_passed}
          </Typography>
          <Typography className={classes.metricLabel}>
            Tests Passed
          </Typography>
        </Box>

        {/* Tests Failed */}
        <Box className={classes.metricCard}>
          <Typography
            className={classes.metricValue}
            style={{ color: "#d32f2f" }}
          >
            {summary.tests_failed}
          </Typography>
          <Typography className={classes.metricLabel}>
            Tests Failed
          </Typography>
        </Box>

        {/* Issues Breakdown */}
        <Box className={classes.metricCard}>
          <Typography
            className={classes.metricValue}
            style={{ color: "#333" }}
          >
            {summary.total_tests}
          </Typography>
          <Typography className={classes.metricLabel}>
            Total Tests
          </Typography>
          <Box className={classes.issuesBadges}>
            {summary.critical_issues > 0 && (
              <span
                className={classes.issueBadge}
                style={{ backgroundColor: "#ffebee", color: "#c62828" }}
              >
                {summary.critical_issues} Critical
              </span>
            )}
            {summary.high_issues > 0 && (
              <span
                className={classes.issueBadge}
                style={{ backgroundColor: "#fff3e0", color: "#e65100" }}
              >
                {summary.high_issues} High
              </span>
            )}
            {summary.medium_issues > 0 && (
              <span
                className={classes.issueBadge}
                style={{ backgroundColor: "#fffde7", color: "#f9a825" }}
              >
                {summary.medium_issues} Medium
              </span>
            )}
          </Box>
        </Box>
      </Paper>

      {/* Category Title */}
      <Typography
        style={{
          fontSize: "14px",
          fontWeight: 600,
          color: "#333",
          marginTop: "4px",
        }}
      >
        OWASP LLM Top 10 Categories
      </Typography>

      {/* Category List */}
      <Box className={classes.categoryList}>
        {categories.map((category) => (
          <Paper
            key={category.id}
            className={classes.categoryCard}
            elevation={0}
          >
            {/* Category ID Badge */}
            <Typography className={classes.categoryId}>
              {category.id}
            </Typography>

            {/* Category Info */}
            <Box className={classes.categoryInfo}>
              <Typography className={classes.categoryName}>
                {category.name}
              </Typography>
              <Typography className={classes.categoryDescription}>
                {category.description}
              </Typography>
            </Box>

            {/* Progress Bar */}
            <Box className={classes.categoryProgress}>
              <LinearProgress
                variant="determinate"
                value={category.compliance_percentage}
                className={classes.progressBar}
                color={getProgressColor(category.compliance_percentage)}
              />
              <Typography className={classes.progressText}>
                {category.compliance_percentage.toFixed(1)}% ({category.total_tests} tests)
              </Typography>
            </Box>

            {/* Status Chip */}
            <Chip
              label={category.status}
              color={getStatusColor(category.status)}
              size="small"
              className={classes.statusChip}
            />
          </Paper>
        ))}
      </Box>

      {/* Last Updated */}
      <Typography
        style={{
          fontSize: "11px",
          color: "#999",
          textAlign: "center",
          marginTop: "auto",
        }}
      >
        Last updated: {new Date(summary.last_updated).toLocaleString()}
        {" • "}
        Auto-refreshes every 5 seconds
      </Typography>
    </Box>
  );
};

export default OwaspComplianceReport;
