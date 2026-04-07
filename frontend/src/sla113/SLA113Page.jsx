import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
  Activity, Cpu, Database, Shield, Zap, Image as ImageIcon, Music, Layout,
  CreditCard, Users, Terminal, AlertTriangle, ChevronRight, Plus, Minus, Trash2,
  HardDrive, Globe, Ghost, Layers, Factory, CheckCircle2, Moon, RefreshCw, XCircle,
  Settings, Server, Lock, SlidersHorizontal, Key, Network, ShieldCheck, Package,
  BarChart3, Hammer, Code, Grid3X3, Mic, Archive, ChevronDown, Scan, Paintbrush, Scissors
} from 'lucide-react';
import SpriteCutter from './SpriteCutter';

const API = `${process.env.REACT_APP_BACKEND_URL}/api/sla113`;

const CANON_PALETTE = {
  obsidian: "#050505",
  gold: "#D4AF37",
  cyan: "#00C8FF",
  chrome: "#E5E4E2",
  roseGold: "#B76E79",
  deepRed: "#8B0000",
  indigo: "#6366f1"
};

const STYLES = `
  /* SLA113 ISOLATION — Reset all Empire 1 globals */
  #sla113-root, #sla113-root * {
    margin: 0; padding: 0; box-sizing: border-box;
    --bg-primary: initial; --bg-secondary: initial; --bg-card: initial;
    --accent-green: initial; --accent-blue: initial;
  }
  #sla113-root {
    position: fixed; inset: 0; z-index: 9999;
    background: #050505; overflow: hidden;
  }

  :root {
    --obsidian: ${CANON_PALETTE.obsidian};
    --gold: ${CANON_PALETTE.gold};
    --cyan: ${CANON_PALETTE.cyan};
    --chrome: ${CANON_PALETTE.chrome};
    --deepRed: ${CANON_PALETTE.deepRed};
    --indigo: ${CANON_PALETTE.indigo};
  }
  .sla113-scope * { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace !important; }

  .glass-panel {
    background: rgba(13, 13, 13, 0.85);
    backdrop-filter: blur(10px);
    border: 1px solid #1a1a1a;
    box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.5);
  }

  .input-dark {
    background: #000; border: 1px solid #1a1a1a; color: #fff;
    padding: 12px; font-size: 0.75rem; outline: none; width: 100%;
    transition: border-color 0.2s;
  }
  .input-dark:focus { border-color: currentColor; }

  @keyframes scanline { 0% { transform: translateY(-100%); } 100% { transform: translateY(100%); } }
  .scanline {
    position: absolute; top: 0; left: 0; width: 100%; height: 2px;
    background: rgba(255, 255, 255, 0.05);
    animation: scanline 6s linear infinite; pointer-events: none; z-index: 50;
  }

  .tech-border { position: relative; }
  .tech-border::before, .tech-border::after {
    content: ''; position: absolute; width: 8px; height: 8px;
    border: 1px solid rgba(255,255,255,0.2); pointer-events: none;
  }
  .tech-border::before { top: -1px; left: -1px; border-right: none; border-bottom: none; }
  .tech-border::after { bottom: -1px; right: -1px; border-left: none; border-top: none; }

  .tech-border-red { position: relative; }
  .tech-border-red::before, .tech-border-red::after {
    content: ''; position: absolute; width: 8px; height: 8px;
    border: 1px solid rgba(255,85,85,0.6); pointer-events: none;
  }
  .tech-border-red::before { top: -1px; left: -1px; border-right: none; border-bottom: none; }
  .tech-border-red::after { bottom: -1px; right: -1px; border-left: none; border-top: none; }

  .custom-scrollbar::-webkit-scrollbar { width: 4px; }
  .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
  .custom-scrollbar::-webkit-scrollbar-thumb { background: #333; border-radius: 10px; }
  .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #666; }

  .sla113-scope input[type=range] { -webkit-appearance: none; width: 100%; background: transparent; }
  .sla113-scope input[type=range]::-webkit-slider-runnable-track { width: 100%; height: 2px; background: #1f1f1f; }
  .sla113-scope input[type=range]::-webkit-slider-thumb {
    -webkit-appearance: none; height: 12px; width: 12px; border-radius: 0;
    background: currentColor; cursor: pointer; margin-top: -5px;
  }
`;

const THEMES = {
  factory: { hex: CANON_PALETTE.cyan, text: 'text-[#00C8FF]', border: 'border-[#00C8FF]', bg: 'bg-[#00C8FF]', bgAlpha: 'bg-[#00C8FF]/10', label: 'FACTORY', sub: 'Live Operations' },
  empire: { hex: CANON_PALETTE.indigo, text: 'text-[#6366f1]', border: 'border-[#6366f1]', bg: 'bg-[#6366f1]', bgAlpha: 'bg-[#6366f1]/10', label: 'EMPIRE 1', sub: 'Revenue Matrix' },
  foundry: { hex: CANON_PALETTE.gold, text: 'text-[#D4AF37]', border: 'border-[#D4AF37]', bg: 'bg-[#D4AF37]', bgAlpha: 'bg-[#D4AF37]/10', label: 'FOUNDRY', sub: 'Creative Tools' },
  vault: { hex: CANON_PALETTE.deepRed, text: 'text-[#8B0000]', border: 'border-[#8B0000]', bg: 'bg-[#8B0000]', bgAlpha: 'bg-[#8B0000]/10', label: 'VAULT', sub: 'Security Core' }
};

const ALL_NAV_ITEMS = [
  { id: 'FRONTLINE', icon: Activity, partition: 'factory' },
  { id: 'WHITE LABEL MINT', icon: Hammer, partition: 'factory' },
  { id: 'MINT LEDGER', icon: CreditCard, partition: 'empire' },
  { id: 'REVENUE PIPELINES', icon: BarChart3, partition: 'empire' },
  { id: 'OS BUILDER', icon: Layout, partition: 'foundry' },
  { id: 'VISION SMITH', icon: ImageIcon, partition: 'foundry' },
  { id: 'AUDIO FORGE', icon: Music, partition: 'foundry' },
  { id: 'SYSTEM CORE', icon: ShieldCheck, partition: 'vault' },
  { id: 'NIGHT QUEUE', icon: Layers, partition: 'vault' },
];

const ENGINE_PRESETS = [
  { id: 'AAA_FISH_SLOT', name: 'Fish Shooting (Luxury)', desc: 'Casino-grade 3D render, luxury obsidian' },
  { id: 'GTA5_TYPE', name: 'Open World (GTA Style)', desc: 'Cinematic urban grit, hyper-realistic' },
  { id: 'COD_WARFARE', name: 'Tactical FPS (COD Style)', desc: 'Tactical military realism, matte black' },
  { id: 'FANTASY_RPG', name: 'Fantasy RPG', desc: 'Magical, mythical creatures, aztec stone' }
];

const UNIVERSAL_GAME_TYPES = [
  { id: "ARCADE_40", label: "40-Target Arcade", seats: 40 },
  { id: "ARCADE_60", label: "60-Target Enterprise", seats: 60 },
  { id: "SLOTS_20", label: "20-Reel Premium Slots", seats: 20 },
  { id: "OPEN_WORLD", label: "GTA-Type Persistence", seats: 100 },
  { id: "CASINO_SUITE", label: "Full Casino Suite", seats: 100 }
];

const AGENT_NODES = [
  { id: 'shop-alpha', subdomain: 'alpha.empire1.cloud', credits: 12500, rtp: 92, status: 'ONLINE' },
  { id: 'shop-beta', subdomain: 'beta.southern.arc', credits: 4200, rtp: 88, status: 'ONLINE' },
  { id: 'shop-gamma', subdomain: 'gamma.barrio.link', credits: 150, rtp: 94, status: 'LOW_FUNDS' }
];

