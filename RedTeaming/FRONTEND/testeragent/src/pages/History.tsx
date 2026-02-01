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
  const [historyList, setHistoryList] = useState<HistoryItemSummary[]>([]);
  const [selectedRun, setSelectedRun] = useState<HistoryItemDetail | null>(null);
  const [loadingList, setLoadingList] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8080";

  // Fetch list of history items
  useEffect(() => {
      const fetchHistory = async () => {
          try {
              const res = await fetch(`${API_BASE_URL}/api/history`);
              if (res.ok) {
                  const data = await res.json();
                  setHistoryList(data.history || []);
              }
          } catch (error) {
              console.error("Failed to fetch history list", error);
          } finally {
              setLoadingList(false);
          }
      };
      fetchHistory();
  }, []);

  // Fetch details when selection changes (or default to first one)
  useEffect(() => {
    if (historyList.length > 0 && !selectedRun) {
        // Default to first
        loadRun(historyList[0].filename);
    }
  }, [historyList]);

  const loadRun = async (filename: string) => {
      try {
          const res = await fetch(`${API_BASE_URL}/api/history/${filename}`);
          if (res.ok) {
              const data = await res.json();
              setSelectedRun(data);
          }
      } catch (error) {
          console.error("Failed to fetch history detail", error);
      }
  };

  const filteredHistory = historyList.filter(h => 
    h.chatbot_name.toLowerCase().includes(searchTerm.toLowerCase()) || 
    h.date.includes(searchTerm)
  );

  return (
    <div className="flex h-screen bg-white font-sans">
      {/* Sidebar - Consistent with ProfileSetup */}
      <aside className="w-56 bg-white border-r border-gray-300 flex flex-col pt-6 px-2 sticky top-0 h-screen">
        <div className="flex flex-col gap-6">
          {/* Logo */}
          <div className="flex items-center gap-3 px-2 cursor-pointer" onClick={() => navigate('/')}>
            <div className="bg-[#17cf54] w-8 h-8 rounded-xl flex items-center justify-center text-white shadow-md">
              <span className="material-symbols-outlined text-xl">shield</span>
            </div>
            <div className="flex flex-col">
              <h1 className="text-black text-[14px] font-bold leading-tight">Red Teaming</h1>
              <p className="text-gray-400 text-[9px] font-bold tracking-wider uppercase mt-0.5">Orchestrator v2.0</p>
            </div>
          </div>

          <div className="px-2">
            <button 
              onClick={() => navigate('/')}
              className="w-full flex items-center gap-3 px-3 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors text-sm font-medium"
            >
              <span className="material-symbols-outlined text-[20px]">arrow_back</span>
             Back to Setup
            </button>
            <button 
                onClick={() => navigate('/dashboard')}
                className="w-full flex items-center gap-3 px-3 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors text-sm font-medium mt-1"
            >
                <span className="material-symbols-outlined text-[20px]">dashboard</span>
                Dashboard
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex overflow-hidden">
        {/* History List (Left Panel) */}
        <div className="w-80 bg-gray-50 border-r border-gray-200 flex flex-col z-10">
          <div className="p-5 border-b border-gray-200">
            <h2 className="text-lg font-bold text-gray-800 mb-4">Attack History</h2>
            <div className="relative">
              <span className="material-symbols-outlined absolute left-3 top-2.5 text-gray-400 text-lg">search</span>
              <input 
                type="text" 
                placeholder="Search runs..." 
                className="w-full pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-[#17cf54] transition-colors"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>
          
          <div className="flex-1 overflow-y-auto">
             {loadingList && <p className="p-4 text-sm text-gray-500">Loading history...</p>}
            {filteredHistory.map(run => (
              <div 
                key={run.id}
                onClick={() => loadRun(run.filename)}
                className={`p-4 border-b border-gray-100 cursor-pointer transition-colors hover:bg-white ${selectedRun?.id === run.id ? 'bg-white border-l-4 border-l-[#17cf54] shadow-sm' : 'border-l-4 border-l-transparent text-gray-600'}`}
              >
                <div className="flex justify-between items-start mb-1">
                  <h3 className={`text-sm font-bold ${selectedRun?.id === run.id ? 'text-gray-900' : 'text-gray-700'}`}>{run.chatbot_name}</h3>
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
                <div className="flex items-center gap-2 text-xs text-gray-400 mt-2">
                  <span className="material-symbols-outlined text-[14px]">calendar_today</span>
                  {run.date}
                </div>
                 <div className="flex items-center gap-2 text-xs text-gray-400 mt-1">
                  <span className="material-symbols-outlined text-[14px]">timer</span>
                  {run.duration}
                </div>
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
                        <h1 className="text-2xl font-bold text-gray-900 mb-2">{selectedRun.chatbot_name}</h1>
                        <div className="flex items-center gap-4 text-sm text-gray-500">
                            <span className="flex items-center gap-1.5 bg-gray-50 border border-gray-200 px-3 py-1 rounded-md">
                                <span className="material-symbols-outlined text-sm">event</span>
                                {selectedRun.date}
                            </span>
                            <span className="flex items-center gap-1.5 bg-gray-50 border border-gray-200 px-3 py-1 rounded-md">
                                <span className="material-symbols-outlined text-sm">schedule</span>
                                {selectedRun.duration}
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
                             <p className="text-[10px] text-gray-400">(C=3pts, H=2pts, M=1pt)</p>
                        </div>
                        <p className="text-3xl font-bold mt-2 text-[#17cf54]">
                            {selectedRun.vulnerability_score !== undefined ? selectedRun.vulnerability_score.toFixed(1) : '0.0'}%
                        </p>
                    </div>

                    {/* Total Vulns */}
                    <div className={`p-4 rounded-xl border flex flex-col justify-between shadow-sm ${selectedRun.total_vulnerabilities > 0 ? 'bg-red-50 border-red-100' : 'bg-[#f0fdf4] border-[#17cf54]/30'}`}>
                        <p className="text-xs font-bold text-gray-500 uppercase tracking-wide">Total Vulnerabilities</p>
                        <p className={`text-3xl font-bold mt-2 ${selectedRun.total_vulnerabilities > 0 ? 'text-red-600' : 'text-[#17cf54]'}`}>
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

                {/* Category Breakdown */}
                <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">Category Breakdown</h4>
                <div className="grid grid-cols-4 gap-4">
                    {Object.entries(selectedRun.categories).map(([category, count]) => (
                        <div key={category} className={`p-3 rounded-xl border ${count > 0 ? 'bg-red-50 border-red-100' : 'bg-gray-50 border-gray-100'}`}>
                            <p className="text-[11px] font-bold text-gray-500 uppercase truncate mb-1" title={category}>{category}</p>
                            <p className={`text-lg font-bold ${count > 0 ? 'text-red-600' : 'text-gray-700'}`}>{count}</p>
                        </div>
                    ))}
                </div>
            </div>

            {/* Scrollable Logs */}
            <div className="flex-1 overflow-y-auto p-8 bg-gray-50/30">
                <h3 className="text-lg font-bold text-gray-800 mb-5 flex items-center gap-2 px-1">
                    <span className="material-symbols-outlined text-[#17cf54]">forum</span>
                    Attack Logs
                </h3>
                
                <div className="space-y-4">
                    {selectedRun.logs.map((log, index) => (
                        <div key={index} className={`rounded-xl border overflow-hidden bg-white ${log.vulnerability_detected ? 'border-red-200 shadow-sm' : 'border-gray-100'}`}>

                            {/* Header */}
                            <div className={`px-4 py-2 flex justify-between items-center text-xs font-medium border-b ${log.vulnerability_detected ? 'bg-red-50 border-red-100 text-red-700' : 'bg-gray-50 border-gray-100 text-gray-500'}`}>
                                <div className="flex items-center gap-3">
                                    <span>{log.timestamp}</span>
                                    <span className="w-px h-3 bg-gray-300/50"></span>
                                    <span>{log.category}</span>
                                </div>
                                {log.vulnerability_detected && (
                                    <span className="flex items-center gap-1 text-red-600 font-bold">
                                        <span className="material-symbols-outlined text-[16px]">warning</span>
                                        {log.vulnerability_type} ({log.risk_level})
                                    </span>
                                )}
                            </div>

                            {/* Conversation */}
                            <div className="p-4 space-y-6">
                                {/* User Input - Aligned Right */}
                                <div className="flex gap-4 flex-row-reverse">
                                    <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 flex-shrink-0 mt-1">
                                         <span className="material-symbols-outlined text-[16px]">person</span>
                                    </div>
                                    <div className="flex-1 text-right">
                                        <p className="text-xs font-bold text-blue-600 mb-1">Attacker (User)</p>
                                        <p className="text-sm text-gray-800 leading-relaxed bg-blue-50 p-3 rounded-2xl rounded-tr-none inline-block border border-blue-100 text-left shadow-sm">
                                            {log.user_request}
                                        </p>
                                    </div>
                                </div>

                                {/* AI Response - Aligned Left */}
                                <div className="flex gap-4">
                                     <div className="w-8 h-8 rounded-full bg-[#17cf54]/20 flex items-center justify-center text-[#17cf54] flex-shrink-0 mt-1">
                                         <span className="material-symbols-outlined text-[16px]">smart_toy</span>
                                    </div>
                                    <div className="flex-1">
                                        <p className="text-xs font-bold text-gray-400 mb-1">Target AI</p>
                                        <div className={`text-sm leading-relaxed p-3 rounded-2xl rounded-tl-none inline-block text-left relative shadow-sm ${log.vulnerability_detected ? 'bg-red-50 text-red-900 border border-red-100' : 'bg-white text-gray-800 border border-gray-100'}`}>
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
