import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

interface LogEntry {
  timestamp: string;
  category: string;
  user_request: string;
  llm_response: string;
  vulnerability_detected: boolean;
  vulnerability_type?: string;
  risk_level?: 'Low' | 'Medium' | 'High' | 'Critical';
}

interface HistoryItemSummary {
    id: string;
    filename: string;
    chatbot_name: string;
    date: string;
    total_vulnerabilities: number;
    duration: string;
}

interface Project {
    id: string;
    name: string;
    runs: HistoryItemSummary[];
}

interface Bucket {
    id: string;
    name: string;
    projects: Project[];
}

interface HistoryItemDetail extends HistoryItemSummary {
  vulnerability_score?: number;
  critical_count?: number;
  high_risk_count?: number;
  medium_risk_count?: number;
  categories: Record<string, number>;
  logs: LogEntry[];
}

const History: React.FC = () => {
  const navigate = useNavigate();
  const [buckets, setBuckets] = useState<Bucket[]>([]);
  const [selectedRun, setSelectedRun] = useState<HistoryItemDetail | null>(null);
  const [loadingList, setLoadingList] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false);
  const [expandedBuckets, setExpandedBuckets] = useState<Set<string>>(new Set());
  const [expandedProjects, setExpandedProjects] = useState<Set<string>>(new Set());
  
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8080";

  // Mock data for buckets and projects (matching profile library structure)
  const mockBuckets: Bucket[] = [
    {
      id: "bucket-1",
      name: "General",
      projects: [
        {
          id: "project-1",
          name: "E-Commerce Shopping Assistant",
          runs: [
            {
              id: "run-1",
              filename: "E-Commerce_Shopping_Assistant_20260128_143000.json",
              chatbot_name: "E-Commerce Shopping Assistant - 2026-01-28",
              date: "2026-01-28",
              total_vulnerabilities: 3,
              duration: "4m 12s"
            },
            {
              id: "run-2", 
              filename: "E-Commerce_Shopping_Assistant_20260129_091500.json",
              chatbot_name: "E-Commerce Shopping Assistant - 2026-01-29",
              date: "2026-01-29",
              total_vulnerabilities: 1,
              duration: "3m 45s"
            },
            {
              id: "run-3",
              filename: "E-Commerce_Shopping_Assistant_20260130_123549.json",
              chatbot_name: "E-Commerce Shopping Assistant - 2026-01-30",
              date: "2026-01-30",
              total_vulnerabilities: 0,
              duration: "3m 05s"
            }
          ]
        },
        {
          id: "project-2",
          name: "Ecommerce chat assistant",
          runs: [
            {
              id: "run-5",
              filename: "Ecommerce_chat_assistant_20260130_100000.json",
              chatbot_name: "Ecommerce chat assistant",
              date: "2026-01-30",
              total_vulnerabilities: 0,
              duration: "2m 45s"
            }
          ]
        },
        {
          id: "project-3",
          name: "Ecommerce Chatbot",
          runs: [
            {
              id: "run-6",
              filename: "Ecommerce_Chatbot_20260131_150000.json",
              chatbot_name: "Ecommerce Chatbot",
              date: "2026-01-31",
              total_vulnerabilities: 1,
              duration: "3m 20s"
            }
          ]
        }
      ]
    },
    {
      id: "bucket-2", 
      name: "FIS",
      projects: [
        {
          id: "project-4",
          name: "E-Commerce Shopping Assistant",
          runs: [
            {
              id: "run-7",
              filename: "FIS_E-Commerce_Shopping_Assistant_20260201_100000.json",
              chatbot_name: "E-Commerce Shopping Assistant - 2026-02-01",
              date: "2026-02-01",
              total_vulnerabilities: 2,
              duration: "4m 05s"
            },
            {
              id: "run-8",
              filename: "FIS_E-Commerce_Shopping_Assistant_20260131_153000.json",
              chatbot_name: "E-Commerce Shopping Assistant - 2026-01-31",
              date: "2026-01-31",
              total_vulnerabilities: 0,
              duration: "3m 22s"
            },
            {
              id: "run-9",
              filename: "FIS_E-Commerce_Shopping_Assistant_20260130_140000.json",
              chatbot_name: "E-Commerce Shopping Assistant - 2026-01-30",
              date: "2026-01-30",
              total_vulnerabilities: 1,
              duration: "4m 10s"
            }
          ]
        }
      ]
    },
    {
      id: "bucket-3", 
      name: "Downer",
      projects: [
        {
          id: "project-5",
          name: "Customer Support Bot",
          runs: [
            {
              id: "run-8",
              filename: "Downer_Support_Bot_20260202_090000.json",
              chatbot_name: "Customer Support Bot",
              date: "2026-02-02",
              total_vulnerabilities: 0,
              duration: "2m 30s"
            }
          ]
        }
      ]
    }
  ];

  // Load mock data
  useEffect(() => {
    // Simulate API loading
    setTimeout(() => {
      setBuckets(mockBuckets);
      setLoadingList(false);
      // Expand first bucket by default
      if (mockBuckets.length > 0) {
        setExpandedBuckets(new Set([mockBuckets[0].id]));
      }
    }, 500);
  }, []);

  // Fetch details when selection changes
  useEffect(() => {
    if (buckets.length > 0 && !selectedRun) {
      // Default to first run in first project of first bucket
      const firstBucket = buckets[0];
      if (firstBucket.projects.length > 0 && firstBucket.projects[0].runs.length > 0) {
        loadRun(firstBucket.projects[0].runs[0].filename);
      }
    }
  }, [buckets]);

  const loadRun = async (filename: string) => {
      try {
          const res = await fetch(`${API_BASE_URL}/api/history/${filename}`);
          if (res.ok) {
              const data = await res.json();
              // Ensure filename is preserved for context lookup
              setSelectedRun({ ...data, filename });
          }
      } catch (error) {
          console.error("Failed to fetch history detail", error);
      }
  };

  const filteredBuckets = buckets.filter(bucket => 
    bucket.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    bucket.projects.some(project => 
      project.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      project.runs.some(run => 
        run.chatbot_name.toLowerCase().includes(searchTerm.toLowerCase()) || 
        run.date.includes(searchTerm)
      )
    )
  );

  const toggleBucket = (bucketId: string) => {
    const newExpanded = new Set(expandedBuckets);
    if (newExpanded.has(bucketId)) {
      newExpanded.delete(bucketId);
    } else {
      newExpanded.add(bucketId);
    }
    setExpandedBuckets(newExpanded);
  };

  const toggleProject = (projectId: string) => {
    const newExpanded = new Set(expandedProjects);
    if (newExpanded.has(projectId)) {
      newExpanded.delete(projectId);
    } else {
      newExpanded.add(projectId);
    }
    setExpandedProjects(newExpanded);
  };

  // Helper to find context for selected run
  const getRunContext = () => {
    if (!selectedRun) return { bucketName: '', projectName: '' };
    
    for (const bucket of buckets) {
      for (const project of bucket.projects) {
        if (project.runs.some(r => r.filename === selectedRun.filename)) {
          return { bucketName: bucket.name, projectName: project.name };
        }
      }
    }
    return { bucketName: '', projectName: '' };
  };
  
  const { bucketName, projectName } = getRunContext();

  return (
    <div className="flex h-screen bg-white font-sans">
      {/* Sidebar - Consistent with ProfileSetup */}
      <aside className="w-56 bg-white border-r border-gray-300 flex flex-col pt-6 px-2 sticky top-0 h-screen justify-between pb-6">
        <div className="flex flex-col gap-6">
          {/* Logo and Title */}
          <div className="flex items-center gap-3 px-2">
            <div className="bg-[#0f62fe] w-8 h-8 rounded-xl flex items-center justify-center text-white shadow-md cursor-pointer" onClick={() => navigate('/')}> 
              <span className="material-symbols-outlined text-xl">shield</span>
            </div>
            <div className="flex flex-col cursor-pointer" onClick={() => navigate('/')}> 
              <h1 className="text-black text-[15px] font-bold leading-tight">Ai Risk Simulation</h1>
            </div>
          </div>
          {/* Back to Onboarding Button */}
          <button 
            onClick={() => navigate('/profile-setup')}
            className="flex items-center gap-2 px-3 py-2 mt-2 mx-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-gray-700 text-sm font-medium transition-colors"
          >
            <span className="material-symbols-outlined text-lg">arrow_back</span>
            <span>Back to Onboarding</span>
          </button>
        </div>

        {/* User Profile */}
        <div 
            className="mt-auto relative group"
            onMouseEnter={() => setIsProfileMenuOpen(true)}
            onMouseLeave={() => setIsProfileMenuOpen(false)}
        >
          <button 
            className="w-full bg-[#f9fafb] rounded-2xl p-4 flex items-center gap-3 border border-gray-100/50 group-hover:bg-gray-50 group-hover:border-[#0f62fe]/30 transition-all cursor-pointer text-left"
          >
            <div className="relative">
              <div className="w-10 h-10 rounded-full bg-gray-200 overflow-hidden ring-2 ring-white">
                <img src="https://ui-avatars.com/api/?name=Security+Analyst&background=e5e7eb&color=374151" alt="Profile" className="w-full h-full object-cover" />
              </div>
              <div className="absolute bottom-0 right-0 w-2.5 h-2.5 bg-[#0f62fe] rounded-full ring-2 ring-white"></div>
            </div>
            <div className="flex flex-col min-w-0">
              <p className="text-xs font-bold text-gray-900 truncate">Security Analyst</p>
              <p className="text-[10px] text-[#0f62fe] font-bold uppercase tracking-wide">Enterprise Node</p>
            </div>
             <span className="material-symbols-outlined ml-auto text-gray-400 text-lg group-hover:text-[#0f62fe] transition-colors">expand_less</span>
          </button>
          
           {isProfileMenuOpen && (
            <div className="absolute bottom-full left-0 w-64 mb-2 bg-white rounded-xl shadow-xl border border-gray-100 overflow-hidden z-20 animate-in fade-in slide-in-from-bottom-2">
              <div className="p-1">
                <button className="w-full flex items-center gap-3 px-3 py-3 hover:bg-[#edf5ff] rounded-lg text-left transition-colors group/item" onClick={() => navigate('/dashboard')}>
                  <span className="material-symbols-outlined text-gray-400 text-[20px] group-hover/item:text-[#0f62fe]">dashboard</span>
                  <span className="text-[14px] font-medium text-gray-700 group-hover/item:text-[#0f62fe]">Dashboard</span>
                </button>
                <button className="w-full flex items-center gap-3 px-3 py-3 hover:bg-[#edf5ff] rounded-lg text-left transition-colors group/item" onClick={() => navigate('/history')}>
                  <span className="material-symbols-outlined text-gray-400 text-[20px] group-hover/item:text-[#0f62fe]">history</span>
                  <span className="text-[14px] font-medium text-gray-700 group-hover/item:text-[#0f62fe]">History</span>
                </button>
              </div>
            </div>
           )}
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex overflow-hidden">
        {/* History List (Left Panel) */}
        <div className="w-80 bg-gray-50 border-r border-gray-200 flex flex-col z-10">
          <div className="p-5 border-b border-gray-200">
            <h2 className="text-2xl font-bold text-slate-700 mb-4 tracking-tight">Project History</h2>
            <div className="relative">
              <span className="material-symbols-outlined absolute left-3 top-2.5 text-gray-400 text-lg">search</span>
              <input 
                type="text" 
                placeholder="Search runs..." 
                className="w-full pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-[#0f62fe] transition-colors"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>
          
          <div className="flex-1 overflow-y-auto">
             {loadingList && <p className="p-4 text-sm text-gray-500">Loading history...</p>}
            {filteredBuckets.map(bucket => (
              <div key={bucket.id} className="border-b border-gray-100">
                {/* Bucket Header */}
                <div 
                  onClick={() => toggleBucket(bucket.id)}
                  className="p-4 bg-gray-50 border-l-4 border-l-gray-300 cursor-pointer hover:bg-gray-100 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <span className={`material-symbols-outlined text-lg transition-transform ${expandedBuckets.has(bucket.id) ? 'rotate-90' : ''}`}>chevron_right</span>
                    <div className="flex items-center gap-2">
                      <span className="material-symbols-outlined text-gray-500">folder</span>
                      <h3 className="text-sm font-bold text-slate-700">{bucket.name}</h3>
                    </div>
                    <span className="text-xs text-gray-500 bg-gray-200 px-2 py-1 rounded-full">
                      {bucket.projects.length} projects
                    </span>
                  </div>
                </div>

                {/* Projects */}
                {expandedBuckets.has(bucket.id) && bucket.projects.map(project => (
                  <div key={project.id} className="ml-4 border-l border-gray-200">
                    {/* Project Header */}
                    <div 
                      onClick={() => toggleProject(project.id)}
                      className="p-3 bg-gray-25 border-l-4 border-l-blue-300 cursor-pointer hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <span className={`material-symbols-outlined text-base transition-transform ${expandedProjects.has(project.id) ? 'rotate-90' : ''}`}>chevron_right</span>
                        <div className="flex items-center gap-2">
                          <span className="material-symbols-outlined text-blue-500">inventory_2</span>
                          <h4 className="text-sm font-semibold text-slate-700 text-left" style={{fontSize: '13px'}}>{project.name}</h4>
                        </div>
                        <span className="text-xs text-gray-500 bg-blue-100 px-2 py-1 rounded-full">
                          {project.runs.length} runs
                        </span>
                      </div>
                    </div>

                    {/* Runs */}
                    {expandedProjects.has(project.id) && project.runs.map(run => (
                      <div 
                        key={run.id}
                        onClick={() => loadRun(run.filename)}
                        className={`p-3 border-b border-gray-100 cursor-pointer transition-colors hover:bg-white ml-8 ${selectedRun?.id === run.id ? 'bg-white border-l-4 border-l-[#0f62fe] shadow-sm' : 'border-l-4 border-l-transparent text-gray-600'}`}
                        style={{paddingBottom: '4px'}}
                      >
                        <div className="flex justify-between items-center mb-2">
                          <div className="flex items-center gap-2 text-sm text-gray-500">
                            <span className="material-symbols-outlined text-[14px]">calendar_today</span>
                            {(() => {
                              const match = run.filename.match(/.*_(\d{8})_(\d{6})\.json$/);
                              if (match) {
                                const d = match[1], t = match[2];
                                const year = d.slice(0,4);
                                const month = d.slice(4,6);
                                const day = d.slice(6,8);
                                const hour = t.slice(0,2);
                                const min = t.slice(2,4);
                                const sec = t.slice(4,6);
                                return (
                                  <>
                                    <span className="font-semibold text-slate-700" style={{fontFamily: 'Inter, Arial, sans-serif', fontSize: '11px'}}>{`${year}-${month}-${day}`}</span>
                                    <span className="mx-1 text-gray-400" style={{fontSize: '11px'}}>|</span>
                                    <span className="font-semibold text-blue-700" style={{fontFamily: 'Inter, Arial, sans-serif', fontSize: '11px'}}>{`${hour}:${min}:${sec}`}</span>
                                  </>
                                );
                              }
                              return <span className="font-semibold" style={{fontSize: '11px'}}>{run.date}</span>;
                            })()}
                          </div>
                          {run.total_vulnerabilities > 0 ? (
                            <span className="bg-red-100 text-red-600 text-[10px] font-bold px-2 py-0.5 rounded-full border border-red-200">
                              {run.total_vulnerabilities} Vulns
                            </span>
                          ) : (
                             <span className="bg-green-100 text-green-600 text-[10px] font-bold px-2 py-0.5 rounded-full border border-green-200">
                              Safe
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>

        {/* Detail View (Right Panel) */}
        <div className="flex-1 flex flex-col overflow-hidden bg-white">
            {!selectedRun && (
                <div className="w-full h-full flex flex-col items-center justify-center text-gray-400">
                    <span className="material-symbols-outlined text-6xl mb-4">history_edu</span>
                    <p>Select a run to view details</p>
                </div>
            )}
            
            {selectedRun && (
            <>
            {/* Fixed Header & Stats */}
            <div className="flex-none px-8 pt-8 pb-6 border-b border-gray-100 shadow-[0_4px_20px_-10px_rgba(0,0,0,0.05)] z-10 bg-white">
                <header className="flex justify-between items-start mb-6">
                    <div>
                        <h1 className="text-[28px] font-bold text-slate-700 mb-2 tracking-tight">
                          {(bucketName && projectName) ? (
                            <>
                              <span className="text-gray-400 font-medium text-lg">{bucketName} <span className="text-gray-300 mx-1">/</span> </span>
                              {projectName}
                            </>
                          ) : (
                            selectedRun.chatbot_name
                          )}
                        </h1>
                        <div className="flex items-center gap-4 text-base text-gray-500">
                            <span className="flex items-center gap-1.5 bg-gray-50 border border-gray-200 px-3 py-1 rounded-md">
                                <span className="material-symbols-outlined text-base">event</span>
                                {selectedRun.date}
                            </span>
                        </div>
                    </div>
                </header>

                {/* Risk Score & Stats Grid */}
                <div className="grid grid-cols-5 gap-4 mb-6">
                    {/* Vulnerability Score - Light Theme */}
                    <div className="p-4 rounded-xl bg-white border border-gray-200 flex flex-col justify-between shadow-sm">
                        <div>
                             <p className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">Vulnerability Score</p>
                        </div>
                        <p className="text-3xl font-bold mt-2 text-[#0f62fe]">
                            {selectedRun.vulnerability_score !== undefined ? selectedRun.vulnerability_score.toFixed(1) : '0.0'}%
                        </p>
                    </div>

                    {/* Total Vulns */}
                    <div className={`p-4 rounded-xl border flex flex-col justify-between shadow-sm ${selectedRun.total_vulnerabilities > 0 ? 'bg-red-50 border-red-100' : 'bg-[#edf5ff] border-[#0f62fe]/30'}`}>
                        <p className="text-xs font-bold text-gray-500 uppercase tracking-wide">Total Vulnerabilities</p>
                        <p className={`text-3xl font-bold mt-2 ${selectedRun.total_vulnerabilities > 0 ? 'text-red-600' : 'text-[#0f62fe]'}`}>
                            {selectedRun.total_vulnerabilities}
                        </p>
                    </div>

                    {/* Critical */}
                    <div className="p-4 rounded-xl border border-gray-100 bg-white flex flex-col justify-between shadow-sm">
                         <p className="text-xs font-bold text-gray-500 uppercase tracking-wide flex items-center gap-1">
                            <span className="w-2 h-2 rounded-full bg-red-700"></span> Critical
                         </p>
                         <p className="text-3xl font-bold mt-2 text-gray-800">{selectedRun.critical_count || 0}</p>
                    </div>

                    {/* High */}
                    <div className="p-4 rounded-xl border border-gray-100 bg-white flex flex-col justify-between shadow-sm">
                         <p className="text-xs font-bold text-gray-500 uppercase tracking-wide flex items-center gap-1">
                            <span className="w-2 h-2 rounded-full bg-red-500"></span> High Risk
                         </p>
                         <p className="text-3xl font-bold mt-2 text-gray-800">{selectedRun.high_risk_count || 0}</p>
                    </div>

                    {/* Medium */}
                    <div className="p-4 rounded-xl border border-gray-100 bg-white flex flex-col justify-between shadow-sm">
                         <p className="text-xs font-bold text-gray-500 uppercase tracking-wide flex items-center gap-1">
                            <span className="w-2 h-2 rounded-full bg-orange-400"></span> Medium Risk
                         </p>
                         <p className="text-3xl font-bold mt-2 text-gray-800">{selectedRun.medium_risk_count || 0}</p>
                    </div>
                </div>


            </div>

            {/* Fixed Scrollable Logs Header */}
            <div className="px-8 pt-6 pb-2 bg-gray-50/30 flex-none">
                <h3 className="text-lg font-bold text-gray-800 flex items-center gap-2 px-1">
                    <span className="material-symbols-outlined text-[#0f62fe]">forum</span>
                    Attack Logs
                </h3>
            </div>

            {/* Scrollable Logs */}
            <div className="flex-1 overflow-y-auto px-8 pb-8 bg-gray-50/30">
                <div className="space-y-4">
                    {selectedRun.logs.map((log, index) => (
                        <div key={index} className={`rounded-xl border overflow-hidden bg-white ${log.vulnerability_detected ? 'border-red-200 shadow-sm' : 'border-gray-100'}`}>

                            {/* Header */}
                            <div className={`px-4 py-2 flex justify-between items-center text-xs font-medium border-b ${log.vulnerability_detected ? 'bg-red-50 border-red-100 text-red-700' : 'bg-gray-50 border-gray-100 text-gray-500'}`}>
                                <div className="flex items-center gap-3">
                                    <span>{log.category}</span>
                                </div>
                                {log.vulnerability_detected && (
                                    <span className="flex items-center gap-1 text-red-600 font-bold">
                                        <span className="material-symbols-outlined text-[16px]">warning</span>
                                        {log.vulnerability_type} ({log.risk_level})
                                    </span>
                                )}
                            </div>

                            {/* Conversation - User First, Then Chatbot */}
                            <div className="p-4 space-y-4">
                                {/* User Input - Right Side */}
                                <div className="flex gap-3 justify-end">
                                    <div className="flex-1 max-w-[70%] flex justify-end">
                                        <p className="text-sm text-gray-800 leading-relaxed bg-blue-50 p-3 rounded-2xl rounded-tr-none border border-blue-100 shadow-sm">
                                            {log.user_request}
                                        </p>
                                    </div>
                                    <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white flex-shrink-0">
                                         <span className="material-symbols-outlined text-[16px]">person</span>
                                    </div>
                                </div>

                                {/* AI Response - Left Side */}
                                <div className="flex gap-3">
                                     <div className="w-8 h-8 rounded-full bg-[#0f62fe] flex items-center justify-center text-white flex-shrink-0">
                                         <span className="material-symbols-outlined text-[16px]">smart_toy</span>
                                    </div>
                                    <div className="flex-1 max-w-[70%]">
                                        <div className={`text-sm leading-relaxed p-3 rounded-2xl rounded-tl-none text-left relative shadow-sm ${log.vulnerability_detected ? 'bg-red-50 text-red-900 border border-red-100' : 'bg-white text-gray-800 border border-gray-100'}`}>
                                            {log.llm_response}
                                            {log.vulnerability_detected && (
                                                <div className="mt-2 pt-2 border-t border-red-200/50 text-xs text-red-600 font-medium flex items-center gap-1">
                                                     <span className="material-symbols-outlined text-[14px]">flag</span>
                                                     Flagged as Unsafe
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
            </>
            )}
        </div>
      </main>
    </div>
  );
};

export default History;

