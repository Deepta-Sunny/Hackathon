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
  
  // Move File State
  const [fileToMove, setFileToMove] = useState<string | null>(null);
  const [moveTargetBucket, setMoveTargetBucket] = useState<string>("");
  
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

  const handleMoveFile = async () => {
    if (!fileToMove || !moveTargetBucket || !selectedBucket) return;
    
    try {
        const res = await fetch(`${API_BASE_URL}/api/buckets/move`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filename: fileToMove,
                source_bucket: selectedBucket,
                target_bucket: moveTargetBucket
            })
        });
        
        if (res.ok) {
            setFileToMove(null);
            setMoveTargetBucket("");
            fetchBucketFiles(selectedBucket); 
        } else {
            console.error("Failed to move file");
        }
    } catch (e) {
        console.error("Error moving file:", e);
    }
  };

  useEffect(() => {
     if (showLibrary) {
        fetchBuckets();
     }
  }, [showLibrary]);

  useEffect(() => {
      if (buckets.includes("General") && !selectedBucket) {
          setSelectedBucket("General");
      } else if (buckets.length > 0 && !selectedBucket) {
          setSelectedBucket(buckets[0]);
      }
  }, [buckets]);

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

    // Validate required fields

    // Username (AI Agent Name): 3-32 chars
    if (!username.trim()) {
      alert("Please enter an AI Agent Name");
      return;
    }
    if (username.length < 3 || username.length > 32) {
      alert("AI Agent Name must be between 3 and 32 characters.");
      return;
    }

    // Domain: 3-40 chars
    if (!domain.trim()) {
      alert("Please enter a Business Domain");
      return;
    }
    if (domain.length < 3 || domain.length > 40) {
      alert("Business Domain must be between 3 and 40 characters.");
      return;
    }

    // Intended Audience: 3-40 chars
    if (!intendedAudience.trim()) {
      alert("Please enter Intended Users");
      return;
    }
    if (intendedAudience.length < 3 || intendedAudience.length > 40) {
      alert("Intended Users must be between 3 and 40 characters.");
      return;
    }

    // Communication Style: required
    if (!communicationStyle) {
      alert("Please select a Communication Style");
      return;
    }

    // Agent Type: required
    if (!agentType) {
      alert("Please select an AI Function Type");
      return;
    }

    // Primary Objective: 10-200 chars
    if (!primaryObjective.trim()) {
      alert("Please enter a Business Purpose");
      return;
    }
    if (primaryObjective.length < 10 || primaryObjective.length > 200) {
      alert("Business Purpose must be between 10 and 200 characters.");
      return;
    }

    // Boundaries: 10-200 chars
    if (!boundaries.trim()) {
      alert("Please enter Security & Compliance Constraints");
      return;
    }
    if (boundaries.length < 10 || boundaries.length > 200) {
      alert("Security & Compliance Constraints must be between 10 and 200 characters.");
      return;
    }

    // Websocket URL: 10-100 chars
    if (!websocketUrl.trim()) {
      alert("Please enter a Live Connection Endpoint");
      return;
    }
    if (websocketUrl.length < 10 || websocketUrl.length > 100) {
      alert("Live Connection Endpoint must be between 10 and 100 characters.");
      return;
    }

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
    
    // Save to backend dashboard state (but don't start attack yet)
    try {
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8080";
      await fetch(`${API_BASE_URL}/api/dashboard/save`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(profile),
      });
      console.log("✅ Profile saved to backend");
    } catch (error) {
      console.log("Could not save to backend:", error);
    }
    
    // Navigate to dashboard (attack will start when user clicks Start button)
    navigate("/dashboard");
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
    <div className="flex h-screen overflow-hidden bg-white font-sans">
      {/* Sidebar */}
      <aside className="w-56 bg-white border-r border-gray-300 flex flex-col justify-between pt-4 pb-6 px-2 sticky top-0 h-screen overflow-visible">
        <div className="flex flex-col gap-12">
          {/* Logo */}
          <div className="flex items-center gap-3 px-2 cursor-pointer" onClick={() => navigate('/')}>
            <div className="bg-[#0f62fe] w-8 h-8 rounded-xl flex items-center justify-center text-white shadow-md">
              <span className="material-symbols-outlined text-xl">shield</span>
            </div>
            <div className="flex flex-col">
              <h1 className="text-black text-[15px] font-bold leading-tight">Crucible AI</h1>
            </div>
          </div>

          {/* Navigation Steps */}
          <nav className="flex flex-col relative pl-1">
            {/* Step 1 */}
            <div className="flex items-start gap-4 pb-10 relative">
              <div className="flex flex-col items-center z-10">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shadow-md transition-all duration-500 ${currentStep >= 1 ? 'bg-[#0f62fe] text-white shadow-[#0f62fe]/30' : 'bg-gray-200 text-gray-600'}`}>1</div>
              </div>
              <div className="pt-1 text-left">
                <p className={`text-[13px] font-bold transition-colors duration-500 ${currentStep === 1 ? 'text-[#0f62fe]' : currentStep > 1 ? 'text-slate-700' : 'text-gray-600'}`}>Agent Role & Representation</p>
              </div>
              {/* Connecting Line */}
              <div className="absolute left-[15px] top-8 bottom-0 w-[3px] overflow-hidden z-0">
                <div className="w-full bg-gray-200 h-full absolute top-0 left-0"></div>
                <div className={`w-full bg-[#0f62fe] absolute top-0 left-0 transition-all duration-700 ease-out ${currentStep >= 2 ? 'h-full' : 'h-0'}`}></div>
              </div>
            </div>

            {/* Step 2 */}
            <div className="flex items-start gap-4 pb-10 relative">
              <div className="flex flex-col items-center z-10">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shadow-md transition-all duration-500 ${currentStep >= 2 ? 'bg-[#0f62fe] text-white shadow-[#0f62fe]/30' : 'bg-gray-200 text-gray-600'}`}>2</div>
              </div>
              <div className="pt-1 text-left">
                <p className={`text-[13px] font-bold transition-colors duration-500 ${currentStep === 2 ? 'text-[#0f62fe]' : currentStep > 2 ? 'text-slate-700' : 'text-gray-600'}`}>Behavior Rules & Safety Goals</p>
              </div>
              {/* Connecting Line */}
              <div className="absolute left-[15px] top-8 bottom-0 w-[3px] overflow-hidden z-0">
                <div className="w-full bg-gray-200 h-full absolute top-0 left-0"></div>
                <div className={`w-full bg-[#0f62fe] absolute top-0 left-0 transition-all duration-700 ease-out ${currentStep >= 3 ? 'h-full' : 'h-0'}`}></div>
              </div>
            </div>

            {/* Step 3 */}
            <div className="flex items-start gap-4 relative">
              <div className="flex flex-col items-center z-10">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shadow-md transition-all duration-500 ${currentStep >= 3 ? 'bg-[#0f62fe] text-white shadow-[#0f62fe]/30' : 'bg-gray-200 text-gray-600'}`}>3</div>
              </div>
              <div className="pt-1 text-left">
                <p className={`text-[13px] font-bold transition-colors duration-500 ${currentStep === 3 ? 'text-[#0f62fe]' : 'text-gray-600'}`}>Technical Access & Integrations</p>
              </div>
            </div>
          </nav>
        </div>

        {/* User Profile */}
        <div 
            className="mt-auto relative mb-6"
        >
          <button 
            onClick={() => setIsProfileMenuOpen(!isProfileMenuOpen)}
            className="w-full bg-[#f9fafb] rounded-xl p-4 flex items-center gap-3 border border-gray-100/50 hover:bg-white hover:border-[#0f62fe]/20 transition-all cursor-pointer text-left"
          >
            <div className="relative">
              <div className="w-10 h-10 rounded-full bg-gray-200 overflow-hidden ring-2 ring-white">
                <img src="https://ui-avatars.com/api/?name=User+Profile&background=e5e7eb&color=374151" alt="Profile" className="w-full h-full object-cover" />
              </div>
              <div className="absolute bottom-0 right-0 w-2.5 h-2.5 bg-[#0f62fe] rounded-full ring-2 ring-white"></div>
            </div>
            <div className="flex flex-col min-w-0">
              <p className="text-xs font-bold text-gray-900 truncate">User Profile</p>
              <p className="text-[10px] text-gray-500 font-medium">Settings</p>
            </div>
             <span className={`material-symbols-outlined ml-auto text-gray-400 text-lg transition-all ${isProfileMenuOpen ? 'rotate-180 text-[#0f62fe]' : ''}`}>expand_less</span>
          </button>
          
           {isProfileMenuOpen && (
            <div className="absolute bottom-full left-0 w-64 mb-4 bg-white rounded-xl shadow-xl border border-gray-100 z-[100] ml-2">
              <div className="p-1">
                <button className="w-full flex items-center gap-3 px-3 py-3 hover:bg-[#edf5ff] rounded-lg text-left transition-colors group/item" onClick={() => { navigate('/dashboard'); setIsProfileMenuOpen(false); }}>
                  <span className="material-symbols-outlined text-gray-400 text-xl group-hover/item:text-[#0f62fe]">dashboard</span>
                  <span className="text-sm font-medium text-gray-700 group-hover/item:text-[#0f62fe]">Dashboard</span>
                </button>
                <button className="w-full flex items-center gap-3 px-3 py-3 hover:bg-[#edf5ff] rounded-lg text-left transition-colors group/item" onClick={() => { navigate('/history'); setIsProfileMenuOpen(false); }}>
                  <span className="material-symbols-outlined text-gray-400 text-xl group-hover/item:text-[#0f62fe]">history</span>
                  <span className="text-sm font-medium text-gray-700 group-hover/item:text-[#0f62fe]">History</span>
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
          <header className="mb-10 border-b border-gray-200 pb-6">
            <div className="flex justify-between items-start">
              <div className="space-y-2">
                <h2 className="text-left text-slate-700 text-[36px] font-bold leading-tight tracking-tight">Agentic Project Onboarding</h2>
                <p className="text-left text-gray-500 text-base font-medium max-w-3xl leading-relaxed">
                  Define what this AI represents, what it can access, and how it behaves under risk scenarios.
                </p>
              </div>
              <div>
                 <button 
                  onClick={() => setShowLibrary(true)}
                  className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 font-bold rounded-lg text-xs transition-colors flex items-center gap-2"
                 >
                   <span className="material-symbols-outlined text-lg">folder_open</span>
                   Client Profiles
                 </button>
              </div>
            </div>
          </header>

          {showLibrary && (
              <div className="fixed inset-0 bg-black/20 backdrop-blur-sm z-50 flex items-center justify-center p-4 font-sans">
                <div className="bg-white rounded-xl shadow-2xl w-[900px] h-[700px] flex flex-col overflow-hidden">
                  <div className="p-4 border-b border-gray-100 flex justify-between items-center bg-gray-50">
                     <h3 className="text-lg font-bold text-gray-800">Client Onboarding Page</h3>
                     <button onClick={() => setShowLibrary(false)} className="text-gray-400 hover:text-gray-600">
                        <span className="material-symbols-outlined">close</span>
                     </button>
                  </div>
                  
                  <div className="flex flex-1 overflow-hidden">
                     {/* Buckets List */}
                     <div className="w-1/3 border-r border-gray-100 p-4 bg-gray-50/50 flex flex-col">
                        <div className="mb-4">
                           <div className="flex gap-2 mb-4 bg-white p-1 rounded-lg border border-gray-200 focus-within:border-[#0f62fe] transition-colors">
                              <input 
                                value={newBucketName}
                                onChange={(e) => setNewBucketName(e.target.value)}
                                placeholder="Create new client folder..."
                                className="flex-1 px-2 py-1.5 text-xs focus:outline-none bg-transparent text-[#0f62fe] placeholder-gray-400 font-medium"
                              />
                               <button 
                                type="button"
                                onClick={createBucket}
                                className="px-3 py-1.5 bg-[#0f62fe] text-white rounded-md hover:bg-[#0353e9] transition-colors"
                              >
                                 <span className="material-symbols-outlined text-xs">add</span>
                              </button>
                           </div>
                           <div className="flex justify-between items-center mb-3">
                              <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider">Client Folders</h4>
                           </div>
                        </div>
                        
                        <div className="flex-1 overflow-y-auto space-y-1">
                           {buckets.length === 0 && <p className="text-xs text-gray-400 italic">No folders yet.</p>}
                           {buckets.map(bucket => (
                              <button
                                key={bucket}
                                onClick={() => setSelectedBucket(bucket)}
                                className={`w-full text-left px-3 py-2 rounded-lg text-xs font-medium flex items-center gap-2 transition-colors ${selectedBucket === bucket ? 'bg-white shadow-sm text-[#0f62fe] border border-gray-100' : 'text-gray-600 hover:bg-gray-100'}`}
                              >
                                 <span className="material-symbols-outlined text-[16px] text-amber-400">folder</span>
                                 {bucket}
                              </button>
                           ))}
                        </div>
                     </div>

                     {/* Files List */}
                     <div className="flex-1 p-4 overflow-y-auto bg-white">
                        <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-4">
                           {selectedBucket ? `Profiles in "${selectedBucket}"` : 'Select a folder to view profiles'}
                        </h4>
                        
                        {!selectedBucket && (
                           <div className="flex flex-col items-center justify-center h-48 text-gray-300">
                              <span className="material-symbols-outlined text-4xl mb-2">folder_open</span>
                              <p className="text-xs">Select a folder on the left</p>
                           </div>
                        )}
                        
                        {selectedBucket && bucketFiles.length === 0 && (
                           <p className="text-xs text-gray-400 italic">No profiles in this folder.</p>
                        )}
                        
                        <div className="grid grid-cols-1 gap-2">
                           {bucketFiles.map(file => (
                              <div 
                                key={file.name} 
                                onClick={() => loadProfile(file.name)}
                                className="flex items-center justify-between p-3 border border-gray-100 rounded-lg hover:bg-gray-50 hover:border-[#0f62fe] cursor-pointer transition-all group"
                              >
                                 <div className="flex items-center gap-3">
                                    <div className="w-8 h-8 rounded-lg bg-[#edf5ff] flex items-center justify-center text-[#0f62fe] group-hover:bg-[#0f62fe] group-hover:text-white transition-colors">
                                       <span className="material-symbols-outlined text-lg">description</span>
                                    </div>
                                    <div>
                                       <p className="text-xs font-bold text-gray-800 group-hover:text-[#0f62fe] transition-colors">{file.name.replace(/^profile_/, '').replace(/\.json$/, '')}</p>
                                       <p className="text-[10px] text-gray-400">{new Date(file.created * 1000).toLocaleString()}</p>
                                    </div>
                                 </div>
                                 
                                 <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
                                    {/* Move File UI */}
                                    {fileToMove === file.name ? (
                                        <div className="flex items-center gap-1 bg-gray-50 p-1 rounded-lg border border-gray-200">
                                            <select 
                                                className="text-[10px] border-none bg-transparent outline-none py-1 w-20"
                                                value={moveTargetBucket}
                                                onChange={e => setMoveTargetBucket(e.target.value)}
                                            >
                                                <option value="">Move...</option>
                                                {buckets.filter(b => b !== selectedBucket).map(b => (
                                                    <option key={b} value={b}>{b}</option>
                                                ))}
                                            </select>
                                            <button 
                                                onClick={handleMoveFile}
                                                disabled={!moveTargetBucket}
                                                className={`p-1 rounded ${moveTargetBucket ? 'text-[#0f62fe] hover:bg-blue-50' : 'text-gray-300'}`}
                                            >
                                                <span className="material-symbols-outlined text-xs">check</span>
                                            </button>
                                            <button 
                                                onClick={() => {setFileToMove(null); setMoveTargetBucket("")}}
                                                className="p-1 rounded text-red-500 hover:bg-red-50"
                                            >
                                                <span className="material-symbols-outlined text-xs">close</span>
                                            </button>
                                        </div>
                                    ) : (
                                        <button 
                                            onClick={() => setFileToMove(file.name)}
                                            title="Move file"
                                            className="p-1.5 text-gray-400 hover:text-blue-500 hover:bg-blue-50 rounded-lg transition-colors"
                                        >
                                            <span className="material-symbols-outlined text-[16px]">drive_file_move</span>
                                        </button>
                                    )}

                                    <button 
                                        onClick={() => loadProfile(file.name)}
                                        className="px-3 py-1.5 bg-white border border-gray-200 text-gray-700 text-xs font-medium rounded-lg group-hover:bg-[#0f62fe] group-hover:text-white group-hover:border-[#0f62fe] transition-colors shadow-sm"
                                    >
                                        Load
                                    </button>
                                 </div>
                              </div>
                           ))}
                        </div>
                     </div>
                  </div>
                </div>
              </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-12 pb-8">
            {/* Section 1: Target Identity */}
            <section ref={section1Ref} className="border-b border-gray-200 pb-12">
              <div className="flex items-center gap-4 mb-6">
                <div className="w-12 h-12 bg-[#edf5ff] rounded-lg flex items-center justify-center text-[#0f62fe]">
                  <span className="material-symbols-outlined text-xl">person_search</span>
                </div>
                <div>
                  <h3 className="text-left text-2xl font-bold text-slate-700 leading-tight">Agent Role & Business Context</h3>
                  <p className="text-left text-gray-500 text-base mt-1 font-medium">Define how the AI represents your business and users.</p>
                </div>
              </div>
              <div className="bg-[#ffffff] p-4 rounded-xl border border-gray-200/60 shadow-[0_2px_20px_rgba(0,0,0,0.02)]">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-x-4 gap-y-4">
                  <div className="space-y-1.5">
                    <label className="text-left text-black text-base font-semibold flex items-center gap-1.5 ">
                       AI Agent Name
                    </label>
                    <input
                      className="w-full rounded-lg border border-gray-300 bg-white h-[42px] px-3 text-base text-gray-700 placeholder:text-gray-400 focus:outline-none focus:border-[#0f62fe] focus:ring-4 focus:ring-[#0f62fe]/5 transition-all"
                      placeholder="e.g., Support Bot"
                      type="text"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-left text-black text-base font-semibold ">Business Domain</label>
                    <input
                      className="w-full rounded-lg border border-gray-300 bg-white h-[42px] px-3 text-base text-gray-700 placeholder:text-gray-400 focus:outline-none focus:border-[#0f62fe] focus:ring-4 focus:ring-[#0f62fe]/5 transition-all"
                      placeholder="e.g., Healthcare"
                      title="e.g., Healthcare / PII Protected"
                      type="text"
                      value={domain}
                      onChange={(e) => setDomain(e.target.value)}
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-left text-black text-base font-semibold ">Intended Users</label>
                    <input
                      className="w-full rounded-lg border border-gray-300 bg-white h-[42px] px-3 text-base text-gray-700 placeholder:text-gray-400 focus:outline-none focus:border-[#0f62fe] focus:ring-4 focus:ring-[#0f62fe]/5 transition-all"
                      placeholder="e.g., Public Users"
                      title="e.g., Guest Users (Public)"
                      type="text"
                      value={intendedAudience}
                      onChange={(e) => setIntendedAudience(e.target.value)}
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-left text-black text-base font-semibold ">Communication Style</label>
                    <div className="relative">
                      <select
                        className="w-full rounded-lg border border-gray-300 bg-white h-[42px] px-3 text-base text-gray-700 appearance-none focus:outline-none focus:border-[#0f62fe] focus:ring-4 focus:ring-[#0f62fe]/5 transition-all cursor-pointer"
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

                  <div className="space-y-1.5">
                    <label className="text-left text-black text-base font-semibold ">AI Function Type</label>
                    <div className="relative">
                      <select
                        className="w-full rounded-xl border border-gray-300 bg-white h-[42px] px-3 text-base text-gray-700 appearance-none focus:outline-none focus:border-[#0f62fe] focus:ring-4 focus:ring-[#0f62fe]/5 transition-all cursor-pointer"
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
            <section ref={section2Ref} className="border-b border-gray-200 pb-12">
              <div className="flex items-center gap-4 mb-6">
                <div className="w-12 h-12 bg-[#edf5ff] rounded-xl flex items-center justify-center text-[#0f62fe]">
                  <span className="material-symbols-outlined text-xl">verified_user</span>
                </div>
                <div>
                  <h3 className="text-left text-2xl font-bold text-slate-700 leading-tight">Behavior Rules & Safety Objectives</h3>
                  <p className="text-left text-gray-500 text-base mt-1 font-medium">Specify clear criteria for expected behavior and boundaries for safe AI behavior.</p>
                </div>
              </div>
              <div className="bg-[#ffffff] p-4 rounded-2xl border border-gray-200/60 shadow-[0_2px_20px_rgba(0,0,0,0.02)] grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-left text-black text-base font-semibold ">Business Purpose</label>
                  <textarea
                    className="w-full rounded-xl border border-gray-300 bg-white p-3 text-base text-gray-700 placeholder:text-gray-400 resize-none focus:outline-none focus:border-[#0f62fe] focus:ring-4 focus:ring-[#0f62fe]/5 transition-all leading-relaxed h-[120px]"
                    placeholder="Describe the agent's main purpose"
                    title="Explain the primary utility of this agent... (e.g., help customers reset passwords via secure tokens)"
                    value={primaryObjective}
                    onChange={(e) => setPrimaryObjective(e.target.value)}
                  ></textarea>
                </div>
                <div className="space-y-2">
                  <label className="text-left text-black text-base font-semibold ">Security & Compliance Constraints</label>
                  <textarea
                    className="w-full rounded-xl border border-gray-300 bg-white p-3 text-base text-gray-700 placeholder:text-gray-400 resize-none focus:outline-none focus:border-[#0f62fe] focus:ring-4 focus:ring-[#0f62fe]/5 transition-all leading-relaxed h-[120px]"
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
              <div className="flex items-center gap-4 mb-6">
                <div className="w-12 h-12 bg-[#edf5ff] rounded-xl flex items-center justify-center text-[#0f62fe]">
                  <span className="material-symbols-outlined text-xl">settings</span>
                </div>
                <div>
                  <h3 className="text-left text-2xl font-bold text-slate-700 leading-tight">Technical Access & System Exposure</h3>
                  <p className="text-left text-gray-500 text-base mt-1 font-medium">Define where the AI connects and what it is allowed to access.</p>
                </div>
              </div>
              <div className="bg-[#ffffff] p-4 rounded-2xl border border-gray-200/60 shadow-[0_2px_20px_rgba(0,0,0,0.02)] space-y-4">
                <div className="space-y-2">
                  <label className="text-left text-black text-base font-semibold ">Live Connection Endpoint</label>
                  <input
                    className="w-full rounded-xl border border-gray-300 bg-white h-[42px] px-3 text-base text-gray-700 placeholder:text-gray-400 focus:outline-none focus:border-[#0f62fe] focus:ring-4 focus:ring-[#0f62fe]/5 transition-all"
                    placeholder="ws://localhost:8001/ws"
                    type="text"
                    value={websocketUrl}
                    onChange={(e) => setWebsocketUrl(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <div>
                    <label className="text-left text-black text-base font-semibold ">
                      Enabled Data Sources
                      <span className="block text-sm font-normal text-gray-400 mt-1 normal-case tracking-normal">What can this agent actually do? Click to select, or add below.</span>
                    </label>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {([
                        'Structured DB',
                        'Unstructured DB',
                        'Web browsing API',
                        'External API',
                        'Knowledge Graph',
                      ]).map((opt) => {
                        const selected = capabilities.find((c) => c.toLowerCase() === opt.toLowerCase());
                        return (
                          <button
                            key={opt}
                            type="button"
                            onClick={() => toggleCapability(opt)}
                            className={`px-3 py-1.5 rounded-full text-base border ${selected ? 'bg-[#0f62fe] text-white border-transparent' : 'bg-[#f3f4f6] text-gray-700 border-gray-200'}`}
                          >
                            {opt}
                          </button>
                        );
                      })}
                    </div>
                    <div className="mt-2 flex gap-2 items-center">
                      <input
                        value={newCapability}
                        onChange={(e) => setNewCapability(e.target.value)}
                        placeholder="Add custom data source"
                        title="Other capability (type and Add)"
                          className="flex-1 rounded-xl border border-gray-300 bg-white h-[42px] px-3 text-base text-gray-700 placeholder:text-gray-400 focus:outline-none focus:border-[#0f62fe] focus:ring-4 focus:ring-[#0f62fe]/5 transition-all"
                      />
                      <button
                        type="button"
                        onClick={addCustomCapability}
                        className="flex items-center gap-2 px-4 py-2 bg-[#0f62fe] text-white rounded-lg text-base font-bold hover:bg-[#0353e9] transition-all shadow-sm"
                      >
                        Add
                      </button>
                    </div>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {capabilities.filter((c) => c.trim() !== "").map((cap, index) => (
                        <div key={index} className="flex items-center gap-2 bg-[#f9fafb] rounded-full px-3 py-1.5 border border-gray-200 text-base">
                        <span className="text-base text-gray-700">{cap}</span>
                        <button type="button" onClick={() => removeCapability(index)} className="text-gray-400 hover:text-red-500">
                          <span className="material-symbols-outlined text-base">close</span>
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </section>

            {/* Submit Button */}
            <div className="flex flex-col items-end gap-4 pt-6 pb-8 mb-24 border-t border-gray-200/60">
              <div className="flex items-center gap-2">
                <label className="text-base font-semibold text-gray-700">Save to client:</label>
                <select 
                  value={selectedBucket} 
                  onChange={(e) => setSelectedBucket(e.target.value)}
                  className="h-[42px] px-3 rounded-xl border border-gray-300 bg-white text-base text-gray-700 focus:outline-none focus:border-[#0f62fe]"
                >
                  <option value="">Select</option>
                  {buckets.map(b => (
                    <option key={b} value={b}>{b}</option>
                  ))}
                </select>
              </div>
              <button
                type="submit"
                className="px-6 py-3 bg-[#0f62fe] text-white rounded-xl text-base font-bold hover:bg-[#0353e9] transition-all shadow-xl shadow-[#0f62fe]/25 hover:shadow-[#0f62fe]/40 hover:-translate-y-0.5 active:translate-y-0"
              >
                Start Risk Simulation
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
};

export default ProfileSetup;
