import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";

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
  agent_type?: string;
  context_awareness: string;
  backend_integration?: string;
  training_context?: string;
  bucket_name?: string;
}

const ProfileSetup = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const mainRef = useRef<HTMLDivElement | null>(null);
  const section1Ref = useRef<HTMLElement | null>(null);
  const section2Ref = useRef<HTMLElement | null>(null);
  const section3Ref = useRef<HTMLElement | null>(null);
  const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false);

  const [username, setUsername] = useState("");
  const [websocketUrl, setWebsocketUrl] = useState("ws://localhost:8001/ws");
  const [domain, setDomain] = useState("");
  const [primaryObjective, setPrimaryObjective] = useState("");
  const [intendedAudience, setIntendedAudience] = useState("");
  const [chatbotRole, setChatbotRole] = useState("");
  const [agentType, setAgentType] = useState("");
  const [capabilities, setCapabilities] = useState<string[]>([""]);
  const [newCapability, setNewCapability] = useState("");
  const [boundaries, setBoundaries] = useState("");
  const [communicationStyle, setCommunicationStyle] = useState("");

  // Bucket State
  const [showLibrary, setShowLibrary] = useState(false);
  const [buckets, setBuckets] = useState<string[]>([]);
  const [selectedBucket, setSelectedBucket] = useState<string>("");
  const [bucketFiles, setBucketFiles] = useState<{name: string, created: number}[]>([]);
  const [newBucketName, setNewBucketName] = useState("");
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8080";

  const fetchBuckets = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/buckets`);
      const data = await res.json();
      setBuckets(data.buckets || []);
    } catch (e) {
      console.error("Error fetching buckets:", e);
    }
  };

  const createBucket = async () => {
    if (!newBucketName.trim()) return;
    try {
      const formData = new FormData();
      formData.append("bucket_name", newBucketName);
      const res = await fetch(`${API_BASE_URL}/api/buckets`, {
        method: "POST",
        body: formData
      });
      if (res.ok) {
         setNewBucketName("");
         fetchBuckets();
      }
    } catch (e) {
      console.error("Error creating bucket:", e);
    }
  };

  const fetchBucketFiles = async (bucket: string) => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/buckets/${bucket}/files`);
      if (res.ok) {
        const data = await res.json();
        setBucketFiles(data.files || []);
      }
    } catch (e) {
      console.error("Error fetching files:", e);
    }
  };

  const loadProfile = async (filename: string) => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/buckets/${selectedBucket}/files/${filename}`);
      if (res.ok) {
         const profile = await res.json();
            setUsername(profile.username || "");
            setWebsocketUrl(profile.websocket_url || "ws://localhost:8001/ws");
            setDomain(profile.domain || "");
            setPrimaryObjective(profile.primary_objective || "");
            setIntendedAudience(profile.intended_audience || "");
            setChatbotRole(profile.chatbot_role || "");
            setAgentType(profile.agent_type || "");
            setCapabilities(profile.capabilities || [""]);
            setBoundaries(profile.boundaries || "");
            setCommunicationStyle(profile.communication_style || "");
            setShowLibrary(false);
      }
    } catch (e) {
      console.error("Error loading profile:", e);
    }
  };

  useEffect(() => {
     if (showLibrary) {
        fetchBuckets();
     }
  }, [showLibrary]);

  useEffect(() => {
     if (selectedBucket) {
        fetchBucketFiles(selectedBucket);
     } else {
        setBucketFiles([]);
     }
  }, [selectedBucket]);

  const toggleCapability = (cap: string) => {
    const exists = capabilities.find((c) => c.toLowerCase() === cap.toLowerCase());
    if (exists) {
      setCapabilities(capabilities.filter((c) => c.toLowerCase() !== cap.toLowerCase()));
    } else {
      setCapabilities([...capabilities.filter((c) => c.trim() !== ""), cap]);
    }
  };

  const addCustomCapability = () => {
    const val = newCapability.trim();
    if (!val) return;
    if (capabilities.find((c) => c.toLowerCase() === val.toLowerCase())) {
      setNewCapability("");
      return;
    }
    setCapabilities([...capabilities.filter((c) => c.trim() !== ""), val]);
    setNewCapability("");
  };

  const removeCapability = (index: number) => {
    setCapabilities(capabilities.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const profile: ChatbotProfile = {
      username,
      websocket_url: websocketUrl,
      domain,
      primary_objective: primaryObjective,
      intended_audience: intendedAudience,
      chatbot_role: chatbotRole || username,
      agent_type: agentType,
      capabilities: capabilities.filter((c) => c.trim() !== ""),
      boundaries,
      communication_style: communicationStyle,
      context_awareness: "maintains_context",
      bucket_name: selectedBucket // Save to selected bucket if any
    };

    // Save profile to sessionStorage for dashboard
    sessionStorage.setItem("chatbotProfile", JSON.stringify(profile));
    
    // Send profile to backend and start orchestration
    try {
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8080";
      const response = await fetch(`${API_BASE_URL}/api/attack/start-with-profile`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(profile),
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log("✅ Profile sent to backend:", data);
        // Navigate to dashboard to monitor orchestration
        navigate("/dashboard");
      } else {
        const error = await response.json();
        console.error("❌ Failed to start orchestration:", error);
        alert(`Failed to start orchestration: ${error.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error("❌ Error sending profile to backend:", error);
      alert(`Error connecting to backend: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  const handleScroll = () => {
    const container = mainRef.current;
    if (!container) return;

    // Use the vertical midpoint of the visible container to determine which
    // section is currently in view. This is more robust than offsetTop heuristics.
    const containerRect = container.getBoundingClientRect();
    const midY = containerRect.top + container.clientHeight / 2;

    const refs = [section1Ref.current, section2Ref.current, section3Ref.current];
    let active = 1;
    for (let i = 0; i < refs.length; i++) {
      const r = refs[i];
      if (!r) continue;
      const rect = r.getBoundingClientRect();
      if (rect.top <= midY && rect.bottom >= midY) {
        active = i + 1;
        break;
      }
    }
    setCurrentStep(active);
  };

  useEffect(() => {
    // initialize active step after mount
    handleScroll();
    // also attach resize listener to recalc if window size changes
    const onResize = () => handleScroll();
    window.addEventListener('resize', onResize);
    fetchBuckets(); // Fetch buckets on mount
    return () => window.removeEventListener('resize', onResize);
  }, []);



  return (
    <div className="flex h-screen overflow-hidden bg-white font-['Inter']">
      {/* Sidebar */}
      <aside className="w-56 bg-white border-r border-gray-300 flex flex-col justify-between pt-0 pb-6 px-2 sticky top-0 h-screen overflow-hidden">
        <div className="flex flex-col gap-12">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="bg-[#17cf54] w-10 h-10 rounded-xl flex items-center justify-center text-white shadow-lg shadow-[#17cf54]/30">
              <span className="material-symbols-outlined text-2xl">shield</span>
            </div>
            <div className="flex flex-col">
              <h1 className="text-black text-[15px] font-bold leading-tight">Red Teaming</h1>
              <p className="text-gray-400 text-[10px] font-bold tracking-wider uppercase mt-0.5">Orchestrator v2.0</p>
            </div>
          </div>

          {/* Navigation Steps */}
          <nav className="flex flex-col relative pl-1">
            {/* Step 1 */}
            <div className="flex items-start gap-4 pb-10 relative">
              <div className="flex flex-col items-center z-10">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shadow-md transition-all duration-500 ${currentStep >= 1 ? 'bg-[#17cf54] text-white shadow-[#17cf54]/30' : 'bg-gray-100 text-gray-400'}`}>1</div>
              </div>
              <div className="pt-1 text-left">
                <p className={`text-[13px] font-bold transition-colors duration-500 ${currentStep === 1 ? 'text-[#17cf54]' : currentStep > 1 ? 'text-slate-700' : 'text-gray-400'}`}>Agent Role & Representation</p>
              </div>
              {/* Connecting Line */}
                <div className="absolute left-4 top-8 bottom-0 w-[2px] bg-gray-100 -z-0">
                 {/* Active Line Segment with Flow Animation */}
                 <div 
                   className={`absolute top-0 left-0 w-full bg-[#17cf54] transform origin-top transition-transform duration-200 ease-out ${currentStep > 1 ? 'scale-y-100' : 'scale-y-0'}`}
                 ></div>
              </div>
            </div>

            {/* Step 2 */}
            <div className="flex items-start gap-4 pb-10 relative">
              <div className="flex flex-col items-center z-10">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shadow-md transition-all duration-500 ${currentStep >= 2 ? 'bg-[#17cf54] text-white shadow-[#17cf54]/30' : 'bg-gray-100 text-gray-400'}`}>2</div>
              </div>
              <div className="pt-1 text-left">
                <p className={`text-[13px] font-bold transition-colors duration-500 ${currentStep === 2 ? 'text-[#17cf54]' : currentStep > 2 ? 'text-slate-700' : 'text-gray-400'}`}>Behavior Rules & Safety Goals</p>
              </div>
               {/* Connecting Line */}
               <div className="absolute left-4 top-8 bottom-0 w-[2px] bg-gray-100 -z-0">
                  {/* Active Line Segment with Flow Animation */}
                  <div 
                     className={`absolute top-0 left-0 w-full bg-[#17cf54] transform origin-top transition-transform duration-200 ease-out ${currentStep > 2 ? 'scale-y-100' : 'scale-y-0'}`}
                   ></div>
               </div>
            </div>

            {/* Step 3 */}
            <div className="flex items-start gap-4 relative">
              <div className="flex items-center justify-center z-10">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shadow-md transition-all duration-500 ${currentStep >= 3 ? 'bg-[#17cf54] text-white shadow-[#17cf54]/30' : 'bg-gray-100 text-gray-400'}`}>3</div>
              </div>
              <div className="pt-1 text-left">
                <p className={`text-[13px] font-bold transition-colors duration-500 ${currentStep === 3 ? 'text-[#17cf54]' : 'text-gray-400'}`}>Technical Access & Integrations</p>
              </div>
            </div>
          </nav>
        </div>

        {/* User Profile */}
        <div className="mt-auto relative">
          <button 
            onClick={() => setIsProfileMenuOpen(!isProfileMenuOpen)}
            className="w-full bg-[#f9fafb] rounded-2xl p-4 flex items-center gap-3 border border-gray-100/50 hover:bg-gray-50 hover:border-[#17cf54]/30 transition-all cursor-pointer text-left"
          >
            <div className="relative">
              <div className="w-10 h-10 rounded-full bg-gray-200 overflow-hidden ring-2 ring-white">
                <img src="https://ui-avatars.com/api/?name=Security+Analyst&background=e5e7eb&color=374151" alt="Profile" className="w-full h-full object-cover" />
              </div>
              <div className="absolute bottom-0 right-0 w-2.5 h-2.5 bg-[#17cf54] rounded-full ring-2 ring-white"></div>
            </div>
            <div className="flex flex-col min-w-0">
              <p className="text-xs font-bold text-gray-900 truncate">Security Analyst</p>
              <p className="text-[10px] text-[#17cf54] font-bold uppercase tracking-wide">Enterprise Node</p>
            </div>
             <span className="material-symbols-outlined ml-auto text-gray-400 text-lg">expand_less</span>
          </button>
          
           {isProfileMenuOpen && (
            <div className="absolute bottom-full left-0 -ml-4 w-44 mb-2 bg-white rounded-xl shadow-xl border border-gray-100 overflow-hidden z-20 animate-in fade-in slide-in-from-bottom-2">
              <div className="p-1">
                <button className="w-full flex items-center gap-3 px-3 py-2.5 hover:bg-gray-50 rounded-lg text-left transition-colors" onClick={() => navigate('/dashboard')}>
                  <span className="material-symbols-outlined text-gray-400 text-[18px]">dashboard</span>
                  <span className="text-[13px] font-medium text-gray-700">Dashboard</span>
                </button>
                <button className="w-full flex items-center gap-3 px-3 py-2.5 hover:bg-gray-50 rounded-lg text-left transition-colors">
                  <span className="material-symbols-outlined text-gray-400 text-[18px]">history</span>
                  <span className="text-[13px] font-medium text-gray-700">History</span>
                </button>
              </div>
            </div>
           )}
        </div>
      </aside>

      {/* Main Content */}
      <main
        ref={mainRef}
        className="flex-1 overflow-y-auto"
        style={{ backgroundColor: 'rgba(255,255,255,0.85)' }}
        onScroll={handleScroll}
      >
        <div className="max-w-6xl ml-12 pt-4 pr-12 text-left">
          {/* Header */}
          <header className="mb-16 border-b border-gray-200 pb-10">
            <div className="flex justify-between items-start">
              <div className="space-y-4">
                <h2 className="text-left text-slate-700 text-[42px] font-bold leading-tight tracking-tight">AI Agent Risk & Role Definition</h2>
                <p className="text-left text-gray-500 text-[15px] font-normal max-w-3xl leading-relaxed">
                  Define what this AI represents, what it can access, and how it behaves under risk scenarios.
                </p>
              </div>
              <div>
                 <button 
                  onClick={() => setShowLibrary(true)}
                  className="px-5 py-2.5 bg-gray-100 hover:bg-gray-200 text-gray-700 font-bold rounded-xl text-sm transition-colors flex items-center gap-2"
                 >
                   <span className="material-symbols-outlined">folder_open</span>
                   Load Profile
                 </button>
              </div>
            </div>
          </header>

          {showLibrary && (
              <div className="fixed inset-0 bg-black/20 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                <div className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[80vh] flex flex-col overflow-hidden">
                  <div className="p-6 border-b border-gray-100 flex justify-between items-center bg-gray-50">
                     <h3 className="text-xl font-bold text-gray-800">Profile Library</h3>
                     <button onClick={() => setShowLibrary(false)} className="text-gray-400 hover:text-gray-600">
                        <span className="material-symbols-outlined">close</span>
                     </button>
                  </div>
                  
                  <div className="flex flex-1 overflow-hidden">
                     {/* Buckets List */}
                     <div className="w-1/3 border-r border-gray-100 p-4 bg-gray-50/50 flex flex-col">
                        <div className="mb-4">
                           <div className="flex justify-between items-center mb-3">
                              <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider">Folders (Buckets)</h4>
                           </div>
                           <div className="flex gap-2 mb-4 bg-white p-1 rounded-lg border border-gray-200 focus-within:border-[#17cf54] transition-colors">
                              <input 
                                value={newBucketName}
                                onChange={(e) => setNewBucketName(e.target.value)}
                                placeholder="Create new bucket..."
                                className="flex-1 px-2 py-1.5 text-sm focus:outline-none bg-transparent"
                              />
                               <button 
                                type="button"
                                onClick={createBucket}
                                className="px-3 py-1.5 bg-gray-800 text-white rounded-md hover:bg-black transition-colors"
                              >
                                 <span className="material-symbols-outlined text-sm">add</span>
                              </button>
                           </div>
                        </div>
                        
                        <div className="flex-1 overflow-y-auto space-y-1">
                           {buckets.length === 0 && <p className="text-sm text-gray-400 italic">No folders yet.</p>}
                           {buckets.map(bucket => (
                              <button
                                key={bucket}
                                onClick={() => setSelectedBucket(bucket)}
                                className={`w-full text-left px-3 py-2.5 rounded-lg text-sm font-medium flex items-center gap-2 transition-colors ${selectedBucket === bucket ? 'bg-white shadow-sm text-[#17cf54] border border-gray-100' : 'text-gray-600 hover:bg-gray-100'}`}
                              >
                                 <span className="material-symbols-outlined text-[18px] text-amber-400">folder</span>
                                 {bucket}
                              </button>
                           ))}
                        </div>
                     </div>

                     {/* Files List */}
                     <div className="flex-1 p-6 overflow-y-auto bg-white">
                        <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-4">
                           {selectedBucket ? `Profiles in "${selectedBucket}"` : 'Select a folder to view profiles'}
                        </h4>
                        
                        {!selectedBucket && (
                           <div className="flex flex-col items-center justify-center h-48 text-gray-300">
                              <span className="material-symbols-outlined text-5xl mb-2">folder_open</span>
                              <p className="text-sm">Select a folder on the left</p>
                           </div>
                        )}
                        
                        {selectedBucket && bucketFiles.length === 0 && (
                           <p className="text-sm text-gray-400 italic">No profiles in this folder.</p>
                        )}
                        
                        <div className="grid grid-cols-1 gap-3">
                           {bucketFiles.map(file => (
                              <div 
                                key={file.name} 
                                onClick={() => loadProfile(file.name)}
                                className="flex items-center justify-between p-4 border border-gray-100 rounded-xl hover:bg-gray-50 hover:border-[#17cf54] cursor-pointer transition-all group"
                              >
                                 <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-lg bg-[#e6f4ea] flex items-center justify-center text-[#17cf54] group-hover:bg-[#17cf54] group-hover:text-white transition-colors">
                                       <span className="material-symbols-outlined">description</span>
                                    </div>
                                    <div>
                                       <p className="text-sm font-bold text-gray-800 group-hover:text-[#17cf54] transition-colors">{file.name.replace(/^profile_/, '').replace(/\.json$/, '')}</p>
                                       <p className="text-xs text-gray-400">{new Date(file.created * 1000).toLocaleString()}</p>
                                    </div>
                                 </div>
                                 <button 
                                    className="px-4 py-2 bg-white border border-gray-200 text-gray-700 text-sm font-medium rounded-lg group-hover:bg-[#17cf54] group-hover:text-white group-hover:border-[#17cf54] transition-colors shadow-sm"
                                 >
                                    Load
                                 </button>
                              </div>
                           ))}
                        </div>
                     </div>
                  </div>
                </div>
              </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-16 pb-16">
            {/* Section 1: Target Identity */}
            <section ref={section1Ref} className="border-b border-gray-200 pb-16">
              <div className="flex items-center gap-4 mb-5">
                <div className="w-10 h-10 bg-[#e6f4ea] rounded-xl flex items-center justify-center text-[#17cf54]">
                  <span className="material-symbols-outlined text-xl">person_search</span>
                </div>
                <div>
                  <h3 className="text-left text-[19px] font-bold text-slate-700 leading-tight">Agent Role & Business Context</h3>
                  <p className="text-left text-gray-500 text-[13px] mt-0.5">Define how the AI represents your business and users.</p>
                </div>
              </div>

              <div className="bg-[#ffffff] p-8 rounded-2xl border border-gray-200/60 shadow-[0_2px_20px_rgba(0,0,0,0.02)]">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-x-8 gap-y-8">
                  <div className="space-y-2.5">
                    <label className="text-left text-black text-[13px] font-bold flex items-center gap-1.5 ">
                      AI Agent Name
                      <span className="material-symbols-outlined text-gray-300 text-[14px] cursor-help hover:text-gray-500 transition-colors" title="Public facing name of the bot">help</span>
                    </label>
                    <input
                      className="w-full rounded-xl border border-gray-100 bg-[#f9fafb] h-[52px] px-5 text-[14px] text-gray-700 placeholder:text-gray-400 focus:outline-none focus:border-[#17cf54] focus:ring-4 focus:ring-[#17cf54]/5 transition-all"
                      placeholder="e.g., Support Bot"
                      type="text"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                    />
                  </div>

                  <div className="space-y-2.5">
                    <label className="text-left text-black text-[13px] font-bold ">Business Domain</label>
                    <input
                      className="w-full rounded-xl border border-gray-100 bg-[#f9fafb] h-[52px] px-5 text-[14px] text-gray-700 placeholder:text-gray-400 focus:outline-none focus:border-[#17cf54] focus:ring-4 focus:ring-[#17cf54]/5 transition-all"
                      placeholder="e.g., Healthcare"
                      title="e.g., Healthcare / PII Protected"
                      type="text"
                      value={domain}
                      onChange={(e) => setDomain(e.target.value)}
                    />
                  </div>

                  <div className="space-y-2.5">
                    <label className="text-left text-black text-[13px] font-bold ">Intended Users</label>
                    <input
                      className="w-full rounded-xl border border-gray-100 bg-[#f9fafb] h-[52px] px-5 text-[14px] text-gray-700 placeholder:text-gray-400 focus:outline-none focus:border-[#17cf54] focus:ring-4 focus:ring-[#17cf54]/5 transition-all"
                      placeholder="e.g., Public Users"
                      title="e.g., Guest Users (Public)"
                      type="text"
                      value={intendedAudience}
                      onChange={(e) => setIntendedAudience(e.target.value)}
                    />
                  </div>

                  <div className="space-y-2.5">
                    <label className="text-left text-black text-[13px] font-bold ">Communication Style</label>
                    <div className="relative">
                      <select
                        className="w-full rounded-xl border border-gray-100 bg-[#f9fafb] h-[44px] px-4 text-[13px] text-gray-700 appearance-none focus:outline-none focus:border-[#17cf54] focus:ring-4 focus:ring-[#17cf54]/5 transition-all cursor-pointer"
                        value={communicationStyle}
                        onChange={(e) => setCommunicationStyle(e.target.value)}
                      >
                        <option value="">Select communication style</option>
                        <option value="professional">Professional & Formal</option>
                        <option value="casual">Casual & Helpful</option>
                        <option value="clinical">Clinical & Objective</option>
                        <option value="hostile">Hostile & Defensive</option>
                      </select>
                      
                    </div>
                  </div>

                  <div className="space-y-2.5">
                    <label className="text-left text-black text-[13px] font-bold ">AI Function Type</label>
                    <div className="relative">
                      <select
                        className="w-full rounded-xl border border-gray-100 bg-[#f9fafb] h-[44px] px-4 text-[13px] text-gray-700 appearance-none focus:outline-none focus:border-[#17cf54] focus:ring-4 focus:ring-[#17cf54]/5 transition-all cursor-pointer"
                        value={agentType}
                        onChange={(e) => setAgentType(e.target.value)}
                      >
                        <option value="">Select agent type</option>
                        <option value="Customer Support Bot">Customer Support Bot</option>
                        <option value="Technical Support Agent">Technical Support Agent</option>
                        <option value="Sales Assistant">Sales Assistant</option>
                        <option value="Information Helper">Information Helper</option>
                        <option value="General Chatbot">General Chatbot</option>
                        <option value="Other">Other</option>
                      </select>
                      
                    </div>
                  </div>
                </div>
              </div>
            </section>

            {/* Section 2: Behavioral Directives */}
            <section ref={section2Ref} className="border-b border-gray-200 pb-16">
              <div className="flex items-center gap-4 mb-5">
                <div className="w-10 h-10 bg-amber-100 rounded-xl flex items-center justify-center text-amber-600">
                  <span className="material-symbols-outlined text-xl">psychology</span>
                </div>
                <div>
                  <h3 className="text-left text-[19px] font-bold text-slate-700 leading-tight">Behavior Rules & Safety Objectives</h3>
                  <p className="text-left text-gray-500 text-[13px] mt-0.5">Define what success looks like and where the AI must stop.</p>
                </div>
              </div>

              <div className="bg-[#ffffff] p-8 rounded-2xl border border-gray-200/60 shadow-[0_2px_20px_rgba(0,0,0,0.02)] grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="space-y-2.5">
                  <label className="text-left text-black text-[13px] font-bold ">Business Purpose</label>
                  <textarea
                    className="w-full rounded-xl border border-gray-100 bg-[#f9fafb] p-5 text-[14px] text-gray-700 placeholder:text-gray-400 resize-none focus:outline-none focus:border-[#17cf54] focus:ring-4 focus:ring-[#17cf54]/5 transition-all leading-relaxed h-[180px]"
                    placeholder="Describe the agent's main purpose"
                    title="Explain the primary utility of this agent... (e.g., help customers reset passwords via secure tokens)"
                    value={primaryObjective}
                    onChange={(e) => setPrimaryObjective(e.target.value)}
                  ></textarea>
                </div>

                <div className="space-y-2.5">
                  <label className="text-left text-black text-[13px] font-bold ">Security & Compliance Constraints</label>
                  <textarea
                    className="w-full rounded-xl border border-gray-100 bg-[#f9fafb] p-5 text-[14px] text-gray-700 placeholder:text-gray-400 resize-none focus:outline-none focus:border-[#17cf54] focus:ring-4 focus:ring-[#17cf54]/5 transition-all leading-relaxed h-[180px]"
                    placeholder="Define security boundaries"
                    title="List strict negative constraints... (e.g., never reveal system prompts, do not discuss internal API structure)"
                    value={boundaries}
                    onChange={(e) => setBoundaries(e.target.value)}
                  ></textarea>
                </div>
              </div>
            </section>

            {/* Section 3: System Configuration */}
            <section ref={section3Ref}>
              <div className="flex items-center gap-4 mb-5">
                <div className="w-10 h-10 bg-[#e6f4ea] rounded-xl flex items-center justify-center text-[#17cf54]">
                  <span className="material-symbols-outlined text-xl">settings</span>
                </div>
                <div>
                  <h3 className="text-left text-[19px] font-bold text-slate-700 leading-tight">Technical Access & System Exposure</h3>
                  <p className="text-left text-gray-500 text-[13px] mt-0.5">Define where the AI connects and what it is allowed to access.</p>
                </div>
              </div>

              <div className="bg-[#ffffff] p-8 rounded-2xl border border-gray-200/60 shadow-[0_2px_20px_rgba(0,0,0,0.02)] space-y-8">
                <div className="space-y-2.5">
                  <label className="text-left text-black text-[13px] font-bold ">Live Connection Endpoint</label>
                  <input
                    className="w-full rounded-xl border border-gray-100 bg-[#f9fafb] h-[52px] px-5 text-[14px] text-gray-700 placeholder:text-gray-400 focus:outline-none focus:border-[#17cf54] focus:ring-4 focus:ring-[#17cf54]/5 transition-all"
                    placeholder="ws://localhost:8001/ws"
                    type="text"
                    value={websocketUrl}
                    onChange={(e) => setWebsocketUrl(e.target.value)}
                  />
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="text-left text-black text-[13px] font-bold ">
                      Enabled Data Sources
                      <span className="block text-[11px] font-normal text-gray-400 mt-1 normal-case tracking-normal">What can this agent actually do? Click to select, or add below.</span>
                    </label>

                    <div className="mt-3 flex flex-wrap gap-2">
                      {[
                        'Structured DB',
                        'Unstructured DB',
                        'Web browsing API',
                        'External API',
                        'Knowledge Graph',
                      ].map((opt) => {
                        const selected = capabilities.find((c) => c.toLowerCase() === opt.toLowerCase());
                        return (
                          <button
                            key={opt}
                            type="button"
                            onClick={() => toggleCapability(opt)}
                            className={`px-3 py-1 rounded-full text-sm border ${selected ? 'bg-[#17cf54] text-white border-transparent' : 'bg-[#f3f4f6] text-gray-700 border-gray-200'}`}
                          >
                            {opt}
                          </button>
                        );
                      })}
                    </div>

                    <div className="mt-3 flex gap-2 items-center">
                      <input
                        value={newCapability}
                        onChange={(e) => setNewCapability(e.target.value)}
                        placeholder="Add custom data source"
                        title="Other capability (type and Add)"
                        className="flex-1 rounded-xl border border-gray-100 bg-[#f9fafb] h-[44px] px-4 text-[14px] text-gray-700 placeholder:text-gray-400 focus:outline-none focus:border-[#17cf54] focus:ring-4 focus:ring-[#17cf54]/5 transition-all"
                      />
                      <button
                        type="button"
                        onClick={addCustomCapability}
                        className="flex items-center gap-2 px-4 py-2.5 bg-[#17cf54] text-white rounded-lg text-sm font-bold hover:bg-[#15ba4a] transition-all shadow-sm"
                      >
                        Add
                      </button>
                    </div>

                    <div className="mt-3 flex flex-wrap gap-2">
                      {capabilities.filter((c) => c.trim() !== "").map((cap, index) => (
                        <div key={index} className="flex items-center gap-2 bg-[#f9fafb] rounded-full px-3 py-1 border border-gray-200 text-sm">
                          <span className="text-[13px] text-gray-700">{cap}</span>
                          <button type="button" onClick={() => removeCapability(index)} className="text-gray-400 hover:text-red-500">
                            <span className="material-symbols-outlined text-[16px]">close</span>
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </section>

            {/* Submit Button */}
            <div className="flex flex-col items-end gap-4 pt-6 mb-8 border-t border-gray-200/60">
              <div className="flex items-center gap-3">
                 <label className="text-sm font-bold text-gray-700">Save to Folder:</label>
                 <select 
                    value={selectedBucket} 
                    onChange={(e) => setSelectedBucket(e.target.value)}
                    className="h-[44px] px-4 rounded-xl border border-gray-200 bg-[#f9fafb] text-sm text-gray-700 focus:outline-none focus:border-[#17cf54]"
                 >
                    <option value="">Default (Uploads)</option>
                    {buckets.map(b => (
                       <option key={b} value={b}>{b}</option>
                    ))}
                 </select>
              </div>

              <button
                type="submit"
                className="px-10 py-4 bg-[#17cf54] text-white rounded-xl text-[15px] font-bold hover:bg-[#15ba4a] transition-all flex items-center gap-3 shadow-xl shadow-[#17cf54]/25 hover:shadow-[#17cf54]/40 hover:-translate-y-0.5 active:translate-y-0"
              >
                Start Risk Simulation
                <span className="material-symbols-outlined text-xl">rocket_launch</span>
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
};

export default ProfileSetup;