const EMPIRE_PIPELINES = [
  { id: 1, lane: 1, name: "Lead Qualification Engine", type: "Automation" },
  { id: 2, lane: 1, name: "CRM Syncing Logic", type: "Automation" },
  { id: 3, lane: 2, name: "Pro Voice Over (SaaS)", type: "Utility" },
  { id: 4, lane: 2, name: "SMS/Email Gateway", type: "Utility" },
  { id: 5, lane: 3, name: "White-Label Instance", type: "Sovereign" },
  { id: 6, lane: 3, name: "Managed Sovereignty", type: "Sovereign" },
];

const AdminHeartbeat = ({ processingCount, theme }) => {
  const [computeMode, setComputeMode] = useState('LOCAL');

  return (
    <div className={`border ${theme.border} bg-black/50 p-4 flex flex-col space-y-3 font-mono text-[10px] shadow-[0_0_15px_rgba(0,0,0,0.5)]`} data-testid="admin-heartbeat">
      <div className={`flex justify-between items-center border-b ${theme.border} pb-2`}>
        <span className={`${theme.text} font-bold tracking-widest uppercase flex items-center gap-2`}>
          <Cpu size={12} /> Daemon Uplink
        </span>
        <span className={`h-2 w-2 rounded-full ${theme.bg} animate-pulse`} />
      </div>
      <div className="space-y-2 text-zinc-400 tracking-wider">
        <div className="flex justify-between items-center">
          <span>CPU / RAM</span>
          <span className="text-zinc-200 font-bold">14% / 42.8 GB</span>
        </div>
        <div className="flex justify-between items-center">
          <span>NIGHT QUEUE</span>
          <span className={`${theme.text} font-bold`}>{processingCount} PENDING</span>
        </div>
        <div className="flex justify-between items-center">
          <span>LAST PING</span>
          <span className="text-zinc-500 truncate">12ms</span>
        </div>
      </div>
      <div className="pt-2 border-t border-zinc-800 flex justify-between items-center">
        <span className="text-zinc-500 uppercase">Compute Node</span>
        <button
          onClick={() => setComputeMode(m => m === 'LOCAL' ? 'CLOUD' : 'LOCAL')}
          className={`px-2 py-0.5 border text-[9px] font-bold tracking-widest transition-all ${
            computeMode === 'LOCAL'
              ? `${theme.border} ${theme.text} ${theme.bgAlpha}`
              : 'border-zinc-800 text-zinc-500 bg-black'
          }`}
          data-testid="compute-mode-toggle"
        >
          {computeMode}
        </button>
      </div>
    </div>
  );
};

