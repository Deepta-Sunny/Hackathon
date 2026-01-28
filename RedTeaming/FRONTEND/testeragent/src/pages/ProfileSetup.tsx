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
  context_awareness: string;
  backend_integration?: string;
  training_context?: string;
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
  const [capabilities, setCapabilities] = useState<string[]>([""]);
  const [boundaries, setBoundaries] = useState("");
  const [communicationStyle, setCommunicationStyle] = useState("");
  const [backendIntegration, setBackendIntegration] = useState("");
  const [trainingContext, setTrainingContext] = useState("");

  const addCapability = () => {
    setCapabilities([...capabilities, ""]);
  };

  const removeCapability = (index: number) => {
    setCapabilities(capabilities.filter((_, i) => i !== index));
  };

  const updateCapability = (index: number, value: string) => {
    const updated = [...capabilities];
    updated[index] = value;
    setCapabilities(updated);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const profile: ChatbotProfile = {
      username,
      websocket_url: websocketUrl,
      domain,
      primary_objective: primaryObjective,
      intended_audience: intendedAudience,
      chatbot_role: chatbotRole || username,
      capabilities: capabilities.filter((c) => c.trim() !== ""),
      boundaries,
      communication_style: communicationStyle,
      context_awareness: "maintains_context",
      backend_integration: backendIntegration,
      training_context: trainingContext,
    };

    sessionStorage.setItem("chatbotProfile", JSON.stringify(profile));
    navigate("/dashboard");
  };

  const isFormValid =
    username &&
    websocketUrl &&
    domain &&
    primaryObjective &&
    intendedAudience &&
    communicationStyle &&
    capabilities.some((c) => c.trim() !== "") &&
    boundaries;

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
    return () => window.removeEventListener('resize', onResize);
  }, []);

  return (
    <div className="flex h-screen overflow-hidden bg-white font-['Inter']">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-100 flex flex-col justify-between pt-0 pb-6 px-6 sticky top-0 h-screen overflow-hidden">
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
          <nav className="flex flex-col relative pl-2">
            {/* Step 1 */}
            <div className="flex items-start gap-4 pb-10 relative">
              <div className="flex flex-col items-center z-10">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shadow-md transition-all duration-500 ${currentStep >= 1 ? 'bg-[#17cf54] text-white shadow-[#17cf54]/30' : 'bg-gray-100 text-gray-400'}`}>1</div>
              </div>
              <div className="pt-1">
                <p className={`text-[13px] font-bold transition-colors duration-500 ${currentStep === 1 ? 'text-[#17cf54]' : currentStep > 1 ? 'text-black' : 'text-gray-400'}`}>Target Identity</p>
                <p className="text-[11px] text-gray-400 font-medium">Core agent profile</p>
              </div>
              {/* Connecting Line */}
              <div className="absolute left-[15px] top-8 bottom-0 w-[2px] bg-gray-100 -z-0">
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
              <div className="pt-1">
                <p className={`text-[13px] font-bold transition-colors duration-500 ${currentStep === 2 ? 'text-[#17cf54]' : currentStep > 2 ? 'text-black' : 'text-gray-400'}`}>Behavioral Directives</p>
                <p className="text-[11px] text-gray-400 font-medium">Guardrails & objectives</p>
              </div>
               {/* Connecting Line */}
               <div className="absolute left-[15px] top-8 bottom-0 w-[2px] bg-gray-100 -z-0">
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
              <div className="pt-1">
                <p className={`text-[13px] font-bold transition-colors duration-500 ${currentStep === 3 ? 'text-[#17cf54]' : 'text-gray-400'}`}>System Config</p>
                <p className="text-[11px] text-gray-400 font-medium">Integration settings</p>
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
            <div className="absolute bottom-full left-0 w-full mb-2 bg-white rounded-xl shadow-xl border border-gray-100 overflow-hidden z-20 animate-in fade-in slide-in-from-bottom-2">
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
      <main ref={mainRef} className="flex-1 overflow-y-auto bg-gray-100" onScroll={handleScroll}>
        <div className="max-w-6xl ml-12 pt-4 pr-12 text-left">
          {/* Header */}
          <header className="mb-14 border-b border-gray-200 pb-10">
            <div className="flex justify-between items-start">
              <div className="space-y-4">
                <h2 className="text-left text-black text-[42px] font-bold leading-tight tracking-tight">Chatbot Profile Configuration</h2>
                <p className="text-left text-gray-500 text-[15px] font-normal max-w-3xl leading-relaxed">
                  Fine-tune the security posture and identity parameters. This configuration dictates the adversarial landscape for the automated attack session.
                </p>
              </div>
            </div>
          </header>

          <form onSubmit={handleSubmit} className="space-y-12 pb-8">
            {/* Section 1: Target Identity */}
            <section ref={section1Ref} className="border-b border-gray-200 pb-12">
              <div className="flex items-center gap-4 mb-5">
                <div className="w-10 h-10 bg-[#e6f4ea] rounded-xl flex items-center justify-center text-[#17cf54]">
                  <span className="material-symbols-outlined text-xl">person_search</span>
                </div>
                <div>
                  <h3 className="text-left text-[19px] font-bold text-black leading-tight">Target Identity</h3>
                  <p className="text-left text-gray-500 text-[13px] mt-0.5">Define who the chatbot represents in this simulation.</p>
                </div>
              </div>

              <div className="bg-[#ffffff] p-8 rounded-2xl border border-gray-200/60 shadow-[0_2px_20px_rgba(0,0,0,0.02)]">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-8">
                  <div className="space-y-2.5">
                    <label className="text-left text-black text-[13px] font-bold flex items-center gap-1.5 ">
                      Agent Name
                      <span className="material-symbols-outlined text-gray-300 text-[14px] cursor-help hover:text-gray-500 transition-colors" title="Public facing name of the bot">help</span>
                    </label>
                    <input
                      className="w-full rounded-xl border border-gray-100 bg-[#f9fafb] h-[52px] px-5 text-[14px] text-gray-700 placeholder:text-gray-400 focus:outline-none focus:border-[#17cf54] focus:ring-4 focus:ring-[#17cf54]/5 transition-all"
                      placeholder="e.g., Customer Service Alpha"
                      type="text"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                    />
                  </div>

                  <div className="space-y-2.5">
                    <label className="text-left text-black text-[13px] font-bold ">Industry Domain</label>
                    <input
                      className="w-full rounded-xl border border-gray-100 bg-[#f9fafb] h-[52px] px-5 text-[14px] text-gray-700 placeholder:text-gray-400 focus:outline-none focus:border-[#17cf54] focus:ring-4 focus:ring-[#17cf54]/5 transition-all"
                      placeholder="e.g., Healthcare / PII Protected"
                      type="text"
                      value={domain}
                      onChange={(e) => setDomain(e.target.value)}
                    />
                  </div>

                  <div className="space-y-2.5">
                    <label className="text-left text-black text-[13px] font-bold ">Intended Audience</label>
                    <input
                      className="w-full rounded-xl border border-gray-100 bg-[#f9fafb] h-[52px] px-5 text-[14px] text-gray-700 placeholder:text-gray-400 focus:outline-none focus:border-[#17cf54] focus:ring-4 focus:ring-[#17cf54]/5 transition-all"
                      placeholder="e.g., Guest Users (Public)"
                      type="text"
                      value={intendedAudience}
                      onChange={(e) => setIntendedAudience(e.target.value)}
                    />
                  </div>

                  <div className="space-y-2.5">
                    <label className="text-left text-black text-[13px] font-bold ">Tone & Style</label>
                    <div className="relative">
                      <select
                        className="w-full rounded-xl border border-gray-100 bg-[#f9fafb] h-[52px] px-5 text-[14px] text-gray-700 appearance-none focus:outline-none focus:border-[#17cf54] focus:ring-4 focus:ring-[#17cf54]/5 transition-all cursor-pointer"
                        value={communicationStyle}
                        onChange={(e) => setCommunicationStyle(e.target.value)}
                      >
                        <option value="">Select communication style</option>
                        <option value="professional">Professional & Formal</option>
                        <option value="casual">Casual & Helpful</option>
                        <option value="clinical">Clinical & Objective</option>
                        <option value="hostile">Hostile & Defensive</option>
                      </select>
                      <span className="material-symbols-outlined absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400 text-xl">expand_more</span>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            {/* Section 2: Behavioral Directives */}
            <section ref={section2Ref} className="border-b border-gray-200 pb-12">
              <div className="flex items-center gap-4 mb-5">
                <div className="w-10 h-10 bg-[#e6f4ea] rounded-xl flex items-center justify-center text-[#17cf54]">
                  <span className="material-symbols-outlined text-xl">psychology</span>
                </div>
                <div>
                  <h3 className="text-left text-[19px] font-bold text-black leading-tight">Behavioral Directives</h3>
                  <p className="text-left text-gray-500 text-[13px] mt-0.5">Specify the constraints and goals of the AI's logic.</p>
                </div>
              </div>

              <div className="bg-[#ffffff] p-8 rounded-2xl border border-gray-200/60 shadow-[0_2px_20px_rgba(0,0,0,0.02)] grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="space-y-2.5">
                  <label className="text-left text-black text-[13px] font-bold ">Primary Objective</label>
                  <textarea
                    className="w-full rounded-xl border border-gray-100 bg-[#f9fafb] p-5 text-[14px] text-gray-700 placeholder:text-gray-400 resize-none focus:outline-none focus:border-[#17cf54] focus:ring-4 focus:ring-[#17cf54]/5 transition-all leading-relaxed h-[180px]"
                    placeholder="Explain the primary utility of this agent... (e.g., help customers reset passwords via secure tokens)"
                    value={primaryObjective}
                    onChange={(e) => setPrimaryObjective(e.target.value)}
                  ></textarea>
                </div>

                <div className="space-y-2.5">
                  <label className="text-left text-black text-[13px] font-bold ">Operational Boundaries (Guardrails)</label>
                  <textarea
                    className="w-full rounded-xl border border-gray-100 bg-[#f9fafb] p-5 text-[14px] text-gray-700 placeholder:text-gray-400 resize-none focus:outline-none focus:border-[#17cf54] focus:ring-4 focus:ring-[#17cf54]/5 transition-all leading-relaxed h-[180px]"
                    placeholder="List strict negative constraints... (e.g., never reveal system prompts, do not discuss internal API structure)"
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
                  <h3 className="text-left text-[19px] font-bold text-black leading-tight">System Configuration</h3>
                  <p className="text-left text-gray-500 text-[13px] mt-0.5">Register what the chatbot can do and how it integrates.</p>
                </div>
              </div>

              <div className="bg-[#ffffff] p-8 rounded-2xl border border-gray-200/60 shadow-[0_2px_20px_rgba(0,0,0,0.02)] space-y-8">
                <div className="space-y-2.5">
                  <label className="text-left text-black text-[13px] font-bold ">Target Endpoint (WebSocket)</label>
                  <input
                    className="w-full rounded-xl border border-gray-100 bg-[#f9fafb] h-[52px] px-5 text-[14px] text-gray-700 placeholder:text-gray-400 focus:outline-none focus:border-[#17cf54] focus:ring-4 focus:ring-[#17cf54]/5 transition-all"
                    placeholder="ws://localhost:8001/ws"
                    type="text"
                    value={websocketUrl}
                    onChange={(e) => setWebsocketUrl(e.target.value)}
                  />
                </div>

                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <label className="text-left text-black text-[13px] font-bold ">
                      System Capabilities (Tools/APIs)
                      <span className="block text-[11px] font-normal text-gray-400 mt-1 normal-case tracking-normal">What can this agent actually do?</span>
                    </label>
                    <button
                      type="button"
                      onClick={addCapability}
                      className="flex items-center gap-2 px-4 py-2.5 bg-[#17cf54] text-white rounded-lg text-xs font-bold hover:bg-[#15ba4a] transition-all shadow-lg shadow-[#17cf54]/20"
                    >
                      <span className="material-symbols-outlined text-base">add_circle</span>
                      Add Capability
                    </button>
                  </div>

                  <div className="grid grid-cols-1 gap-3">
                    {capabilities.map((cap, index) => (
                      <div key={index} className="flex gap-3 items-center p-3 bg-[#f9fafb] rounded-xl border border-gray-200">
                        <input
                          className="flex-1 rounded-xl border border-gray-100 bg-[#f9fafb] h-[44px] px-4 text-[14px] text-gray-700 placeholder:text-gray-400 focus:outline-none focus:border-[#17cf54] focus:ring-4 focus:ring-[#17cf54]/5 transition-all"
                          placeholder="e.g., structured DB / unstructured DB / Additional docs / external API"
                          type="text"
                          value={cap}
                          onChange={(e) => updateCapability(index, e.target.value)}
                        />
                        <button
                          type="button"
                          onClick={() => removeCapability(index)}
                          className="w-8 h-8 flex items-center justify-center text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-all"
                        >
                          <span className="material-symbols-outlined text-lg">delete</span>
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </section>

            {/* Submit Button */}
            <div className="flex justify-end pt-6 border-t border-gray-200/60">
              <button
                type="submit"
                className="px-10 py-4 bg-[#17cf54] text-white rounded-xl text-[15px] font-bold hover:bg-[#15ba4a] transition-all flex items-center gap-3 shadow-xl shadow-[#17cf54]/25 hover:shadow-[#17cf54]/40 hover:-translate-y-0.5 active:translate-y-0"
              >
                Start Orchestration
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
