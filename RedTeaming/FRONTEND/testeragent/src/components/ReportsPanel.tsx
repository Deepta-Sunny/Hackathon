import {
  Box,
  Paper,
  Typography,
} from "@mui/material";
import React, { useEffect, useState } from "react";
import { createUseStyles } from "react-jss";
import { useSelector } from "react-redux";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, RadialBarChart, RadialBar, PolarAngleAxis } from 'recharts';
import type { RootState } from "../store/Store";
import OwaspComplianceReport from "./OwaspComplianceReport";
import { mockVulnerabilityStats, mockTotalRiskDistribution, mockTotalTurns } from '../chatLogData';

const useStyles = createUseStyles({
  container: {
    border: '1px solid #0f62fe',
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
    backgroundColor: "#edf5ff",
    color: "#0f62fe",
    boxShadow: "0 10px 10px rgba(0, 0, 0, 0.1)",
    textAlign: "left",
    borderBottom: '1px solid #00000010',
  },
  headerTitle: {
    fontWeight: 600,
    fontSize: "14px",
  },
  content: {
    flex: 1,
    padding: "20px",
    overflowY: "auto",
    display: "flex",
    flexDirection: "column",
    gap: "20px",
  },
  statsContainer: {
    display: "grid",
    gridTemplateColumns: "140px 1fr",
    gridTemplateRows: "auto auto",
    gap: "10px",
    marginBottom: "4px",
  },
  statsRow: {
    display: "flex",
    gap: "10px",
  },
  statCard: {
    flex: "1 1 120px",
    padding: "10px",
    backgroundColor: "#f8f9fa",
    borderRadius: "6px",
    border: "1px solid #e0e0e0",
    textAlign: "center",
  },
  statValue: {
    fontSize: "28px",
    fontWeight: 900,
    color: "#0f62fe",
    marginBottom: "2px",
  },
  statLabel: {
    fontSize: "10px",
    color: "#666",
    textTransform: "uppercase",
    letterSpacing: "0.5px",
  },
  chartContainer: {
    flex: 1,
    minHeight: "300px",
  },
  chartTitle: {
    fontSize: "12px",
    fontWeight: 600,
    color: "#333",
    marginBottom: "8px",
  },
  circularScoreContainer: {
    gridRow: "1 / 3",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    padding: "10px",
    backgroundColor: "#f8f9fa",
    borderRadius: "6px",
    border: "1px solid #e0e0e0",
  },
  scoreLabel: {
    fontSize: "10px",
    color: "#666",
    textTransform: "uppercase",
    letterSpacing: "0.5px",
    marginTop: "8px",
  },
  scoreSubtext: {
    fontSize: "10px",
    color: "#999",
    marginTop: "4px",
  },
});