export default function SLA113Page() {
  const navigate = useNavigate();
  const [partition, setPartition] = useState('foundry');
  const [activeTab, setActiveTab] = useState('OS BUILDER');

  const [revenue] = useState(142500);
  const [isCritical, setIsCritical] = useState(false);
  const [humanMode, setHumanMode] = useState(false);

  // API data
  const [gameTypes, setGameTypes] = useState({});
  const [projects, setProjects] = useState([]);
  const [stats, setStats] = useState({});

  // OS Builder State
  const [osPartitions, setOsPartitions] = useState([{ id: 1, type: 'ARCADE_40', units: 1 }]);
  const [isBuilding, setIsBuilding] = useState(false);
  const [genMode, setGenMode] = useState('night');

  // Vision Smith State
  const [referenceFile, setReferenceFile] = useState(null);
  const [prompt, setPrompt] = useState("");
  const [selectedPreset, setSelectedPreset] = useState('AAA_FISH_SLOT');
  const [visionResult, setVisionResult] = useState(null);
  const [visionLoading, setVisionLoading] = useState(false);
  const [generatedImages, setGeneratedImages] = useState([]);
  const [spriteCutterImage, setSpriteCutterImage] = useState(null);

  // Mint Ledger State
  const [agents, setAgents] = useState([]);

  // Pipeline heartbeats — real pipelines from API
  const [pipelines, setPipelines] = useState([]);
  const [pipelineHeartbeats, setPipelineHeartbeats] = useState({});
  useEffect(() => {
    const interval = setInterval(() => {
      const newHeartbeats = {};
      pipelines.forEach(p => { newHeartbeats[p.id] = Math.random() > 0.7 ? 'active' : 'idle'; });
      setPipelineHeartbeats(newHeartbeats);
    }, 2000);
    return () => clearInterval(interval);
  }, [pipelines]);

  // Night Queue State — real jobs from API
  const [queue, setQueue] = useState([]);

  // System Core State
  const [firewallStrength, setFirewallStrength] = useState(85);
  const [neuralLoad, setNeuralLoad] = useState(12);
  const [coreToggles, setCoreToggles] = useState({
    neuralFirewall: true, stealthMesh: false, quantumBridge: true, autoAudit: true
  });

  // White Label Mint
  const [whiteLabelName, setWhiteLabelName] = useState("");
  const [whiteLabelLogs, setWhiteLabelLogs] = useState([]);
  const [isForgingTenant, setIsForgingTenant] = useState(false);

  // AI Terminal
  const [isTerminalExpanded, setIsTerminalExpanded] = useState(false);
  const [aiInput, setAiInput] = useState("");
  const [aiOutput, setAiOutput] = useState("> SYSTEM_INITIALIZED. READY FOR DIRECTIVE.");
  const [isThinking, setIsThinking] = useState(false);

  const currentTheme = THEMES[partition];
  const activeNavItems = ALL_NAV_ITEMS.filter(item => item.partition === partition);
  const activeProcessingCount = queue.filter(q => q.status === 'processing' || q.status === 'pending').length;

  const totalSeats = useMemo(() => {
    return osPartitions.reduce((acc, p) => {
      const g = UNIVERSAL_GAME_TYPES.find(x => x.id === p.type);
      return acc + (g ? g.seats * p.units : 0);
    }, 0);
  }, [osPartitions]);

  // Fetch backend data
  const fetchData = useCallback(async () => {
    try {
      const [typesRes, projRes, statsRes, tenantsRes, jobsRes, pipelinesRes] = await Promise.all([
        axios.get(`${API}/game-types`),
        axios.get(`${API}/projects`),
        axios.get(`${API}/stats`),
        axios.get(`${API}/tenants`).catch(() => ({ data: { tenants: [] } })),
        axios.get(`${API}/jobs`).catch(() => ({ data: { jobs: [] } })),
        axios.get(`${API}/pipelines`).catch(() => ({ data: { pipelines: [] } })),
      ]);
      setGameTypes(typesRes.data.game_types || {});
      setProjects(projRes.data.projects || []);
      setStats(statsRes.data || {});
      setAgents(tenantsRes.data.tenants || []);
      setQueue(jobsRes.data.jobs || []);
      setPipelines(pipelinesRes.data.pipelines || []);
    } catch (e) {
      console.error("SLA113 data fetch failed:", e);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handlePartitionChange = (p) => {
    setPartition(p);
    const defaultTab = ALL_NAV_ITEMS.find(item => item.partition === p)?.id || '';
    setActiveTab(defaultTab);
  };

  const handleForgeOS = async () => {
    setIsBuilding(true);
    try {
      const gameType = osPartitions[0]?.type === 'OPEN_WORLD' ? 'open_world' : osPartitions[0]?.type === 'SLOTS_20' ? 'slot_machine' : 'fish_shooter';
      await axios.post(`${API}/projects`, { name: `OS_BUILD_${Date.now()}`, game_type: gameType, theme: 'sovereign', target_platform: 'both' });
      await axios.post(`${API}/jobs`, { preset: osPartitions[0]?.type || 'CUSTOM_OS_BUILD', priority: 'high' });
      await fetchData();
    } catch (e) { console.error(e); }
    setIsBuilding(false);
    handlePartitionChange('vault');
    setActiveTab('NIGHT QUEUE');
  };

  const handleVisionSmith = async () => {
    if (!prompt) return;
    setVisionLoading(true);
    try {
      // Generate real image via GPT Image 1
      const imgRes = await axios.post(`${API}/vision/generate-image`, {
        prompt,
        style: selectedPreset === 'GTA5_TYPE' ? 'neon' : selectedPreset === 'COD_WARFARE' ? '3d_render' : selectedPreset === 'FANTASY_RPG' ? 'hand_drawn' : 'pixel_art',
        size: '1024x1024',
      });
      if (imgRes.data.image_base64) {
        setGeneratedImages(prev => [{ base64: imgRes.data.image_base64, prompt: imgRes.data.prompt, style: imgRes.data.style, id: Date.now() }, ...prev]);
      }

      // Also generate asset specs if project exists
      let projectId = projects[0]?.id;
      if (projectId) {
        const res = await axios.post(`${API}/vision/generate`, {
          project_id: projectId, asset_type: 'sprites', style: 'neon', count: 5, custom_prompt: prompt,
        });
        setVisionResult(res.data);
      }
    } catch (e) {
      console.error("Vision generation failed:", e);
      setVisionResult({ error: e.response?.data?.detail || e.message });
    }
    setVisionLoading(false);
  };

  const handleMintWhiteLabel = async () => {
    if (!whiteLabelName || isForgingTenant) return;
    setIsForgingTenant(true);
    setWhiteLabelLogs([`> Initiating Sovereign Mint for: ${whiteLabelName.toUpperCase()}`]);
    try {
      const subdomain = whiteLabelName.toLowerCase().replace(/\s+/g, '-') + '.empire1.cloud';
      setWhiteLabelLogs(p => [...p, `> Validating Root Authority... [OK]`]);
      await new Promise(r => setTimeout(r, 600));
      setWhiteLabelLogs(p => [...p, `> Cloning SLA113 core foundries...`]);
      const res = await axios.post(`${API}/tenants`, { name: whiteLabelName.toUpperCase(), subdomain });
      await new Promise(r => setTimeout(r, 400));
      setWhiteLabelLogs(p => [...p, `> Securing dedicated tenant boundary...`]);
      await new Promise(r => setTimeout(r, 400));
      setWhiteLabelLogs(p => [...p, `> Done. Instance: ${res.data.subdomain} [${res.data.status.toUpperCase()}]`]);
      await fetchData();
    } catch (e) {
      setWhiteLabelLogs(p => [...p, `> [ERROR] ${e.response?.data?.detail || e.message}`]);
    }
    setIsForgingTenant(false);
  };

  const removeQueueItem = async (id) => {
    try {
      await axios.delete(`${API}/jobs/${id}`);
      setQueue(queue.filter(item => item.id !== id));
    } catch (e) { console.error(e); }
  };

  const askAI = async () => {
    if (!aiInput.trim()) return;
    setIsThinking(true);
    setIsTerminalExpanded(true);
    const command = aiInput;
    setAiInput("");
    setAiOutput(prev => prev + `\n> [USER]: ${command}`);
    try {
      const res = await axios.post(`${API}/terminal`, { command, session_id: 'main' });
      setAiOutput(prev => prev + `\n${res.data.response}`);
    } catch (e) {
      setAiOutput(prev => prev + `\n> [ERROR] Overseer unreachable: ${e.message}`);
    }
    setIsThinking(false);
  };

  return (
    <>
      <style dangerouslySetInnerHTML={{ __html: STYLES }} />
      <div className="sla113-scope flex h-screen w-full bg-[#050505] text-zinc-300 font-mono text-sm overflow-hidden select-none" data-testid="sla113-page">

        {/* SIDEBAR */}
        <aside className={`w-72 border-r bg-[#050505] flex flex-col shadow-2xl z-20 shrink-0 transition-colors duration-500 ${currentTheme.border}/30`} data-testid="sla113-sidebar">
          <div className={`p-6 border-b transition-colors duration-500 ${currentTheme.border}/30`}>
            <div className="flex items-center gap-3">
              <div className={`w-8 h-8 border ${currentTheme.border} flex items-center justify-center shadow-[0_0_15px_rgba(255,255,255,0.05)]`}>
                <Shield className={currentTheme.text} size={18} />
              </div>
              <div>
                <h1 className="text-white font-bold tracking-widest text-sm uppercase leading-none">
                  SLA113 <span className="opacity-20 mx-1">//</span> <span className={currentTheme.text}>{currentTheme.label}</span>
                </h1>
                <p className="text-zinc-500 text-[9px] mt-1 tracking-widest uppercase">{currentTheme.sub}</p>
              </div>
            </div>
          </div>

          <nav className="flex-1 py-4 space-y-1 overflow-y-auto custom-scrollbar" data-testid="sla113-nav">
            {activeNavItems.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full flex items-center justify-between px-4 py-3 uppercase tracking-widest text-[10px] transition-all group ${
                    activeTab === item.id
                      ? `${currentTheme.bgAlpha} ${currentTheme.text} border-l-2 ${currentTheme.border}`
                      : 'text-zinc-500 hover:text-zinc-300 border-l-2 border-transparent'
                  }`}
                  data-testid={`nav-${item.id.toLowerCase().replace(/\s/g, '-')}`}
                >
                  <div className="flex items-center gap-3">
                    <Icon size={14} className={activeTab === item.id ? currentTheme.text : 'group-hover:text-zinc-300'} />
                    {item.id}
                  </div>
                  {item.id === 'NIGHT QUEUE' && activeProcessingCount > 0 && (
                    <span className={`w-2 h-2 rounded-full ${currentTheme.bg} animate-pulse`}></span>
                  )}
                </button>
              );
            })}
          </nav>

          <div className={`p-4 border-t transition-colors duration-500 ${currentTheme.border}/30`}>
            <AdminHeartbeat processingCount={activeProcessingCount} theme={currentTheme} />
          </div>

          <button onClick={() => navigate('/')} className={`m-4 p-3 border border-zinc-800 text-zinc-500 text-[9px] uppercase tracking-widest hover:text-zinc-300 hover:border-zinc-600 transition-all`} data-testid="back-to-core">
            BACK TO CORE
          </button>
        </aside>

        {/* MAIN VIEWPORT */}
        <div className="flex-1 flex flex-col relative overflow-hidden bg-[radial-gradient(circle_at_50%_0%,_rgba(255,255,255,0.01)_0%,_transparent_70%)] z-10">

          {/* TOP HEADER */}
          <header className="flex flex-wrap gap-4 items-center justify-between bg-[#050505]/95 border-b border-zinc-900/50 px-8 py-3 z-50 shrink-0" data-testid="sla113-header">
            <div>
              <div className="text-[8px] text-zinc-500 uppercase tracking-widest">Net Revenue</div>
              <div className="text-lg font-black text-white">${revenue.toLocaleString()}</div>
            </div>
            <div className="flex gap-2 items-center">
              {['factory', 'empire', 'foundry', 'vault'].map(p => (
                <button
                  key={p} onClick={() => handlePartitionChange(p)}
                  className={`px-4 py-2 text-[9px] font-bold border transition-all uppercase tracking-widest ${
                    partition === p
                      ? `${THEMES[p].bgAlpha} ${THEMES[p].text} ${THEMES[p].border}`
                      : 'border-zinc-800/50 text-zinc-600 hover:text-zinc-400 bg-black/50'
                  }`}
                  data-testid={`partition-${p}`}
                >
                  {THEMES[p].label}
                </button>
              ))}
              <div className="h-6 w-px bg-zinc-800 mx-2"></div>
              <button onClick={() => setHumanMode(!humanMode)} className={`px-4 py-2 border text-[9px] font-bold transition-all ${humanMode ? currentTheme.border : 'border-zinc-800 text-zinc-500'}`} data-testid="mode-toggle">
                {humanMode ? "HUMAN" : "TECH"}
              </button>
              <button onClick={() => setIsCritical(true)} className="p-2 border border-red-500/20 text-red-500 hover:bg-red-500/10 transition-colors" data-testid="critical-btn">
                <AlertTriangle size={14}/>
              </button>
            </div>
          </header>

          {/* CONTENT */}
          <main className="flex-1 overflow-y-auto p-8 custom-scrollbar relative flex flex-col">
            <div className="scanline"></div>

            {/* FACTORY: FRONTLINE */}
            {partition === 'factory' && activeTab === 'FRONTLINE' && (
              <div className="grid grid-cols-12 gap-6 h-full animate-in fade-in" data-testid="frontline-panel">
                <div className="col-span-8 flex flex-col gap-6">
                  <div className="flex-1 glass-panel border-cyan-500/20 flex flex-col">
                    <div className="p-4 border-b border-cyan-500/20 bg-cyan-900/10 flex justify-between items-center text-[10px] uppercase tracking-widest">
                      <span className="flex items-center gap-2 text-cyan-400"><Zap size={12} fill="currentColor" /> Live Ritual Feed</span>
                      <span className="text-zinc-500">Node: SGV_ELA_WEST</span>
                    </div>
                    <div className="flex-1 p-6 font-mono text-[11px] space-y-3 overflow-y-auto">
                      <p className="text-zinc-600">[02:44:01] Ritual Initialized. Boss: TONATIUH.</p>
                      <p className="text-zinc-400">[02:44:12] Shot detected from Subdomain: shop-alpha.</p>
                      <p className="text-zinc-400">[02:44:15] Credit Debit: 0.50 (SLA113_LEDGER).</p>
                      <p className="text-cyan-400">[02:44:20] Boss Phase Transition: SOLAR_FLARE_INJECTED.</p>
                      <p className="text-[#D4AF37]">[02:44:30] Jackpot Probability: Clamped at 0.00042%.</p>
                      {projects.map((p, i) => (
                        <p key={i} className="text-zinc-400">[LIVE] Project: {p.name} | Type: {p.game_type} | Status: {p.status}</p>
                      ))}
                    </div>
                    <div className="p-4 border-t border-cyan-500/20 flex gap-4 bg-black/50">
                      <input type="text" placeholder="Inject Owner Intelligence..." className="input-dark focus:border-cyan-500" data-testid="frontline-input" />
                      <button className="px-6 py-2 bg-cyan-500/20 border border-cyan-500 text-cyan-400 font-bold uppercase text-[10px] tracking-widest hover:bg-cyan-500 hover:text-black transition-all" data-testid="frontline-execute">Execute</button>
                    </div>
                  </div>
                </div>
                <div className="col-span-4 space-y-6">
                  <div className="glass-panel border-cyan-500/20 p-6 space-y-6">
                    <h3 className="text-cyan-400 text-xs font-bold uppercase tracking-widest border-b border-cyan-500/20 pb-4">Cinematic Engine</h3>
                    <div className="flex justify-center py-6">
                      <div className="w-32 h-32 rounded-full bg-cyan-500/5 border border-cyan-500/30 flex items-center justify-center relative shadow-[0_0_40px_rgba(0,200,255,0.1)]">
                        <div className="w-24 h-24 rounded-full border-2 border-t-cyan-400 border-r-transparent border-b-transparent border-l-transparent animate-spin" />
                        <div className="absolute flex flex-col items-center">
                          <span className="text-cyan-400 font-bold text-xl">94%</span>
                          <span className="text-[9px] text-zinc-500 uppercase">RTP Hold</span>
                        </div>
                      </div>
                    </div>
                    <div className="space-y-2 text-[10px] text-zinc-400">
                      <div className="flex justify-between"><span>Total Projects</span><span className="text-cyan-400 font-bold">{stats.total_projects || 0}</span></div>
                      <div className="flex justify-between"><span>Game Types</span><span className="text-cyan-400 font-bold">{stats.supported_game_types || 0}</span></div>
                      <div className="flex justify-between"><span>AI Engines</span><span className="text-cyan-400 font-bold">{stats.engines?.length || 0}</span></div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* FACTORY: WHITE LABEL MINT */}
            {partition === 'factory' && activeTab === 'WHITE LABEL MINT' && (
              <div className="grid grid-cols-12 gap-8 max-w-7xl mx-auto w-full animate-in fade-in" data-testid="white-label-panel">
                <div className="col-span-4 space-y-6">
                  <div className="glass-panel p-8 space-y-6 border-cyan-500/20">
                    <h3 className="text-cyan-400 text-xs font-black uppercase tracking-[4px] border-b border-zinc-900 pb-4">Instance Minting</h3>
                    <div className="space-y-4">
                      <div>
                        <label className="text-[10px] text-zinc-500 uppercase block mb-2">Instance Name</label>
                        <input value={whiteLabelName} onChange={e => setWhiteLabelName(e.target.value)} placeholder="e.g. BARRIO ARCADE" className="input-dark focus:border-cyan-500 uppercase" data-testid="white-label-name" />
                      </div>
                      <button onClick={handleMintWhiteLabel} disabled={isForgingTenant} className="w-full py-4 bg-cyan-900/20 border border-cyan-500/50 text-cyan-400 hover:bg-cyan-500 hover:text-black font-bold uppercase tracking-widest transition-all" data-testid="mint-deploy-btn">
                        {isForgingTenant ? 'Forging...' : 'Execute Deploy'}
                      </button>
                    </div>
                  </div>
                </div>
                <div className="col-span-8 glass-panel border-cyan-500/20 tech-border p-8 font-mono text-[11px] text-zinc-400 h-[400px] overflow-y-auto custom-scrollbar bg-black/80">
                  {whiteLabelLogs.map((l, i) => <div key={i} className="mb-3">{l}</div>)}
                  {whiteLabelLogs.length === 0 && <div className="opacity-30 animate-pulse uppercase tracking-[4px] flex items-center gap-3"><Terminal size={14}/> Awaiting Deployment Directive...</div>}
                </div>
              </div>
            )}

            {/* EMPIRE: MINT LEDGER */}
            {partition === 'empire' && activeTab === 'MINT LEDGER' && (
              <div className="space-y-6 animate-in fade-in max-w-7xl mx-auto w-full" data-testid="mint-ledger-panel">
                <div className="grid grid-cols-3 gap-6">
                  <div className="glass-panel border-indigo-500/20 p-6 flex items-center justify-between">
                    <div><span className="text-[9px] text-zinc-500 uppercase tracking-[0.2em]">Master Mint Balance</span><h4 className="text-2xl font-bold text-indigo-400 mt-1 font-mono">1,000,000.00</h4></div>
                    <Database size={32} className="text-indigo-400 opacity-20" />
                  </div>
                  <div className="glass-panel border-indigo-500/20 p-6 flex items-center justify-between">
                    <div><span className="text-[9px] text-zinc-500 uppercase tracking-[0.2em]">Total Agent Credits</span><h4 className="text-2xl font-bold text-[#00C8FF] mt-1 font-mono">{agents.reduce((s,a) => s + (a.credits||0), 0).toLocaleString()}.00</h4></div>
                    <Users size={32} className="text-[#00C8FF] opacity-20" />
                  </div>
                  <div className="glass-panel border-indigo-500/20 p-6 flex items-center justify-between">
                    <div><span className="text-[9px] text-zinc-500 uppercase tracking-[0.2em]">Active Tenants</span><h4 className="text-2xl font-bold text-zinc-200 mt-1 font-mono">{agents.length}</h4></div>
                    <Zap size={32} className="text-zinc-500 opacity-20" />
                  </div>
                </div>
                <div className="glass-panel border-indigo-500/20 overflow-hidden">
                  <table className="w-full text-left">
                    <thead className="bg-indigo-500/5 border-b border-indigo-500/20 text-[10px] uppercase tracking-widest text-zinc-500 font-normal">
                      <tr><th className="p-4">Tenant</th><th className="p-4">Subdomain</th><th className="p-4">Credit Balance</th><th className="p-4">RTP Mode</th><th className="p-4 text-right">Actions</th></tr>
                    </thead>
                    <tbody className="text-xs font-mono">
                      {agents.map((agent) => (
                        <tr key={agent.id} className="border-b border-zinc-900/50 hover:bg-white/5 transition-all">
                          <td className="p-4 text-indigo-400 font-bold">{agent.name || agent.id}</td>
                          <td className="p-4 text-zinc-400">{agent.subdomain}</td>
                          <td className="p-4 text-zinc-300">{(agent.credits||0).toLocaleString()}.00</td>
                          <td className="p-4">
                            <span className={`px-2 py-0.5 border text-[9px] ${(agent.rtp_mode||92) >= 94 ? 'border-emerald-500/50 text-emerald-500 bg-emerald-500/10' : (agent.rtp_mode||92) >= 92 ? 'border-amber-500/50 text-amber-500 bg-amber-500/10' : 'border-red-500/50 text-red-500 bg-red-500/10'}`}>
                              {(agent.rtp_mode||92) >= 94 ? 'EASY' : (agent.rtp_mode||92) >= 92 ? 'MEDIUM' : 'HARD'} ({agent.rtp_mode||92}%)
                            </span>
                          </td>
                          <td className="p-4 text-right space-x-2">
                            <button onClick={async () => { await axios.put(`${API}/tenants/${agent.id}/credits?amount=1000`); fetchData(); }} className="text-[9px] border border-indigo-500/30 bg-indigo-500/10 px-3 py-1.5 text-indigo-400 hover:bg-indigo-500 hover:text-black transition-all">+1K</button>
                            <button onClick={async () => { const rtp = prompt('Set RTP (80-99):', agent.rtp_mode||92); if(rtp) { await axios.put(`${API}/tenants/${agent.id}/rtp?rtp=${rtp}`); fetchData(); }}} className="text-[9px] border border-zinc-700 bg-black px-3 py-1.5 text-zinc-400 hover:bg-zinc-800 transition-all">RTP</button>
                          </td>
                        </tr>
                      ))}
                      {agents.length === 0 && <tr><td colSpan={5} className="p-8 text-center text-zinc-500 text-[10px] uppercase tracking-widest">No tenants minted. Use FACTORY &gt; WHITE LABEL MINT.</td></tr>}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* EMPIRE: REVENUE PIPELINES */}
            {partition === 'empire' && activeTab === 'REVENUE PIPELINES' && (
              <div className="animate-in fade-in max-w-7xl mx-auto w-full" data-testid="revenue-pipelines-panel">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                  {pipelines.map(p => {
                    const isActive = pipelineHeartbeats[p.id] === 'active';
                    return (
                      <div key={p.id} className={`p-5 border transition-all relative overflow-hidden ${isActive ? 'bg-indigo-900/20 border-indigo-500/50 shadow-[0_0_15px_rgba(99,102,241,0.1)]' : 'bg-black/50 border-zinc-900/80'}`}>
                        <div className="flex justify-between items-start mb-4 text-indigo-400">
                          {p.lane === 1 ? <Cpu size={16}/> : p.lane === 2 ? <Package size={16}/> : <ShieldCheck size={16}/>}
                          <span className={`w-2 h-2 rounded-full ${isActive ? 'bg-indigo-400 animate-ping' : 'bg-zinc-800'}`}></span>
                        </div>
                        <h4 className="text-xs font-bold text-zinc-200 mb-1">{p.name}</h4>
                        <p className="text-[9px] text-zinc-500 uppercase tracking-widest font-mono">Lane 0{p.lane} // {p.type}</p>
                        <div className="mt-3 flex justify-between text-[9px]">
                          <span className="text-zinc-500">{p.executions || 0} runs</span>
                          <span className="text-indigo-400 font-bold">${(p.revenue || 0).toLocaleString()}</span>
                        </div>
                      </div>
                    );
                  })}
                  {pipelines.length === 0 && <div className="col-span-4 text-center text-zinc-500 text-[10px] uppercase tracking-widest py-12">No pipelines configured</div>}
                </div>
              </div>
            )}

            {/* FOUNDRY: OS BUILDER */}
            {partition === 'foundry' && activeTab === 'OS BUILDER' && (
              <div className="grid grid-cols-12 gap-6 animate-in fade-in max-w-7xl mx-auto w-full" data-testid="os-builder-panel">
                <div className="col-span-7 space-y-6">
                  <div className="glass-panel border-[#D4AF37]/20 p-8 space-y-6">
                    <div className="flex justify-between items-start border-b border-[#D4AF37]/20 pb-4">
                      <div>
                        <h3 className="text-lg text-[#D4AF37] font-bold tracking-widest uppercase">Universal Builder v7</h3>
                        <p className="text-[#D4AF37]/50 text-[10px] mt-1 tracking-widest uppercase">Allocate Custom Clusters</p>
                      </div>
                      <div className="text-right">
                        <p className="text-[10px] text-zinc-500 uppercase tracking-widest">Total Seats</p>
                        <p className="text-2xl font-mono text-[#D4AF37]">{totalSeats}</p>
                      </div>
                    </div>
                    <div className="space-y-4">
                      <div className="flex justify-between items-center text-[10px] uppercase tracking-widest text-zinc-500">
                        <span>OS Clusters</span>
                        <button onClick={() => setOsPartitions([...osPartitions, { id: Date.now(), type: 'SLOTS_20', units: 1 }])} className="text-[#D4AF37] flex items-center gap-1 hover:text-white transition-all bg-[#D4AF37]/10 px-3 py-1 border border-[#D4AF37]/30" data-testid="add-cluster-btn">
                          <Plus size={12} /> Add Cluster
                        </button>
                      </div>
                      <div className="space-y-3 max-h-[200px] overflow-y-auto pr-2 custom-scrollbar">
                        {osPartitions.map((part, index) => (
                          <div key={part.id} className="flex gap-3 items-center group">
                            <select value={part.type} onChange={(e) => { const n = [...osPartitions]; n[index].type = e.target.value; setOsPartitions(n); }} className="flex-1 input-dark uppercase tracking-widest focus:border-[#D4AF37] text-zinc-300">
                              {UNIVERSAL_GAME_TYPES.map(g => (<option key={g.id} value={g.id}>{g.label}</option>))}
                            </select>
                            <div className="flex items-center gap-2 bg-black border border-zinc-800 px-3 py-2">
                              <span className="text-[9px] text-zinc-500 uppercase">Units</span>
                              <input type="number" min="1" value={part.units} onChange={(e) => { const n = [...osPartitions]; n[index].units = parseInt(e.target.value) || 1; setOsPartitions(n); }} className="w-8 bg-transparent text-[#D4AF37] text-xs text-center focus:outline-none font-bold" />
                            </div>
                            <button onClick={() => setOsPartitions(osPartitions.filter(p => p.id !== part.id))} className="p-3 text-zinc-600 hover:text-red-500 bg-black border border-zinc-800 transition-colors"><Trash2 size={14} /></button>
                          </div>
                        ))}
                      </div>
                    </div>
                    <div className="pt-4 border-t border-zinc-800/50">
                      <h3 className="text-[10px] font-bold uppercase tracking-widest text-zinc-500 mb-3">Generation Mode</h3>
                      <div className="grid grid-cols-2 gap-4">
                        <button onClick={() => setGenMode('fast')} className={`flex flex-col items-start p-4 border transition-all ${genMode === 'fast' ? 'bg-[#D4AF37]/10 border-[#D4AF37]' : 'bg-black border-zinc-800'}`}>
                          <div className="flex items-center justify-between w-full mb-2">
                            <div className={`p-1.5 ${genMode === 'fast' ? 'text-[#D4AF37]' : 'text-zinc-500'}`}><Zap size={14} /></div>
                            {genMode === 'fast' && <CheckCircle2 className="text-[#D4AF37]" size={14} />}
                          </div>
                          <div className={`text-[10px] font-bold uppercase tracking-widest ${genMode === 'fast' ? 'text-[#D4AF37]' : 'text-zinc-300'}`}>Fast Render</div>
                          <div className="text-[9px] text-zinc-500 mt-1">Instant API</div>
                        </button>
                        <button onClick={() => setGenMode('night')} className={`flex flex-col items-start p-4 border transition-all ${genMode === 'night' ? 'bg-[#D4AF37]/10 border-[#D4AF37]' : 'bg-black border-zinc-800'}`}>
                          <div className="flex items-center justify-between w-full mb-2">
                            <div className={`p-1.5 ${genMode === 'night' ? 'text-[#D4AF37]' : 'text-zinc-500'}`}><Moon size={14} /></div>
                            {genMode === 'night' && <CheckCircle2 className="text-[#D4AF37]" size={14} />}
                          </div>
                          <div className={`text-[10px] font-bold uppercase tracking-widest ${genMode === 'night' ? 'text-[#D4AF37]' : 'text-zinc-300'}`}>Night Shift</div>
                          <div className="text-[9px] text-zinc-500 mt-1">Batch Queue</div>
                        </button>
                      </div>
                    </div>
                    <button onClick={handleForgeOS} disabled={isBuilding} className={`w-full py-5 font-black tracking-[0.3em] uppercase transition-all text-xs border mt-4 ${isBuilding ? 'border-zinc-800 text-zinc-700 bg-transparent' : 'border-[#D4AF37] text-black bg-[#D4AF37] hover:bg-[#F3E5AB]'}`} data-testid="forge-os-btn">
                      {isBuilding ? 'Compiling OS...' : 'Forge OS Container'}
                    </button>
                  </div>
                </div>
                <div className="col-span-5 glass-panel border-[#D4AF37]/20 flex flex-col">
                  <div className="p-4 border-b border-[#D4AF37]/20 flex justify-between items-center text-[10px] uppercase tracking-widest bg-[#D4AF37]/5">
                    <span className="text-[#D4AF37] font-bold">Build Architecture Ledger</span>
                    <Database size={12} className="text-[#D4AF37]" />
                  </div>
                  <div className="p-6 space-y-3 text-[10px] font-mono overflow-y-auto custom-scrollbar flex-1">
                    {projects.length > 0 ? projects.map((p, i) => (
                      <div key={i} className="flex justify-between items-center p-3 border border-zinc-900 bg-black/50">
                        <span className="text-zinc-300">{p.name}</span>
                        <span className="text-[#D4AF37]">{p.game_type}</span>
                      </div>
                    )) : (
                      <div className="flex flex-col items-center justify-center text-center h-full opacity-50 space-y-4">
                        <Layout size={48} className="text-[#D4AF37]"/>
                        <span className="text-zinc-400 uppercase tracking-[0.2em]">Awaiting Compile Directive</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* FOUNDRY: VISION SMITH */}
            {partition === 'foundry' && activeTab === 'VISION SMITH' && (
              <div className="grid grid-cols-12 gap-6 animate-in fade-in max-w-7xl mx-auto w-full" data-testid="vision-smith-panel">
                <div className="col-span-4 space-y-6">
                  <div className="glass-panel border-[#D4AF37]/20 p-8 space-y-6 shadow-xl">
                    <div className="border-b border-[#D4AF37]/20 pb-4">
                      <h3 className="text-lg text-[#D4AF37] font-bold tracking-widest uppercase flex items-center gap-2"><ImageIcon size={18} /> Prompt Architect</h3>
                      <p className="text-[10px] text-zinc-400 mt-1 tracking-widest uppercase">Style Injection Enforcement</p>
                    </div>
                    <div className="space-y-6">
                      <div>
                        <label className="block text-[10px] text-[#D4AF37] mb-3 uppercase tracking-widest font-bold">1. Style Anchor</label>
                        <div className={`border-2 border-dashed transition-all p-8 text-center relative group bg-black/50 ${referenceFile ? 'border-emerald-500/50' : 'border-zinc-800 hover:border-[#D4AF37]/50'}`}>
                          <input type="file" className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10" onChange={(e) => setReferenceFile(e.target.files[0])} data-testid="style-anchor-upload" />
                          {referenceFile ? (
                            <div className="flex flex-col items-center">
                              <span className="text-emerald-400 text-[10px] font-bold uppercase tracking-widest mb-1">Target Locked</span>
                              <span className="text-zinc-500 text-[9px]">{referenceFile.name}</span>
                            </div>
                          ) : (
                            <div className="text-zinc-500 flex flex-col items-center gap-3">
                              <Scan size={24} className="opacity-50" />
                              <span className="text-[10px] uppercase tracking-widest">Ingest Master Canon Art</span>
                            </div>
                          )}
                        </div>
                      </div>
                      <div>
                        <label className="block text-[10px] text-[#D4AF37] mb-3 uppercase tracking-widest font-bold">2. Engine Preset</label>
                        <select value={selectedPreset} onChange={(e) => setSelectedPreset(e.target.value)} className="input-dark uppercase tracking-widest focus:border-[#D4AF37]" data-testid="engine-preset-select">
                          {ENGINE_PRESETS.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
                        </select>
                      </div>
                      <div>
                        <label className="block text-[10px] text-[#D4AF37] mb-3 uppercase tracking-widest font-bold">3. Directive</label>
                        <textarea rows={3} value={prompt} onChange={(e) => setPrompt(e.target.value)} placeholder="Enter boss concept..." className="input-dark resize-none focus:border-[#D4AF37]" data-testid="vision-directive-input" />
                      </div>
                    </div>
                    <button onClick={handleVisionSmith} disabled={visionLoading || !prompt} className={`w-full py-4 font-bold tracking-[0.3em] uppercase transition-all text-xs border ${visionLoading || !prompt ? 'border-zinc-800 text-zinc-700 bg-black' : 'border-[#D4AF37] text-black bg-[#D4AF37] hover:bg-[#F3E5AB]'}`} data-testid="engage-smith-btn">
                      {visionLoading ? 'Generating...' : !prompt ? 'Directive Required' : 'Engage Smith'}
                    </button>
                  </div>
                </div>
                <div className="col-span-8 flex flex-col gap-6">
                  <div className="flex-1 glass-panel border-[#D4AF37]/20 flex flex-col overflow-hidden relative min-h-[500px]">
                    {(generatedImages.length > 0 || visionResult) ? (
                      <div className="flex-1 p-6 overflow-y-auto custom-scrollbar">
                        {generatedImages.length > 0 && (
                          <>
                            <div className="flex items-center gap-3 mb-4">
                              <span className="text-emerald-400 text-[10px] font-bold uppercase tracking-widest border border-emerald-500/30 bg-emerald-500/10 px-3 py-1">IMAGE GENERATED</span>
                              <span className="text-zinc-500 text-[10px]">{generatedImages.length} image(s)</span>
                            </div>
                            <div className="grid grid-cols-2 gap-3 mb-6">
                              {generatedImages.map((img) => (
                                <div key={img.id} className="border border-zinc-800 bg-black/50 overflow-hidden group relative">
                                  <img src={`data:image/png;base64,${img.base64}`} alt={img.prompt} className="w-full h-auto" />
                                  <div className="absolute bottom-0 left-0 right-0 p-3 bg-gradient-to-t from-black/90 to-transparent flex items-end justify-between">
                                    <div>
                                      <p className="text-[10px] text-zinc-300 truncate">{img.prompt}</p>
                                      <a href={`data:image/png;base64,${img.base64}`} download={`sla113_${img.id}.png`} className="text-[9px] text-[#D4AF37] uppercase tracking-widest hover:text-white transition-colors">Download</a>
                                    </div>
                                    <button
                                      onClick={() => setSpriteCutterImage(img.base64)}
                                      className="px-3 py-1.5 border border-cyan-500/50 bg-cyan-500/10 text-cyan-400 text-[9px] uppercase tracking-widest font-bold hover:bg-cyan-500 hover:text-black transition-all flex items-center gap-1.5"
                                      data-testid={`cut-sprite-btn-${img.id}`}
                                    >
                                      <Scissors size={10} /> Cut
                                    </button>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </>
                        )}
                        {visionResult && !visionResult.error && (
                          <>
                            <div className="flex items-center gap-3 mb-4">
                              <span className="text-emerald-400 text-[10px] font-bold uppercase tracking-widest border border-emerald-500/30 bg-emerald-500/10 px-3 py-1">ASSET SPECS</span>
                              <span className="text-zinc-500 text-[10px]">{visionResult.generation_time}s</span>
                            </div>
                            <div className="grid grid-cols-2 gap-3">
                              {visionResult.assets?.map((asset, i) => (
                                <div key={i} className="p-4 border border-zinc-800 bg-black/50">
                                  <h4 className="text-[#D4AF37] font-bold text-xs mb-2">{asset.name || `Asset ${i+1}`}</h4>
                                  <p className="text-zinc-400 text-[10px] leading-relaxed">{asset.description}</p>
                                  {asset.color_palette && (
                                    <div className="flex gap-1 mt-2">{asset.color_palette.map((c, j) => <span key={j} className="w-4 h-4 border border-zinc-700" style={{background: c}} />)}</div>
                                  )}
                                </div>
                              ))}
                            </div>
                          </>
                        )}
                        {visionResult?.error && <div className="p-4 border border-red-500/30 bg-red-500/5 text-red-400 text-[11px] font-mono">{visionResult.error}</div>}
                      </div>
                    ) : (
                      <div className="flex-1 flex items-center justify-center opacity-20">
                        <div className="text-center text-[#D4AF37] uppercase tracking-widest flex flex-col items-center gap-6">
                          <Paintbrush size={64} className="opacity-20" />
                          <span className="text-[10px] font-bold tracking-[4px]">Awaiting Architectural Engagement</span>
                        </div>
                      </div>
                    )}
                    <div className="h-32 bg-black/80 backdrop-blur-md border-t border-[#D4AF37]/20 p-6 font-mono text-[11px] text-zinc-500 overflow-y-auto leading-relaxed">
                      <p>{'>'} SYSTEM READY. PALETTE LOCK: <span className="text-zinc-300">#050505, #D4AF37, #00C8FF</span></p>
                      <p>{'>'} STYLE ENFORCEMENT: <span className="text-[#D4AF37]">CHICANO MURAL / AZTEC GEOMETRY</span></p>
                      {generatedImages.length > 0 && <p className="text-emerald-400">{'>'} GPT IMAGE 1: {generatedImages.length} IMAGE(S) FORGED.</p>}
                      {visionResult && !visionResult.error && <p className="text-emerald-400">{'>'} ASSET SPECS: {visionResult.assets?.length || 0} GENERATED.</p>}
                      {visionLoading && <p className="text-[#D4AF37] animate-pulse">{'>'} ENGAGING SMITH... GENERATING...</p>}
                      {!visionResult && !visionLoading && generatedImages.length === 0 && <p className="animate-pulse mt-4">{'>'} STANDING BY FOR OPERATOR INPUT...</p>}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* FOUNDRY: AUDIO FORGE */}
            {partition === 'foundry' && activeTab === 'AUDIO FORGE' && (
              <div className="grid grid-cols-12 gap-6 h-full animate-in fade-in max-w-7xl mx-auto w-full" data-testid="audio-forge-panel">
                <div className="col-span-8 flex flex-col gap-6">
                  <div className="flex-1 glass-panel border-[#D4AF37]/20 flex flex-col justify-center p-12 relative overflow-hidden shadow-2xl">
                    <div className="flex items-end justify-center gap-1 h-40 z-10">
                      {[...Array(48)].map((_, i) => (
                        <div key={i} className="w-1.5 bg-[#D4AF37]/80 transition-all duration-300 animate-pulse" style={{ height: `${Math.random() * 100}%`, animationDelay: `${i * 0.05}s` }} />
                      ))}
                    </div>
                    <div className="absolute top-6 left-6 flex items-center gap-3 text-[10px] text-[#D4AF37] uppercase tracking-[4px] font-bold"><Music size={14} /> FMOD Master Bus Routing</div>
                  </div>
                </div>
                <div className="col-span-4 space-y-6">
                  <div className="glass-panel border-[#D4AF37]/20 p-8 space-y-8">
                    <h3 className="text-[#D4AF37] text-xs font-bold uppercase tracking-widest border-b border-[#D4AF37]/20 pb-4">DSP Controls</h3>
                    <div className="space-y-6">
                      <div className="space-y-3">
                        <div className="flex justify-between text-[10px] uppercase tracking-widest text-zinc-400 font-bold"><span>Ambience Bloom</span><span>72%</span></div>
                        <input type="range" defaultValue={72} className="text-[#D4AF37]" />
                      </div>
                      <div className="space-y-3">
                        <div className="flex justify-between text-[10px] uppercase tracking-widest text-zinc-400 font-bold"><span>Low End Sub</span><span>85%</span></div>
                        <input type="range" defaultValue={85} className="text-[#D4AF37]" />
                      </div>
                    </div>
                    <button className="w-full py-4 bg-[#D4AF37]/10 border border-[#D4AF37] text-[#D4AF37] font-bold uppercase text-[10px] tracking-[2px] hover:bg-[#D4AF37] hover:text-black transition-all mt-8">Export Bank (.bank)</button>
                  </div>
                </div>
              </div>
            )}

            {/* VAULT: SYSTEM CORE */}
            {partition === 'vault' && activeTab === 'SYSTEM CORE' && (
              <div className="grid grid-cols-12 gap-8 animate-in fade-in max-w-7xl mx-auto w-full" data-testid="system-core-panel">
                <div className="col-span-12 lg:col-span-5 space-y-6">
                  <div className="glass-panel border-red-500/20 p-8 space-y-6 tech-border-red">
                    <h3 className="text-red-500 text-xs font-black uppercase tracking-[4px] border-b border-red-500/20 pb-4 flex items-center gap-3"><Lock size={16}/> Kernel Security Matrix</h3>
                    <div className="grid grid-cols-1 gap-4">
                      {Object.entries(coreToggles).map(([key, active]) => (
                        <div key={key} className="flex justify-between items-center bg-black/50 border border-red-500/10 p-4 hover:border-red-500/30 transition-all">
                          <div className="flex flex-col">
                            <span className="text-[10px] text-zinc-200 font-bold uppercase tracking-widest">{key.replace(/([A-Z])/g, ' $1')}</span>
                            <span className="text-[8px] text-zinc-500 mt-1 uppercase">Sovereign Encryption: <span className={active ? 'text-red-500' : 'text-zinc-600'}>{active ? 'ENFORCED' : 'BYPASS'}</span></span>
                          </div>
                          <button onClick={() => setCoreToggles(p => ({...p, [key]: !active}))} className={`w-12 h-6 border transition-all relative ${active ? 'border-red-500 bg-red-500/10' : 'border-zinc-800 bg-black'}`}>
                            <div className={`absolute top-[3px] w-3 h-3 transition-all ${active ? 'right-1 bg-red-500' : 'left-1 bg-zinc-800'}`}></div>
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
                <div className="col-span-12 lg:col-span-7 space-y-6">
                  <div className="glass-panel border-red-500/20 p-8">
                    <h3 className="text-red-500 text-xs font-black uppercase tracking-[4px] border-b border-red-500/20 pb-4 mb-8 flex items-center gap-3"><SlidersHorizontal size={16}/> Hardware Allocation</h3>
                    <div className="space-y-10 text-red-500">
                      <div className="space-y-4">
                        <div className="flex justify-between items-end"><span className="text-[10px] text-zinc-400 font-bold uppercase tracking-widest">Firewall Strength</span><span className="font-mono text-xl font-bold">{firewallStrength}%</span></div>
                        <input type="range" min="0" max="100" value={firewallStrength} onChange={e => setFirewallStrength(Number(e.target.value))} />
                      </div>
                      <div className="space-y-4">
                        <div className="flex justify-between items-end"><span className="text-[10px] text-zinc-400 font-bold uppercase tracking-widest">Neural Compute Load</span><span className="font-mono text-xl font-bold">{neuralLoad} Ghz</span></div>
                        <input type="range" min="0" max="64" value={neuralLoad} onChange={e => setNeuralLoad(Number(e.target.value))} />
                      </div>
                    </div>
                  </div>
                  <div className="grid grid-cols-3 gap-4">
                    {[{icon: Key, label: 'Rotate Keys'}, {icon: HardDrive, label: 'Flush Buffers'}, {icon: Network, label: 'Ping Nodes'}].map(item => {
                      const Icon = item.icon;
                      return (
                        <div key={item.label} className="glass-panel border-red-500/20 p-6 flex flex-col items-center justify-center text-center group hover:border-red-500 transition-all cursor-pointer bg-black/50">
                          <Icon size={20} className="text-zinc-600 group-hover:text-red-500 mb-3 transition-colors"/>
                          <span className="text-[9px] text-zinc-400 font-bold uppercase tracking-widest group-hover:text-red-500 transition-colors">{item.label}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}

            {/* VAULT: NIGHT QUEUE */}
            {partition === 'vault' && activeTab === 'NIGHT QUEUE' && (
              <div className="glass-panel border-red-500/20 overflow-hidden shadow-lg animate-in fade-in max-w-7xl mx-auto w-full" data-testid="night-queue-panel">
                <table className="w-full text-left text-sm">
                  <thead className="bg-red-500/5 border-b border-red-500/20 text-red-500/60">
                    <tr>
                      <th className="p-5 font-bold uppercase tracking-[0.2em] text-[10px]">Job ID</th>
                      <th className="p-5 font-bold uppercase tracking-[0.2em] text-[10px]">Target Preset</th>
                      <th className="p-5 font-bold uppercase tracking-[0.2em] text-[10px]">Status</th>
                      <th className="p-5 font-bold uppercase tracking-[0.2em] text-[10px]">Progress</th>
                      <th className="p-5 font-bold uppercase tracking-[0.2em] text-[10px] text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-red-500/10">
                    {queue.length === 0 ? (
                      <tr><td colSpan={5} className="p-12 text-center text-red-500/50 text-[10px] uppercase tracking-[4px]">Vault Queue is empty.</td></tr>
                    ) : queue.map((item) => (
                      <tr key={item.id} className="hover:bg-red-500/5 transition-colors bg-black/50">
                        <td className="p-5 font-bold text-zinc-200 text-xs">{item.id}</td>
                        <td className="p-5 text-red-400 font-mono text-[10px]">{item.preset}</td>
                        <td className="p-5">
                          <span className={`px-2 py-1 rounded-sm text-[9px] font-bold tracking-widest uppercase border ${
                            item.status === 'processing' ? 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30' :
                            item.status === 'completed' ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/30' :
                            item.status === 'failed' ? 'bg-red-500/10 text-red-500 border-red-500/30' :
                            'bg-zinc-800/50 text-zinc-400 border-zinc-700'
                          }`}>{item.status}</span>
                        </td>
                        <td className="p-5">
                          <div className="flex items-center gap-3">
                            <div className="h-1.5 w-full max-w-[120px] bg-black border border-red-500/20 overflow-hidden">
                              <div className={`h-full transition-all duration-500 ${item.status === 'completed' ? 'bg-emerald-500' : item.status === 'failed' ? 'bg-red-500' : 'bg-cyan-500'}`} style={{ width: `${item.progress}%` }} />
                            </div>
                            <span className="text-[10px] font-mono text-zinc-500">{item.progress}%</span>
                          </div>
                        </td>
                        <td className="p-5 text-right">
                          <div className="flex justify-end gap-3">
                            {item.status === 'failed' && <button className="p-1.5 text-zinc-600 hover:text-cyan-400 transition-colors"><RefreshCw size={14} /></button>}
                            <button onClick={() => removeQueueItem(item.id)} className="p-1.5 text-zinc-600 hover:text-red-500 transition-colors"><XCircle size={14} /></button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            <div className={`shrink-0 transition-all duration-300 ${isTerminalExpanded ? 'h-56' : 'h-24'}`}></div>
          </main>

          {/* AI TERMINAL */}
          <div className={`absolute bottom-0 left-0 w-full bg-[#050505]/95 backdrop-blur-xl border-t transition-colors duration-500 ${currentTheme.border} z-50 shadow-[0_-10px_30px_rgba(0,0,0,0.8)]`} data-testid="ai-terminal">
            <div className="max-w-7xl mx-auto flex flex-col">
              {isTerminalExpanded && (
                <div className="p-6 pb-2 flex flex-col gap-4 animate-in slide-in-from-bottom-2 duration-300">
                  <div className={`flex items-center gap-3 border-b border-zinc-800 pb-2 text-[10px] font-black uppercase tracking-[4px] ${currentTheme.text}`}>
                    <div className={`w-2 h-2 rounded-full ${currentTheme.bg} animate-pulse`}></div>
                    <span>Overseer Uplink // SLA113 Core</span>
                  </div>
                  <div className="font-mono text-[11px] text-zinc-400 leading-relaxed bg-black/80 p-4 min-h-[80px] border-l-2 border-zinc-800 max-h-[140px] overflow-y-auto custom-scrollbar">
                    <pre className="whitespace-pre-wrap">{aiOutput}</pre>
                    {isThinking && <span className="inline-block w-2 h-4 bg-zinc-500 animate-pulse ml-2 align-middle"></span>}
                  </div>
                </div>
              )}
              <div className="p-4 flex gap-4 items-stretch bg-black/40">
                <button onClick={() => setIsTerminalExpanded(!isTerminalExpanded)} className="px-4 border border-zinc-800 bg-black hover:border-zinc-600 text-zinc-400 transition-colors flex items-center justify-center" data-testid="terminal-toggle">
                  {isTerminalExpanded ? <ChevronDown size={16}/> : <Terminal size={16}/>}
                </button>
                <input
                  value={aiInput} onChange={e => setAiInput(e.target.value)} onKeyPress={e => e.key === 'Enter' && askAI()}
                  placeholder="Command the Sovereign Core..."
                  className="flex-grow bg-black border border-zinc-800 p-3 text-xs focus:outline-none focus:border-zinc-600 text-zinc-300 font-mono placeholder:text-zinc-600"
                  data-testid="ai-terminal-input"
                />
                <button onClick={askAI} disabled={isThinking || !aiInput.trim()} className={`px-8 uppercase text-[10px] font-bold ${currentTheme.bgAlpha} ${currentTheme.text} border ${currentTheme.border} hover:bg-black transition-all flex items-center justify-center`} data-testid="ai-terminal-execute">
                  Execute
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* CRITICAL DRIFT OVERLAY */}
      {isCritical && (
        <div className="fixed inset-0 z-[100] bg-black/95 backdrop-blur-xl flex items-center justify-center p-6 animate-in fade-in" data-testid="critical-overlay">
          <div className="max-w-md w-full border-2 border-red-600 bg-[#050505] p-10 space-y-8 relative overflow-hidden tech-border-red">
            <div className="absolute top-0 left-0 w-full h-1 bg-[repeating-linear-gradient(45deg,#dc2626,#dc2626_10px,#000_10px,#000_20px)]" />
            <div className="absolute bottom-0 left-0 w-full h-1 bg-[repeating-linear-gradient(45deg,#dc2626,#dc2626_10px,#000_10px,#000_20px)]" />
            <div className="text-center space-y-2 relative z-10">
              <div className="flex justify-center mb-6">
                <div className="w-20 h-20 border-2 border-red-600 flex items-center justify-center rounded-full animate-pulse bg-red-600/10">
                  <AlertTriangle size={36} className="text-red-500" />
                </div>
              </div>
              <h2 className="text-3xl font-black text-red-500 tracking-[0.3em] uppercase">Critical Drift</h2>
              <p className="text-zinc-500 text-[10px] tracking-[4px] uppercase mt-4">Manual Override Required</p>
            </div>
            <div className="space-y-4 font-mono text-[11px] text-zinc-400 text-center bg-black p-6 border border-zinc-900 relative z-10 shadow-inner">
              <p>Master Admin connection heartbeat lost.</p>
              <p className="text-cyan-500 font-bold">SLA113 PIPELINE DETACHED.</p>
              <p className="text-[#D4AF37] mt-4 text-[9px] leading-relaxed uppercase">System is entering preservation mode. All Night-Shift generations paused until re-authentication.</p>
            </div>
            <button onClick={() => setIsCritical(false)} className="w-full py-5 bg-red-600/10 border border-red-600 text-red-500 font-black tracking-[0.3em] uppercase text-xs hover:bg-red-600 hover:text-black transition-all relative z-10" data-testid="reinitialize-btn">
              Reinitialize Ledger
            </button>
          </div>
        </div>
      )}

      {/* SPRITE CUTTER MODAL */}
      {spriteCutterImage && (
        <SpriteCutter
          imageBase64={spriteCutterImage}
          onClose={() => setSpriteCutterImage(null)}
        />
      )}
    </>
  );
}
