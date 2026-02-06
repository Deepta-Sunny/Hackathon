import React, { useEffect, useState, useCallback } from "react";
import {
  Box,
  Typography,
  LinearProgress,
  Chip,
  Paper,
  CircularProgress,
  Tooltip,
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
    display: "flex",
    alignItems: "center",
    gap: "16px",
    padding: "10px 14px",
    backgroundColor: "#f8f9fa",
    borderRadius: "6px",
    border: "1px solid #e0e0e0",
    minHeight: "fit-content",
  },
  scoreCircle: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
  },
  scoreCircleOuter: {
    width: "60px",
    height: "60px",
    borderRadius: "50%",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    position: "relative",
    flexShrink: 0,
  },
  scoreCircleInner: {
    width: "48px",
    height: "48px",
    borderRadius: "50%",
    backgroundColor: "#fff",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    boxShadow: "inset 0 1px 4px rgba(0,0,0,0.1)",
  },
  scoreValue: {
    fontSize: "14px",
    fontWeight: 700,
    lineHeight: 1,
  },
  scoreLabel: {
    fontSize: "10px",
    color: "#666",
    fontWeight: 500,
  },
  metricCard: {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    padding: "6px 10px",
    backgroundColor: "#fff",
    borderRadius: "4px",
    border: "1px solid #e0e0e0",
    flexShrink: 0,
  },
  metricValue: {
    fontSize: "16px",
    fontWeight: 700,
    lineHeight: 1,
  },
  metricLabel: {
    fontSize: "10px",
    color: "#666",
    fontWeight: 500,
    whiteSpace: "nowrap",
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
    gridTemplateColumns: "70px 1fr 130px 90px",
    alignItems: "center",
    gap: "14px",
    padding: "12px 16px",
    backgroundColor: "#fff",
    borderRadius: "6px",
    border: "1px solid #e0e0e0",
    transition: "all 0.2s",
    flexShrink: 0,
    "&:hover": {
      borderColor: "#0f62fe",
      boxShadow: "0 2px 8px rgba(15, 98, 254, 0.1)",
    },
  },
  categoryId: {
    fontSize: "12px",
    fontWeight: 600,
    color: "#0f62fe",
    backgroundColor: "#edf5ff",
    padding: "4px 8px",
    borderRadius: "4px",
    textAlign: "center",
  },
  categoryInfo: {
    display: "flex",
    flexDirection: "column",
    gap: "1px",
  },
  categoryName: {
    fontSize: "14px",
    fontWeight: 600,
    color: "#333",
  },
  categoryDescription: {
    fontSize: "11px",
    color: "#666",
    lineHeight: 1.3,
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
    fontSize: "12px",
    color: "#666",
    textAlign: "right",
  },
  statusChip: {
    fontWeight: 600,
    fontSize: "12px",
  },
  tooltip: {
    backgroundColor: "#fff !important",
    border: "1px solid #0f62fe",
    borderRadius: "4px",
    fontSize: "11px",
    padding: "10px 12px",
    boxShadow: "0 2px 8px rgba(0,0,0,0.15)",
    maxWidth: "280px",
  },
  tooltipArrow: {
    color: "#fff !important",
    "&::before": {
      border: "1px solid #0f62fe",
    },
  },
  tooltipContent: {
    display: "flex",
    flexDirection: "column",
    gap: "6px",
  },
  tooltipHeader: {
    fontSize: "12px",
    fontWeight: 700,
    color: "#0f62fe",
    marginBottom: "4px",
    borderBottom: "1px solid #e0e0e0",
    paddingBottom: "4px",
  },
  tooltipRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "16px",
    fontSize: "11px",
  },
  tooltipLabel: {
    color: "#666",
    display: "flex",
    alignItems: "center",
    gap: "6px",
  },
  tooltipValue: {
    fontWeight: 700,
    fontSize: "12px",
  },
  tooltipDot: {
    width: "8px",
    height: "8px",
    borderRadius: "50%",
    display: "inline-block",
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
    alignItems: "center",
    flexWrap: "wrap",
  },
  issueBadge: {
    fontSize: "9px",
    padding: "2px 6px",
    borderRadius: "3px",
    fontWeight: 600,
    lineHeight: 1.2,
  },
  divider: {
    width: "1px",
    height: "40px",
    backgroundColor: "#e0e0e0",
    flexShrink: 0,
  },
  metricsGroup: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    flex: 1,
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
          <Tooltip
            key={category.id}
            title={
              <Box className={classes.tooltipContent}>
                <Typography className={classes.tooltipHeader}>
                  {category.id} - Test Results
                </Typography>
                <Box className={classes.tooltipRow}>
                  <span className={classes.tooltipLabel}>
                    <span className={classes.tooltipDot} style={{ backgroundColor: "#66bb6a" }}></span>
                    Safe
                  </span>
                  <span className={classes.tooltipValue} style={{ color: "#66bb6a" }}>
                    {category.safe_count}
                  </span>
                </Box>
                <Box className={classes.tooltipRow}>
                  <span className={classes.tooltipLabel}>
                    <span className={classes.tooltipDot} style={{ backgroundColor: "#fbc02d" }}></span>
                    Medium
                  </span>
                  <span className={classes.tooltipValue} style={{ color: "#fbc02d" }}>
                    {category.medium_count}
                  </span>
                </Box>
                <Box className={classes.tooltipRow}>
                  <span className={classes.tooltipLabel}>
                    <span className={classes.tooltipDot} style={{ backgroundColor: "#f57c00" }}></span>
                    High
                  </span>
                  <span className={classes.tooltipValue} style={{ color: "#f57c00" }}>
                    {category.high_count}
                  </span>
                </Box>
                <Box className={classes.tooltipRow}>
                  <span className={classes.tooltipLabel}>
                    <span className={classes.tooltipDot} style={{ backgroundColor: "#d32f2f" }}></span>
                    Critical
                  </span>
                  <span className={classes.tooltipValue} style={{ color: "#d32f2f" }}>
                    {category.critical_count}
                  </span>
                </Box>
              </Box>
            }
            arrow
            placement="left"
            componentsProps={{
              tooltip: {
                className: classes.tooltip,
              },
              arrow: {
                className: classes.tooltipArrow,
              },
            }}
          >
            <Paper
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
          </Tooltip>
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