const ReportsPanel: React.FC = () => {
  const classes = useStyles();
  const { monitorSocket } = useSelector((state: RootState) => state.api);
  
  // Toggle state for Overall vs OWASP view
  const [activeView, setActiveView] = useState<'overall' | 'owasp'>('overall');
  
  // Track vulnerabilities by category, run, and risk level
  const [vulnerabilityStats, setVulnerabilityStats] = useState<{
    crescendo: { 
      run1: { critical: number; high: number; medium: number; safe: number };
      run2: { critical: number; high: number; medium: number; safe: number };
      run3: { critical: number; high: number; medium: number; safe: number };
    };
    skeleton_key: { 
      run1: { critical: number; high: number; medium: number; safe: number };
      run2: { critical: number; high: number; medium: number; safe: number };
      run3: { critical: number; high: number; medium: number; safe: number };
    };
    obfuscation: { 
      run1: { critical: number; high: number; medium: number; safe: number };
      run2: { critical: number; high: number; medium: number; safe: number };
      run3: { critical: number; high: number; medium: number; safe: number };
    };
    standard: { 
      run1: { critical: number; high: number; medium: number; safe: number };
      run2: { critical: number; high: number; medium: number; safe: number };
      run3: { critical: number; high: number; medium: number; safe: number };
    };
  }>(mockVulnerabilityStats);
  
  // Track total risk distribution across all categories
  const [totalRiskDistribution, setTotalRiskDistribution] = useState(mockTotalRiskDistribution);

  // Track total number of turns for score calculation
  const [totalTurns, setTotalTurns] = useState(mockTotalTurns);

  useEffect(() => {
    if (!monitorSocket) {
      return;
    }

    const handleMessage = (event: MessageEvent) => {
      try {
        const payload = JSON.parse(event.data) as {
          type: string;
          data?: Record<string, unknown>;
        };

        console.log('[ReportsPanel] WebSocket message received:', payload.type, payload.data?.category);
        
        // Reset stats when attack starts
        if (payload.type === "attack_started") {
          setVulnerabilityStats({
            crescendo: { 
              run1: { critical: 0, high: 0, medium: 0, safe: 0 },
              run2: { critical: 0, high: 0, medium: 0, safe: 0 },
              run3: { critical: 0, high: 0, medium: 0, safe: 0 }
            },
            skeleton_key: { 
              run1: { critical: 0, high: 0, medium: 0, safe: 0 },
              run2: { critical: 0, high: 0, medium: 0, safe: 0 },
              run3: { critical: 0, high: 0, medium: 0, safe: 0 }
            },
            obfuscation: { 
              run1: { critical: 0, high: 0, medium: 0, safe: 0 },
              run2: { critical: 0, high: 0, medium: 0, safe: 0 },
              run3: { critical: 0, high: 0, medium: 0, safe: 0 }
            },
            standard: { 
              run1: { critical: 0, high: 0, medium: 0, safe: 0 },
              run2: { critical: 0, high: 0, medium: 0, safe: 0 },
              run3: { critical: 0, high: 0, medium: 0, safe: 0 }
            }
          });
          setTotalRiskDistribution({ critical: 0, high: 0, medium: 0, safe: 0 });
          setTotalTurns(0);
          return;
        }

        // Update stats on turn completion
        if (payload.type === "turn_completed" && payload.data) {
          const data = payload.data;
          const category = String(data.category || "").toLowerCase();
          const run = Number(data.run || 0);
          const riskCategory = Number(data.risk_category || 1);

          // Increment total turns
          setTotalTurns((prev) => prev + 1);

          if (category in vulnerabilityStats && run >= 1 && run <= 3) {
            // Update run-specific risk level count
            setVulnerabilityStats((prev) => {
              const updated = { ...prev };
              const categoryKey = category as keyof typeof vulnerabilityStats;
              const runKey = `run${run}` as 'run1' | 'run2' | 'run3';
              
              const runStats = { ...updated[categoryKey][runKey] };
              
              // Increment the appropriate risk level
              // Backend risk categories: 1=SAFE, 2=MEDIUM, 3=HIGH, 4=CRITICAL
              if (riskCategory === 4) {
                runStats.critical += 1;
              } else if (riskCategory === 3) {
                runStats.high += 1;
              } else if (riskCategory === 2) {
                runStats.medium += 1;
              } else {
                runStats.safe += 1;
              }
              
              updated[categoryKey] = {
                ...updated[categoryKey],
                [runKey]: runStats
              };
              
              return updated;
            });
            
            // Update total risk distribution
            setTotalRiskDistribution((prev) => {
              const updated = { ...prev };
              if (riskCategory === 4) {
                updated.critical += 1;
              } else if (riskCategory === 3) {
                updated.high += 1;
              } else if (riskCategory === 2) {
                updated.medium += 1;
              } else {
                updated.safe += 1;
              }
              return updated;
            });
          }
        }
      } catch (error) {
        console.warn("Failed to parse report message", error);
      }
    };

    monitorSocket.addEventListener("message", handleMessage);
    
    return () => {
      monitorSocket.removeEventListener("message", handleMessage);
    };
  }, [monitorSocket]);  // FIXED: Removed vulnerabilityStats to prevent duplicate listeners

  // Calculate vulnerability score (Critical=3, High=2, Medium=1, Safe=0)
  // Score is now based on total number of prompts (turns), not just vulnerabilities
  const totalVulnerabilities = totalRiskDistribution.critical + totalRiskDistribution.high + totalRiskDistribution.medium;
  const vulnerabilityPoints = (totalRiskDistribution.critical * 3) + 
                              (totalRiskDistribution.high * 2) + 
                              (totalRiskDistribution.medium * 1);
  // Max possible points is totalTurns * 3 (if every prompt was critical)
  const maxPossiblePoints = totalTurns * 3;
  const vulnerabilityScore = maxPossiblePoints > 0 ? ((vulnerabilityPoints / maxPossiblePoints) * 100).toFixed(1) : '0.0';

  // Flatten chart data to show 3 bars per category (one for each run)
  // Maintain execution order: Standard, Crescendo, Skeleton Key, Obfuscation
  const chartData: any[] = [];
  const categoryOrder = ['standard', 'crescendo', 'skeleton_key', 'obfuscation'];
  
  categoryOrder.forEach((categoryKey) => {
    const runs = vulnerabilityStats[categoryKey as keyof typeof vulnerabilityStats];
    const categoryName = categoryKey.replace('_', ' ').toUpperCase();
    
    // Add Run 1 bar
    chartData.push({
      category: `${categoryName} - Run 1`,
      critical: runs.run1.critical,
      high: runs.run1.high,
      medium: runs.run1.medium,
      safe: runs.run1.safe
    });
    
    // Add Run 2 bar
    chartData.push({
      category: `${categoryName} - Run 2`,
      critical: runs.run2.critical,
      high: runs.run2.high,
      medium: runs.run2.medium,
      safe: runs.run2.safe
    });
    
    // Add Run 3 bar
    chartData.push({
      category: `${categoryName} - Run 3`,
      critical: runs.run3.critical,
      high: runs.run3.high,
      medium: runs.run3.medium,
      safe: runs.run3.safe
    });
  });

  // Calculate totals from risk distribution (already calculated above in vulnerabilityScore section)
  const totalCritical = totalRiskDistribution.critical;
  const totalHigh = totalRiskDistribution.high;
  const totalMedium = totalRiskDistribution.medium;

  return (
    <Paper className={classes.container} elevation={2}>
      <Box className={classes.header}>
        <Box style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography fontFamily="inherit" className={classes.headerTitle}>
            Vulnerability Reports
          </Typography>
          
          {/* Toggle Button */}
          <Box style={{ display: 'flex', gap: '8px', backgroundColor: '#ffffff', borderRadius: '8px', padding: '4px', border: '1px solid #0f62fe' }}>
            <button
              onClick={() => setActiveView('overall')}
              style={{
                padding: '6px 12px',
                border: 'none',
                borderRadius: '6px',
                backgroundColor: activeView === 'overall' ? '#0f62fe' : 'transparent',
                color: activeView === 'overall' ? '#ffffff' : '#0f62fe',
                fontWeight: 600,
                fontSize: '11px',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                fontFamily: 'inherit'
              }}
            >
              Overall Vulnerability Report
            </button>
            <button
              onClick={() => setActiveView('owasp')}
              style={{
                padding: '6px 12px',
                border: 'none',
                borderRadius: '6px',
                backgroundColor: activeView === 'owasp' ? '#0f62fe' : 'transparent',
                color: activeView === 'owasp' ? '#ffffff' : '#0f62fe',
                fontWeight: 600,
                fontSize: '11px',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                fontFamily: 'inherit'
              }}
            >
              OWASP Compliance Report
            </button>
          </Box>
        </Box>
      </Box>
      
      <Box className={classes.content}>
        {/* Overall Vulnerability Report View */}
        {activeView === 'overall' && (
        <>
        {/* Summary Statistics */}
        <Box className={classes.statsContainer}>
          {/* Circular Progress Bar for Vulnerability Score - Column 1, Row span 2 */}
          <Box className={classes.circularScoreContainer}>
            <ResponsiveContainer width={100} height={100}>
              <RadialBarChart 
                cx="50%" 
                cy="50%" 
                innerRadius="70%" 
                outerRadius="100%" 
                barSize={10}
                data={[{
                  name: 'Score',
                  value: parseFloat(vulnerabilityScore),
                  fill: parseFloat(vulnerabilityScore) > 66.6 ? '#d32f2f' : parseFloat(vulnerabilityScore) > 33.3 ? '#f57c00' : '#66bb6a'
                }]}
                startAngle={90}
                endAngle={-270}
              >
                <PolarAngleAxis type="number" domain={[0, 100]} angleAxisId={0} tick={false} />
                <RadialBar
                  background={{ fill: '#e0e0e0' }}
                  dataKey="value"
                  cornerRadius={8}
                />
                <text
                  x="50%"
                  y="50%"
                  textAnchor="middle"
                  dominantBaseline="middle"
                  style={{
                    fontSize: '20px',
                    fontWeight: 900,
                    fill: parseFloat(vulnerabilityScore) > 66.6 ? '#d32f2f' : parseFloat(vulnerabilityScore) > 33.3 ? '#f57c00' : '#388e3c'
                  }}
                >
                  {vulnerabilityScore}%
                </text>
              </RadialBarChart>
            </ResponsiveContainer>
            <Typography className={classes.scoreLabel}>
              Vulnerability Score
            </Typography>
          </Box>

          {/* Column 2, Row 1 - Total Vulnerabilities */}
          <Box className={classes.statCard}>
            <Typography className={classes.statValue}>
              {totalVulnerabilities}
            </Typography>
            <Typography className={classes.statLabel}>
              Total Vulnerabilities
            </Typography>
          </Box>
          
          {/* Column 2, Row 2 - Risk Counts */}
          <Box className={classes.statsRow}>
            <Box className={classes.statCard} style={{ flex: 1 }}>
              <Typography className={classes.statValue} style={{ color: '#d32f2f' }}>
                {totalCritical}
              </Typography>
              <Typography className={classes.statLabel} style={{ textAlign: 'center' }}>
                Critical
              </Typography>
            </Box>
            
            <Box className={classes.statCard} style={{ flex: 1 }}>
              <Typography className={classes.statValue} style={{ color: '#f57c00' }}>
                {totalHigh}
              </Typography>
              <Typography className={classes.statLabel} style={{ color: '#ff6b6b', textAlign: 'center' }}>
                HIGH
              </Typography>
            </Box>
            
            <Box className={classes.statCard} style={{ flex: 1 }}>
              <Typography className={classes.statValue} style={{ color: '#fbc02d' }}>
                {totalMedium}
              </Typography>
              <Typography className={classes.statLabel} style={{ textAlign: 'center' }}>
                Medium Risk
              </Typography>
            </Box>
          </Box>
        </Box>
        
        {/* Vulnerability Chart by Attack Category and Run */}
        <Box className={classes.chartContainer}>
          <Typography className={classes.chartTitle}>
            Vulnerabilities by Attack Category & Run (Real-Time)
          </Typography>
          <ResponsiveContainer width="100%" height="90%">
            <BarChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="category" 
                style={{ fontSize: '8px', fontFamily: 'inherit' }}
                angle={-45}
                textAnchor="end"
                height={100}
                interval={0}
              />
              <YAxis style={{ fontSize: '9px', fontFamily: 'inherit' }} allowDecimals={false} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#fff', 
                  border: '1px solid #0f62fe',
                  borderRadius: '4px',
                  fontFamily: 'inherit'
                }}
              />
              <Legend wrapperStyle={{ fontFamily: 'inherit', fontSize: '9px' }} />
              <Bar dataKey="critical" stackId="a" fill="#d32f2f" name="Critical" />
              <Bar dataKey="high" stackId="a" fill="#f57c00" name="High" />
              <Bar dataKey="medium" stackId="a" fill="#fbc02d" name="Medium" />
              <Bar dataKey="safe" stackId="a" fill="#66bb6a" name="Safe" />
            </BarChart>
          </ResponsiveContainer>
        </Box>
        </>
        )}
        
        {/* OWASP Compliance Report View */}
        {activeView === 'owasp' && (
          <OwaspComplianceReport />
        )}
      </Box>
    </Paper>
  );
};

export default ReportsPanel;