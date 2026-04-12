import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
  Activity, Cpu, Database, Shield, Zap, Image as ImageIcon, Music, Layout,
  CreditCard, Users, Terminal, AlertTriangle, ChevronRight, Plus, Minus, Trash2,
  HardDrive, Globe, Ghost, Layers, Factory, CheckCircle2, Moon, RefreshCw, XCircle,
  Settings, Server, Lock, SlidersHorizontal, Key, Network, ShieldCheck, Package,
  BarChart3, Hammer, Code, Grid3X3, Mic, Archive, ChevronDown, Scan, Paintbrush, Scissors,
  Rocket, FileCheck, Upload, Play, ExternalLink, CloudLightning, Link2, Skull, Heart, Swords
} from 'lucide-react';
import SpriteCutter from './SpriteCutter';
import DependencyGraph from './DependencyGraph';
import FrontlinePanel from './FrontlinePanel';
import AudioForgePanel from './panels/AudioForgePanel';
import { ArtTechNexusPanel, MatrixParamsPanel } from './panels/VaultAdminPanels';
import { synthesizeFromAsset, playBuffer, stopSource, bufferToWav, downloadWav } from './audioSynth';

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
  { id: 'DEPLOY CENTER', icon: Upload, partition: 'factory' },
  { id: 'UNIVERSES', icon: Globe, partition: 'factory' },
  { id: 'MINT LEDGER', icon: CreditCard, partition: 'empire' },
  { id: 'REVENUE PIPELINES', icon: BarChart3, partition: 'empire' },
  { id: 'BESTIARY', icon: Skull, partition: 'empire' },
  { id: 'OS BUILDER', icon: Layout, partition: 'foundry' },
  { id: 'VISION SMITH', icon: ImageIcon, partition: 'foundry' },
  { id: 'AUDIO FORGE', icon: Music, partition: 'foundry' },
  { id: 'BUILD PIPELINE', icon: Rocket, partition: 'vault' },
  { id: 'COMPLIANCE', icon: FileCheck, partition: 'vault' },
  { id: 'ARTTECH NEXUS', icon: Grid3X3, partition: 'vault' },
  { id: 'MATRIX PARAMS', icon: SlidersHorizontal, partition: 'vault' },
  { id: 'SYSTEM CORE', icon: ShieldCheck, partition: 'vault' },
  { id: 'NIGHT QUEUE', icon: Layers, partition: 'vault' },
];

const BOSS_BESTIARY = [
  {
    id: 'XOCHIPILLI',
    name: 'Xochipilli Scathed',
    title: 'Sun Priest of the Burning Codex',
    tier: 'MYTHIC',
    hp: 850000,
    credits: { left: 3500, right: 2400 },
    image: 'https://customer-assets.emergentagent.com/job_3653cf8a-8710-488d-846f-2f0428b714dd/artifacts/7v5cck22_boss.jpg',
    spriteSheet: null,
    attacks: ['Solar Flare Staff', 'Calendar Shield Bash', 'Obsidian Cannon Barrage', 'Flower of Fire'],
    weakness: 'Water / Ice',
    lore: 'Once the god of flowers, art and song — now a skeletal harbinger wielding the burning codex of the Fifth Sun. His Aztec armor cracks with lava, each flower on his body a trapped soul.',
    rtp: '94.2%',
    theme: 'Aztec / Mesoamerican',
  },
  {
    id: 'LOBO_NEGRO',
    name: 'Lobo Negro',
    title: 'Spirit Wolf of the Golden Spiral',
    tier: 'LEGENDARY',
    hp: 620000,
    credits: { left: 2800, right: 1900 },
    image: 'https://customer-assets.emergentagent.com/job_3653cf8a-8710-488d-846f-2f0428b714dd/artifacts/row23xof_bossf.png',
    spriteSheet: 'https://customer-assets.emergentagent.com/job_3653cf8a-8710-488d-846f-2f0428b714dd/artifacts/g7h5sjnl_spritesheet1%20%281%29.jpg',
    attacks: ['Shadow Lunge', 'Gold Glyph Howl', 'Spiral Mark Drain', 'Pack Summon'],
    weakness: 'Lightning / Holy',
    lore: 'A massive black wolf branded with ancient golden Aztec glyphs. Each spiral burned into his fur is a pact with the underworld. His amber eyes see through walls and into the spirit realm.',
    rtp: '93.8%',
    theme: 'Aztec / Spirit Animal',
  },
  {
    id: 'LA_REINA',
    name: 'La Reina Oscura',
    title: 'Queen of the Obsidian Court',
    tier: 'MYTHIC',
    hp: 780000,
    credits: { left: 4200, right: 3100 },
    image: 'https://customer-assets.emergentagent.com/job_3653cf8a-8710-488d-846f-2f0428b714dd/artifacts/row23xof_bossf.png',
    spriteSheet: null,
    attacks: ['Obsidian Blade Dance', 'Shadow Crown Pulse', 'Spirit Chain Bind', 'Eclipse Judgment'],
    weakness: 'Fire / Light',
    lore: 'The warrior queen who rose from the streets of East Los to command the obsidian throne. Her blade drinks shadows and her crown channels the spirits of fallen warriors.',
    rtp: '95.1%',
    theme: 'Aztec / Urban Warrior',
  },
];

const GAME_BACKGROUNDS = [
  {
    id: 'BG_AZTEC_LA',
    name: 'Aztec Ruins x East LA',
    image: 'https://customer-assets.emergentagent.com/job_3653cf8a-8710-488d-846f-2f0428b714dd/artifacts/l1atothu_background1.png.png',
    type: 'Parallax Background',
    resolution: '1024x1024',
    theme: 'Mesoamerican / Urban',
  },
];

const ENGINE_PRESETS = [
  { id: 'AAA_FISH_SLOT', name: 'Fish Shooting (Luxury)', desc: 'Casino-grade 3D render, luxury obsidian' },
  { id: 'GTA5_TYPE', name: 'Open World (GTA Style)', desc: 'Cinematic urban grit, hyper-realistic' },
  { id: 'COD_WARFARE', name: 'Tactical FPS (COD Style)', desc: 'Tactical military realism, matte black' },
  { id: 'FANTASY_RPG', name: 'Fantasy RPG', desc: 'Magical, mythical creatures, aztec stone' }
];

const UNIVERSAL_GAME_TYPES = [
  // Arcade & Action
  { id: "arcade_classic", label: "Arcade Classic", seats: 40, cat: "arcade" },
  { id: "fish_shooting", label: "Fish Shooting", seats: 60, cat: "arcade" },
  { id: "battle_royale", label: "Battle Royale", seats: 100, cat: "arcade" },
  { id: "tactical_fps", label: "Tactical FPS", seats: 80, cat: "arcade" },
  { id: "cod_warfare", label: "COD Warfare", seats: 80, cat: "arcade" },
  { id: "platformer", label: "Platformer", seats: 20, cat: "arcade" },
  { id: "fighting", label: "Fighting (2D/3D)", seats: 40, cat: "arcade" },
  { id: "puzzle", label: "Puzzle", seats: 20, cat: "arcade" },
  { id: "adventure", label: "Adventure", seats: 40, cat: "arcade" },
  { id: "open_world", label: "Open World (GTA)", seats: 100, cat: "arcade" },
  // Casino & Gambling
  { id: "slot_machine", label: "Slot Machine", seats: 20, cat: "casino" },
  { id: "video_poker", label: "Video Poker", seats: 20, cat: "casino" },
  { id: "casino_suite", label: "Casino Suite", seats: 100, cat: "casino" },
  { id: "pachinko", label: "Pachinko", seats: 30, cat: "casino" },
  { id: "lottery", label: "Lottery", seats: 20, cat: "casino" },
  { id: "bingo", label: "Bingo", seats: 40, cat: "casino" },
  { id: "sportsbook", label: "Sportsbook", seats: 60, cat: "casino" },
  { id: "card_games", label: "Card Games", seats: 30, cat: "casino" },
  // RPG & Narrative
  { id: "open_world_rpg", label: "Open World RPG", seats: 100, cat: "rpg" },
  { id: "dungeon_crawler", label: "Dungeon Crawler", seats: 40, cat: "rpg" },
  { id: "fantasy_rpg", label: "Fantasy RPG", seats: 60, cat: "rpg" },
  { id: "cyberpunk", label: "Cyberpunk", seats: 80, cat: "rpg" },
  { id: "horror", label: "Horror", seats: 40, cat: "rpg" },
  { id: "southern_barrio", label: "Southern Barrio", seats: 40, cat: "rpg" },
  { id: "sandbox", label: "Sandbox", seats: 60, cat: "rpg" },
  // Racing & Simulation
  { id: "racing_sim", label: "Racing Sim", seats: 60, cat: "racing" },
  // Hybrid & Custom
  { id: "hybrid_mix", label: "Hybrid Mix", seats: 40, cat: "hybrid" },
  { id: "generic_game_asset", label: "Generic Game Asset", seats: 20, cat: "hybrid" },
  { id: "custom_partner", label: "Custom Partner Games", seats: 60, cat: "hybrid" },
];

const CATEGORY_META = {
  arcade: { label: 'ARCADE & ACTION', color: 'text-cyan-400' },
  casino: { label: 'CASINO & GAMBLING', color: 'text-amber-400' },
  rpg: { label: 'RPG & NARRATIVE', color: 'text-indigo-400' },
  racing: { label: 'RACING & SIMULATION', color: 'text-emerald-400' },
  hybrid: { label: 'HYBRID & CUSTOM', color: 'text-zinc-400' },
};

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
  const [osPartitions, setOsPartitions] = useState([{ id: 1, type: 'fish_shooting', units: 1 }]);
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
  const [visionAssetType, setVisionAssetType] = useState('concept_art');
  const [visionStyle, setVisionStyle] = useState('pixel_art');
  const [visionSize, setVisionSize] = useState('1024x1024');

  // Bestiary
  const [selectedBoss, setSelectedBoss] = useState(BOSS_BESTIARY[0]);

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

  // Audio Forge State (managed by AudioForgePanel)
  const [audioAssets, setAudioAssets] = useState([]);

  // Admin Vault — Nexus + Matrix
  const [nexusPipelines, setNexusPipelines] = useState([]);
  const [matrixParams, setMatrixParams] = useState(null);
  const [osModules, setOsModules] = useState([]);

  // Build Pipeline State
  const [builds, setBuilds] = useState([]);
  const [buildTarget, setBuildTarget] = useState('webgl');
  const [buildOptimization, setBuildOptimization] = useState('balanced');
  const [compilingBuild, setCompilingBuild] = useState(null);

  // Compliance State
  const [complianceReports, setComplianceReports] = useState([]);
  const [complianceJurisdiction, setComplianceJurisdiction] = useState('GLI');

  // Deploy State
  const [deployments, setDeployments] = useState([]);
  const [deployCdn, setDeployCdn] = useState('cloudflare');
  const [deployRegion, setDeployRegion] = useState('us-west');

  // Universe Registry
  const [universes, setUniverses] = useState([]);

  // Auto-Certify State
  const [autoCertifying, setAutoCertifying] = useState(false);
  const [certifySteps, setCertifySteps] = useState([]);

  // Universe Expand State
  const [expandedUniverse, setExpandedUniverse] = useState(null);
  const [universeStatus, setUniverseStatus] = useState(null);

  // Worker State
  const [workerStatus, setWorkerStatus] = useState({ running: false, active_jobs: 0, blocked_jobs: 0, completed_jobs: 0, total_jobs: 0 });
  const [newJobPreset, setNewJobPreset] = useState('FISH_SHOOTING');
  const [newJobPriority, setNewJobPriority] = useState('normal');
  const [newJobDeps, setNewJobDeps] = useState([]);
  const [depGraph, setDepGraph] = useState({ nodes: [], edges: [] });
  const [nightQueueView, setNightQueueView] = useState('list'); // 'list' | 'graph'

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
      const [typesRes, projRes, statsRes, tenantsRes, jobsRes, pipelinesRes, buildsRes, compRes, deployRes, universesRes, audioRes, nexusRes, matrixRes, osModRes] = await Promise.all([
        axios.get(`${API}/game-types`),
        axios.get(`${API}/projects`),
        axios.get(`${API}/stats`),
        axios.get(`${API}/tenants`).catch(() => ({ data: { tenants: [] } })),
        axios.get(`${API}/jobs`).catch(() => ({ data: { jobs: [] } })),
        axios.get(`${API}/pipelines`).catch(() => ({ data: { pipelines: [] } })),
        axios.get(`${API}/builds`).catch(() => ({ data: { builds: [] } })),
        axios.get(`${API}/compliance`).catch(() => ({ data: { reports: [] } })),
        axios.get(`${API}/deployments`).catch(() => ({ data: { deployments: [] } })),
        axios.get(`${API}/universes`).catch(() => ({ data: { universes: [] } })),
        axios.get(`${API}/audio/assets`).catch(() => ({ data: { assets: [] } })),
        axios.get(`${API}/nexus/pipelines`).catch(() => ({ data: { pipelines: [] } })),
        axios.get(`${API}/nexus/matrix`).catch(() => ({ data: null })),
        axios.get(`${API}/nexus/os-modules`).catch(() => ({ data: { modules: [] } })),
      ]);
      setGameTypes(typesRes.data.game_types || {});
      setProjects(projRes.data.projects || []);
      setStats(statsRes.data || {});
      setAgents(tenantsRes.data.tenants || []);
      setQueue(jobsRes.data.jobs || []);
      setPipelines(pipelinesRes.data.pipelines || []);
      setBuilds(buildsRes.data.builds || []);
      setComplianceReports(compRes.data.reports || []);
      setDeployments(deployRes.data.deployments || []);
      setUniverses(universesRes.data.universes || []);
      setAudioAssets(audioRes.data.assets || []);
      setNexusPipelines(nexusRes.data.pipelines || []);
      setMatrixParams(matrixRes.data);
      setOsModules(osModRes.data.modules || []);
    } catch (e) {
      console.error("SLA113 data fetch failed:", e);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  // Auto-poll when viewing Night Queue (worker is processing jobs)
  useEffect(() => {
    if (activeTab !== 'NIGHT QUEUE') return;
    const fetchWorker = async () => {
      try {
        const [wRes, gRes] = await Promise.all([
          axios.get(`${API}/worker/status`),
          axios.get(`${API}/jobs/graph`),
        ]);
        setWorkerStatus(wRes.data);
        setDepGraph(gRes.data);
      } catch {}
    };
    fetchWorker();
    const interval = setInterval(() => { fetchData(); fetchWorker(); }, 3000);
    return () => clearInterval(interval);
  }, [activeTab, fetchData]);

  const handlePartitionChange = (p) => {
    setPartition(p);
    const defaultTab = ALL_NAV_ITEMS.find(item => item.partition === p)?.id || '';
    setActiveTab(defaultTab);
  };

  const handleForgeOS = async () => {
    setIsBuilding(true);
    try {
      const gameType = osPartitions[0]?.type || 'fish_shooting';
      const gt = UNIVERSAL_GAME_TYPES.find(g => g.id === gameType);
      await axios.post(`${API}/projects`, { name: `OS_BUILD_${Date.now()}`, game_type: gameType, theme: 'sovereign', target_platform: 'both' });
      await axios.post(`${API}/jobs`, { preset: gameType.toUpperCase(), priority: 'high' });
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
      // Generate AAA-quality game art via GPT Image 1
      const imgRes = await axios.post(`${API}/vision/generate-image`, {
        prompt,
        asset_type: visionAssetType,
        style: visionStyle,
        size: visionSize,
        quality: 'high',
      });
      if (imgRes.data.image_base64) {
        setGeneratedImages(prev => [{
          base64: imgRes.data.image_base64,
          prompt: imgRes.data.prompt,
          style: imgRes.data.style,
          asset_type: imgRes.data.asset_type,
          id: Date.now()
        }, ...prev]);
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

            {/* FACTORY: FRONTLINE — REAL-TIME WEBSOCKET */}
            {partition === 'factory' && activeTab === 'FRONTLINE' && (
              <FrontlinePanel API={API} projects={projects} stats={stats} />
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

            {/* FACTORY: DEPLOY CENTER */}
            {partition === 'factory' && activeTab === 'DEPLOY CENTER' && (
              <div className="grid grid-cols-12 gap-6 animate-in fade-in max-w-7xl mx-auto w-full" data-testid="deploy-center-panel">
                <div className="col-span-5 space-y-6">
                  <div className="glass-panel border-cyan-500/20 p-8 space-y-6">
                    <h3 className="text-cyan-400 text-xs font-black uppercase tracking-[4px] border-b border-cyan-500/20 pb-4 flex items-center gap-3"><Upload size={16}/> CDN Deploy</h3>
                    <div className="space-y-4">
                      <div>
                        <label className="text-[9px] text-zinc-500 uppercase tracking-widest block mb-2">Source Build</label>
                        <select className="input-dark focus:border-cyan-500 uppercase tracking-widest" data-testid="deploy-build-select" id="deploy-build-select">
                          {builds.filter(b => b.status === 'completed').map(b => <option key={b.id} value={b.id}>{b.id} — {b.project_name} ({b.target})</option>)}
                          {builds.filter(b => b.status === 'completed').length === 0 && <option>No completed builds</option>}
                        </select>
                      </div>
                      <div>
                        <label className="text-[9px] text-zinc-500 uppercase tracking-widest block mb-2">CDN Provider</label>
                        <div className="grid grid-cols-2 gap-2">
                          {[{id:'cloudflare',label:'Cloudflare'},{id:'aws',label:'AWS'},{id:'gcp',label:'GCP'},{id:'custom',label:'Custom'}].map(c => (
                            <button key={c.id} onClick={() => setDeployCdn(c.id)} className={`py-2 text-[9px] uppercase tracking-widest border transition-all ${deployCdn === c.id ? 'border-cyan-500 bg-cyan-500/10 text-cyan-400' : 'border-zinc-800 text-zinc-600 hover:text-zinc-300'}`} data-testid={`cdn-${c.id}`}>
                              {c.label}
                            </button>
                          ))}
                        </div>
                      </div>
                      <div>
                        <label className="text-[9px] text-zinc-500 uppercase tracking-widest block mb-2">Region</label>
                        <div className="grid grid-cols-3 gap-2">
                          {['us-west','us-east','eu-west','asia-east','global'].map(r => (
                            <button key={r} onClick={() => setDeployRegion(r)} className={`py-1.5 text-[8px] uppercase tracking-widest border transition-all ${deployRegion === r ? 'border-cyan-500 bg-cyan-500/10 text-cyan-400' : 'border-zinc-800 text-zinc-600 hover:text-zinc-300'}`}>
                              {r}
                            </button>
                          ))}
                        </div>
                      </div>
                    </div>
                    <button
                      onClick={async () => {
                        const sel = document.getElementById('deploy-build-select');
                        const bid = sel?.value;
                        const completedBuilds = builds.filter(b => b.status === 'completed');
                        if (!bid || completedBuilds.length === 0) return;
                        await axios.post(`${API}/deploy`, { build_id: bid, target_cdn: deployCdn, region: deployRegion });
                        fetchData();
                      }}
                      disabled={builds.filter(b => b.status === 'completed').length === 0}
                      className="w-full py-4 font-bold tracking-[3px] uppercase text-[10px] border border-cyan-500 text-black bg-cyan-500 hover:bg-cyan-300 transition-all disabled:opacity-30"
                      data-testid="deploy-btn"
                    >
                      Deploy to CDN
                    </button>
                  </div>
                </div>
                <div className="col-span-7 space-y-4">
                  <span className="text-cyan-400 text-[10px] font-bold uppercase tracking-[3px]">Live Deployments ({deployments.length})</span>
                  <div className="space-y-3 max-h-[500px] overflow-y-auto custom-scrollbar">
                    {deployments.length === 0 && <div className="glass-panel border-cyan-500/10 p-12 text-center text-zinc-600 text-[10px] uppercase tracking-widest">No deployments. Build a project first, then deploy.</div>}
                    {deployments.map(d => (
                      <div key={d.id} className="glass-panel border-cyan-500/20 p-5 space-y-3">
                        <div className="flex justify-between items-start">
                          <div>
                            <span className="text-zinc-200 text-xs font-bold">{d.id}</span>
                            <span className="text-zinc-500 text-[9px] ml-3">{d.project_name} / {d.target_cdn.toUpperCase()} / {d.region}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className={`px-2 py-0.5 text-[8px] uppercase tracking-widest border font-bold ${
                              d.status === 'live' ? 'border-emerald-500/30 text-emerald-500 bg-emerald-500/10' :
                              d.status === 'propagating' ? 'border-cyan-500/30 text-cyan-400 bg-cyan-500/10' :
                              'border-zinc-700 text-zinc-400'
                            }`}>{d.status}</span>
                            {d.status !== 'live' && (
                              <button onClick={async () => { await axios.post(`${API}/deploy/${d.id}/advance`); fetchData(); }} className="text-[9px] border border-cyan-500/30 bg-cyan-500/10 text-cyan-400 px-2 py-1 hover:bg-cyan-500 hover:text-black transition-all" data-testid={`advance-deploy-${d.id}`}>
                                Propagate
                              </button>
                            )}
                            <button onClick={async () => { await axios.delete(`${API}/deploy/${d.id}`); fetchData(); }} className="text-zinc-600 hover:text-red-500 transition-colors"><XCircle size={14}/></button>
                          </div>
                        </div>
                        <div className="flex items-center gap-3">
                          <div className="flex-1 h-1.5 bg-black border border-zinc-900 overflow-hidden">
                            <div className={`h-full transition-all ${d.status === 'live' ? 'bg-emerald-500' : 'bg-cyan-500'}`} style={{width: `${d.progress}%`}}/>
                          </div>
                          <span className="text-[10px] font-mono text-zinc-500">{d.progress}%</span>
                        </div>
                        {d.url && (
                          <a href={`${process.env.REACT_APP_BACKEND_URL}${d.url}`} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 bg-emerald-500/5 border border-emerald-500/20 p-3 text-emerald-400 text-[10px] font-mono hover:bg-emerald-500/10 transition-all" data-testid={`deploy-url-${d.id}`}>
                            <Play size={12}/> Play Live Game
                            <span className="text-zinc-500 mx-2">{d.url}</span>
                            <span className={`ml-auto text-[8px] uppercase tracking-widest ${d.ssl_status === 'active' ? 'text-emerald-500' : 'text-zinc-600'}`}>SSL: {d.ssl_status}</span>
                          </a>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}


            {/* FACTORY: UNIVERSE REGISTRY */}
            {partition === 'factory' && activeTab === 'UNIVERSES' && (
              <div className="animate-in fade-in max-w-7xl mx-auto w-full space-y-6" data-testid="universe-registry-panel">
                <div className="flex items-center justify-between">
                  <span className="text-cyan-400 text-[10px] font-bold uppercase tracking-[3px] flex items-center gap-2"><Globe size={14}/> Sovereign Universe Registry ({universes.length})</span>
                  <span className="text-[8px] text-zinc-600 uppercase tracking-widest">Auto-Discovery Active</span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {universes.map(u => {
                    const engineColors = {
                      'fastapi+mongodb': { border: 'border-cyan-500/40', bg: 'bg-cyan-500/5', text: 'text-cyan-400', dot: 'bg-cyan-500', glow: 'shadow-[0_0_20px_rgba(0,200,255,0.08)]' },
                      'emergent-llm': { border: 'border-indigo-500/40', bg: 'bg-indigo-500/5', text: 'text-indigo-400', dot: 'bg-indigo-500', glow: 'shadow-[0_0_20px_rgba(99,102,241,0.08)]' },
                      'vertex-ai': { border: 'border-amber-500/40', bg: 'bg-amber-500/5', text: 'text-amber-400', dot: 'bg-amber-500', glow: 'shadow-[0_0_20px_rgba(245,158,11,0.08)]' },
                      'internal': { border: 'border-zinc-600/40', bg: 'bg-zinc-800/30', text: 'text-zinc-400', dot: 'bg-zinc-500', glow: '' },
                      'cocos2d': { border: 'border-emerald-500/40', bg: 'bg-emerald-500/5', text: 'text-emerald-400', dot: 'bg-emerald-500', glow: 'shadow-[0_0_20px_rgba(16,185,129,0.08)]' },
                    };
                    const ec = engineColors[u.engine] || engineColors['internal'];
                    const isExpanded = expandedUniverse === u.id;
                    return (
                      <div key={u.id} className={`glass-panel ${ec.border} ${ec.bg} ${ec.glow} transition-all duration-300 ${isExpanded ? 'ring-1 ring-white/10' : 'hover:scale-[1.01]'}`} data-testid={`universe-${u.id}`}>
                        {/* Clickable Header */}
                        <button
                          onClick={async () => {
                            if (isExpanded) { setExpandedUniverse(null); setUniverseStatus(null); return; }
                            setExpandedUniverse(u.id);
                            try {
                              const res = await axios.get(`${process.env.REACT_APP_BACKEND_URL}${u.prefix}/status`);
                              setUniverseStatus(res.data);
                            } catch { setUniverseStatus({ error: 'Endpoint not reachable' }); }
                          }}
                          className="w-full p-6 text-left space-y-3"
                          data-testid={`universe-toggle-${u.id}`}
                        >
                          <div className="flex justify-between items-start">
                            <div className="space-y-1">
                              <div className="flex items-center gap-2">
                                <span className={`w-2.5 h-2.5 rounded-full ${ec.dot} ${u.status === 'online' ? 'animate-pulse' : ''}`}></span>
                                <span className="text-zinc-100 text-sm font-bold tracking-wider uppercase">{u.name}</span>
                                <ChevronDown size={12} className={`text-zinc-600 transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
                              </div>
                              <p className="text-zinc-500 text-[9px] uppercase tracking-widest leading-relaxed">{u.description}</p>
                            </div>
                            <span className={`px-2 py-0.5 text-[7px] uppercase tracking-widest border font-bold ${
                              u.status === 'online' ? 'border-emerald-500/30 text-emerald-500 bg-emerald-500/10' : 'border-red-500/30 text-red-500 bg-red-500/10'
                            }`}>{u.status}</span>
                          </div>
                          {u.product && (
                            <div className="bg-black/50 border border-zinc-800 p-3">
                              <span className="text-[8px] text-zinc-600 uppercase tracking-widest block mb-1">Product</span>
                              <span className={`text-xs font-bold ${ec.text}`}>{u.product}</span>
                            </div>
                          )}
                          <div className="flex gap-3">
                            <div className="flex-1 bg-black/50 border border-zinc-800 p-3">
                              <span className="text-[8px] text-zinc-600 uppercase tracking-widest block mb-1">Prefix</span>
                              <code className="text-zinc-300 text-[10px] font-mono">{u.prefix}</code>
                            </div>
                            <div className="flex-1 bg-black/50 border border-zinc-800 p-3">
                              <span className="text-[8px] text-zinc-600 uppercase tracking-widest block mb-1">Engine</span>
                              <span className={`text-[10px] font-bold uppercase tracking-wider ${ec.text}`}>{u.engine}</span>
                            </div>
                          </div>
                        </button>

                        {/* Expanded Status Panel */}
                        {isExpanded && (
                          <div className="px-6 pb-6 space-y-4 border-t border-zinc-800 pt-4 animate-in slide-in-from-top-2">
                            {/* Live Status */}
                            <div>
                              <span className="text-[8px] text-zinc-600 uppercase tracking-widest block mb-2">Live API Response</span>
                              <pre className="bg-black/80 border border-zinc-800 p-4 text-[10px] font-mono text-zinc-400 overflow-x-auto max-h-40 overflow-y-auto" data-testid={`universe-status-${u.id}`}>
                                {universeStatus ? JSON.stringify(universeStatus, null, 2) : 'Loading...'}
                              </pre>
                            </div>

                            {/* Action Buttons */}
                            <div className="flex gap-2">
                              <a
                                href={`${process.env.REACT_APP_BACKEND_URL}${u.prefix}/status`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className={`flex-1 py-3 text-center text-[9px] uppercase tracking-widest font-bold border ${ec.border} ${ec.text} hover:bg-white/5 transition-all`}
                                data-testid={`universe-api-${u.id}`}
                              >
                                Open API
                              </a>
                              {u.id === 'empire1' && (
                                <a
                                  href="/"
                                  className="flex-1 py-3 text-center text-[9px] uppercase tracking-widest font-bold border border-indigo-500/40 text-indigo-400 hover:bg-indigo-500/10 transition-all"
                                  data-testid="launch-empire1"
                                >
                                  Launch Empire 1
                                </a>
                              )}
                              {u.id === 'sla113' && (
                                <button
                                  onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
                                  className="flex-1 py-3 text-[9px] uppercase tracking-widest font-bold border border-cyan-500/40 text-cyan-400 hover:bg-cyan-500/10 transition-all"
                                >
                                  You Are Here
                                </button>
                              )}
                              {u.id !== 'sla113' && (
                                <button
                                  onClick={async () => { await axios.delete(`${API}/universes/${u.id}`); setExpandedUniverse(null); fetchData(); }}
                                  className="px-4 py-3 text-[9px] uppercase tracking-widest font-bold border border-red-500/30 text-red-500 hover:bg-red-500/10 transition-all"
                                  data-testid={`deregister-${u.id}`}
                                >
                                  Deregister
                                </button>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
                {universes.length === 0 && (
                  <div className="glass-panel border-cyan-500/10 p-16 text-center">
                    <Globe size={32} className="text-zinc-700 mx-auto mb-4"/>
                    <p className="text-zinc-600 text-[10px] uppercase tracking-widest">No universes registered. They auto-register on server boot.</p>
                  </div>
                )}
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
              <div className="animate-in fade-in max-w-7xl mx-auto w-full space-y-6" data-testid="revenue-pipelines-panel">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <span className="text-indigo-400 text-[10px] font-bold uppercase tracking-[3px]">{pipelines.length} Pipelines</span>
                    <span className="text-zinc-500 text-[10px]">Total Revenue: <span className="text-indigo-400 font-bold">${pipelines.reduce((s,p) => s + (p.revenue||0), 0).toLocaleString()}</span></span>
                  </div>
                  <button
                    onClick={async () => { for (const p of pipelines) { await axios.put(`${API}/pipelines/${p.id}/pulse`).catch(() => {}); } fetchData(); }}
                    className="px-4 py-2 border border-indigo-500/30 bg-indigo-500/10 text-indigo-400 text-[9px] uppercase tracking-widest font-bold hover:bg-indigo-500 hover:text-black transition-all flex items-center gap-2"
                    data-testid="pulse-all-pipelines"
                  >
                    <CloudLightning size={12} /> Pulse All
                  </button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                  {pipelines.map(p => {
                    const isActive = pipelineHeartbeats[p.id] === 'active';
                    return (
                      <div key={p.id} className={`p-5 border transition-all relative overflow-hidden group ${isActive ? 'bg-indigo-900/20 border-indigo-500/50 shadow-[0_0_15px_rgba(99,102,241,0.1)]' : 'bg-black/50 border-zinc-900/80 hover:border-zinc-700'}`}>
                        <div className="flex justify-between items-start mb-4 text-indigo-400">
                          {p.lane === 1 ? <Cpu size={16}/> : p.lane === 2 ? <Package size={16}/> : <ShieldCheck size={16}/>}
                          <span className={`w-2 h-2 rounded-full ${isActive ? 'bg-indigo-400 animate-ping' : 'bg-zinc-800'}`}></span>
                        </div>
                        <h4 className="text-xs font-bold text-zinc-200 mb-1">{p.name}</h4>
                        <p className="text-[9px] text-zinc-500 uppercase tracking-widest font-mono">Lane 0{p.lane} // {p.type}</p>
                        <div className="mt-3 flex justify-between items-center text-[9px]">
                          <span className="text-zinc-500">{p.executions || 0} runs</span>
                          <span className="text-indigo-400 font-bold">${(p.revenue || 0).toLocaleString()}</span>
                        </div>
                        <button
                          onClick={async () => { await axios.put(`${API}/pipelines/${p.id}/pulse`); fetchData(); }}
                          className="mt-3 w-full py-2 border border-indigo-500/20 bg-indigo-500/5 text-indigo-400 text-[9px] uppercase tracking-widest font-bold opacity-0 group-hover:opacity-100 hover:bg-indigo-500 hover:text-black transition-all flex items-center justify-center gap-2"
                          data-testid={`pulse-pipeline-${p.id}`}
                        >
                          <Zap size={10} /> Pulse
                        </button>
                      </div>
                    );
                  })}
                  {pipelines.length === 0 && <div className="col-span-4 text-center text-zinc-500 text-[10px] uppercase tracking-widest py-12">No pipelines configured</div>}
                </div>
              </div>
            )}

            {/* EMPIRE: BESTIARY */}
            {partition === 'empire' && activeTab === 'BESTIARY' && (
              <div className="animate-in fade-in max-w-7xl mx-auto w-full" data-testid="bestiary-panel">
                <div className="grid grid-cols-12 gap-6">
                  {/* Boss Roster */}
                  <div className="col-span-3 space-y-3">
                    <h3 className="text-indigo-400 text-[10px] font-bold uppercase tracking-[3px] border-b border-indigo-500/20 pb-3 flex items-center gap-2">
                      <Skull size={14} /> Boss Roster ({BOSS_BESTIARY.length})
                    </h3>
                    {BOSS_BESTIARY.map(boss => (
                      <button
                        key={boss.id}
                        onClick={() => setSelectedBoss(boss)}
                        className={`w-full text-left border transition-all overflow-hidden group ${
                          selectedBoss?.id === boss.id
                            ? 'border-indigo-500/60 bg-indigo-500/10 shadow-[0_0_15px_rgba(99,102,241,0.15)]'
                            : 'border-zinc-800 bg-black/50 hover:border-zinc-700'
                        }`}
                        data-testid={`boss-select-${boss.id}`}
                      >
                        <div className="flex items-center gap-3 p-3">
                          <img src={boss.image} alt={boss.name} className="w-14 h-14 object-cover border border-zinc-800 shrink-0" />
                          <div className="min-w-0">
                            <div className="text-xs font-bold text-zinc-200 truncate">{boss.name}</div>
                            <div className="text-[8px] text-zinc-500 uppercase tracking-widest">{boss.tier}</div>
                            <div className="text-[8px] text-indigo-400 font-mono mt-0.5">HP: {(boss.hp / 1000).toFixed(0)}K</div>
                          </div>
                        </div>
                      </button>
                    ))}
                    <div className="border border-dashed border-zinc-800 p-4 text-center text-zinc-700 text-[9px] uppercase tracking-widest hover:border-[#D4AF37]/30 hover:text-[#D4AF37]/50 transition-all cursor-pointer">
                      <Plus size={14} className="inline mr-2" /> Add Boss via Vision Smith
                    </div>
                  </div>

                  {/* Boss Detail */}
                  {selectedBoss && (
                    <div className="col-span-9 space-y-4">
                      {/* Hero Image */}
                      <div className="relative overflow-hidden border border-indigo-500/20 bg-black group">
                        <img
                          src={selectedBoss.image}
                          alt={selectedBoss.name}
                          className="w-full h-[300px] object-cover object-center"
                          style={{ filter: 'contrast(1.05) brightness(0.95)' }}
                          data-testid="boss-hero-image"
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-black via-black/50 to-transparent" />
                        <div className="absolute inset-0 bg-gradient-to-r from-black/80 to-transparent" />

                        {/* Boss Info Overlay */}
                        <div className="absolute bottom-0 left-0 right-0 p-6 space-y-2">
                          <div className="flex items-end justify-between">
                            <div>
                              <span className={`px-3 py-1 text-[8px] uppercase tracking-[3px] font-bold border ${
                                selectedBoss.tier === 'MYTHIC' ? 'border-amber-500/50 bg-amber-500/10 text-amber-400' : 'border-purple-500/50 bg-purple-500/10 text-purple-400'
                              }`}>{selectedBoss.tier}</span>
                              <h2 className="text-2xl font-black text-white tracking-widest uppercase mt-3">{selectedBoss.name}</h2>
                              <p className="text-[10px] text-indigo-400 tracking-[4px] uppercase">{selectedBoss.title}</p>
                            </div>
                            <div className="text-right space-y-1">
                              <div className="text-[9px] text-zinc-500 uppercase tracking-widest">Credit Values</div>
                              <div className="flex gap-3">
                                <span className="text-[#D4AF37] font-bold text-lg">{selectedBoss.credits.left}</span>
                                <span className="text-zinc-600">/</span>
                                <span className="text-indigo-400 font-bold text-lg">{selectedBoss.credits.right}</span>
                              </div>
                            </div>
                          </div>

                          {/* HP Bar */}
                          <div className="mt-2">
                            <div className="flex justify-between text-[8px] mb-1">
                              <span className="text-red-400 uppercase tracking-widest flex items-center gap-1"><Heart size={8} /> {selectedBoss.hp.toLocaleString()} HP</span>
                              <span className="text-zinc-600">RTP: {selectedBoss.rtp}</span>
                            </div>
                            <div className="h-2 bg-black/80 border border-red-500/20 overflow-hidden">
                              <div className="h-full bg-gradient-to-r from-red-700 via-red-500 to-red-400 w-full" />
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Stats Grid */}
                      <div className="grid grid-cols-3 gap-3">
                        {/* Attacks */}
                        <div className="border border-zinc-800 bg-black/50 p-4 space-y-2">
                          <h4 className="text-red-400 text-[9px] font-bold uppercase tracking-[3px] flex items-center gap-2"><Swords size={12} /> Attack Kit</h4>
                          <div className="space-y-1.5">
                            {selectedBoss.attacks.map((atk, i) => (
                              <div key={i} className="flex items-center gap-2 text-[10px]">
                                <span className="w-4 h-4 border border-red-500/30 bg-red-500/10 flex items-center justify-center text-red-400 text-[7px] font-bold shrink-0">{i + 1}</span>
                                <span className="text-zinc-300">{atk}</span>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Weakness & Theme */}
                        <div className="border border-zinc-800 bg-black/50 p-4 space-y-3">
                          <div>
                            <h4 className="text-cyan-400 text-[9px] font-bold uppercase tracking-[3px] mb-1">Weakness</h4>
                            <span className="text-cyan-300 text-sm font-bold">{selectedBoss.weakness}</span>
                          </div>
                          <div>
                            <h4 className="text-[#D4AF37] text-[9px] font-bold uppercase tracking-[3px] mb-1">Art Theme</h4>
                            <span className="text-[#D4AF37] text-sm font-bold">{selectedBoss.theme}</span>
                          </div>
                          <div>
                            <h4 className="text-indigo-400 text-[9px] font-bold uppercase tracking-[3px] mb-1">Boss ID</h4>
                            <span className="text-indigo-300 text-[10px] font-mono">{selectedBoss.id}</span>
                          </div>
                        </div>

                        {/* Lore */}
                        <div className="border border-zinc-800 bg-black/50 p-4 space-y-2">
                          <h4 className="text-amber-400 text-[9px] font-bold uppercase tracking-[3px]">Lore</h4>
                          <p className="text-zinc-400 text-[10px] leading-relaxed">{selectedBoss.lore}</p>
                        </div>
                      </div>

                      {/* Sprite Sheet */}
                      {selectedBoss.spriteSheet && (
                        <div className="border border-indigo-500/20 bg-black/50 p-4 space-y-3">
                          <div className="flex items-center justify-between">
                            <h4 className="text-indigo-400 text-[9px] font-bold uppercase tracking-[3px] flex items-center gap-2"><Grid3X3 size={12} /> Sprite Sheet</h4>
                            <span className="text-[8px] text-zinc-600 uppercase tracking-widest">2x2 Grid — 4 Poses</span>
                          </div>
                          <img
                            src={selectedBoss.spriteSheet}
                            alt={`${selectedBoss.name} sprites`}
                            className="w-full max-h-[200px] object-contain border border-zinc-800"
                            style={{ imageRendering: 'auto', background: 'repeating-conic-gradient(#111 0% 25%, #0a0a0a 0% 50%) 0 0 / 16px 16px' }}
                            data-testid="boss-sprite-sheet"
                          />
                        </div>
                      )}

                      {/* Game Backgrounds */}
                      {GAME_BACKGROUNDS.length > 0 && (
                        <div className="border border-[#D4AF37]/20 bg-black/50 p-4 space-y-3">
                          <h4 className="text-[#D4AF37] text-[9px] font-bold uppercase tracking-[3px] flex items-center gap-2"><ImageIcon size={12} /> Game Backgrounds ({GAME_BACKGROUNDS.length})</h4>
                          <div className="grid grid-cols-2 gap-3">
                            {GAME_BACKGROUNDS.map(bg => (
                              <div key={bg.id} className="relative group overflow-hidden border border-zinc-800 hover:border-[#D4AF37]/30 transition-all">
                                <img src={bg.image} alt={bg.name} className="w-full h-32 object-cover" />
                                <div className="absolute bottom-0 left-0 right-0 p-2 bg-gradient-to-t from-black to-transparent">
                                  <div className="text-[9px] text-zinc-200 font-bold">{bg.name}</div>
                                  <div className="text-[8px] text-zinc-500">{bg.type} / {bg.resolution}</div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
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
                        <button onClick={() => setOsPartitions([...osPartitions, { id: Date.now(), type: 'slot_machine', units: 1 }])} className="text-[#D4AF37] flex items-center gap-1 hover:text-white transition-all bg-[#D4AF37]/10 px-3 py-1 border border-[#D4AF37]/30" data-testid="add-cluster-btn">
                          <Plus size={12} /> Add Cluster
                        </button>
                      </div>
                      <div className="space-y-3 max-h-[200px] overflow-y-auto pr-2 custom-scrollbar">
                        {osPartitions.map((part, index) => (
                          <div key={part.id} className="flex gap-3 items-center group">
                            <select value={part.type} onChange={(e) => { const n = [...osPartitions]; n[index].type = e.target.value; setOsPartitions(n); }} className="flex-1 input-dark uppercase tracking-widest focus:border-[#D4AF37] text-zinc-300 text-[9px]">
                              {Object.entries(CATEGORY_META).map(([catId, meta]) => (
                                <optgroup key={catId} label={meta.label}>
                                  {UNIVERSAL_GAME_TYPES.filter(g => g.cat === catId).map(g => (<option key={g.id} value={g.id}>{g.label}</option>))}
                                </optgroup>
                              ))}
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
                    {projects.length > 0 ? projects.map((p, i) => {
                      const gt = UNIVERSAL_GAME_TYPES.find(g => g.id === p.game_type);
                      const catColor = gt ? (CATEGORY_META[gt.cat]?.color || 'text-zinc-400') : 'text-zinc-400';
                      return (
                        <div key={i} className="flex justify-between items-center p-3 border border-zinc-900 bg-black/50">
                          <span className="text-zinc-300">{p.name}</span>
                          <span className={catColor}>{gt?.label || p.game_type}</span>
                        </div>
                      );
                    }) : (
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
                <div className="col-span-4 space-y-5 max-h-[calc(100vh-220px)] overflow-y-auto custom-scrollbar">
                  <div className="glass-panel border-[#D4AF37]/20 p-6 space-y-5 shadow-xl">
                    <div className="border-b border-[#D4AF37]/20 pb-3">
                      <h3 className="text-base text-[#D4AF37] font-bold tracking-widest uppercase flex items-center gap-2"><ImageIcon size={16} /> Prompt Architect</h3>
                      <p className="text-[9px] text-zinc-500 mt-1 tracking-widest uppercase">AAA Game Asset Pipeline</p>
                    </div>

                    {/* Asset Type */}
                    <div>
                      <label className="block text-[9px] text-[#D4AF37] mb-2 uppercase tracking-widest font-bold">1. Asset Type</label>
                      <div className="grid grid-cols-2 gap-1.5">
                        {[
                          { id: 'concept_art', label: 'Concept Art' },
                          { id: 'character', label: 'Character' },
                          { id: 'boss', label: 'Boss Design' },
                          { id: 'sprite_sheet', label: 'Sprite Sheet' },
                          { id: 'tileset', label: 'Tileset' },
                          { id: 'background', label: 'Background' },
                          { id: 'ui_element', label: 'UI Kit' },
                          { id: 'vfx', label: 'VFX / Particles' },
                        ].map(t => (
                          <button
                            key={t.id}
                            onClick={() => setVisionAssetType(t.id)}
                            className={`py-2 text-[8px] uppercase tracking-widest border transition-all ${
                              visionAssetType === t.id ? 'border-[#D4AF37] bg-[#D4AF37]/10 text-[#D4AF37]' : 'border-zinc-800 text-zinc-600 hover:text-zinc-300'
                            }`}
                            data-testid={`asset-type-${t.id}`}
                          >
                            {t.label}
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Art Style */}
                    <div>
                      <label className="block text-[9px] text-[#D4AF37] mb-2 uppercase tracking-widest font-bold">2. Art Style</label>
                      <div className="grid grid-cols-2 gap-1.5">
                        {[
                          { id: 'pixel_art', label: 'Pixel Art' },
                          { id: '3d_render', label: '3D Render' },
                          { id: 'hand_drawn', label: 'Hand Painted' },
                          { id: 'anime', label: 'Anime' },
                          { id: 'neon_cyberpunk', label: 'Cyberpunk' },
                          { id: 'dark_fantasy', label: 'Dark Fantasy' },
                          { id: 'military_realism', label: 'Military' },
                          { id: 'comic_book', label: 'Comic Book' },
                          { id: 'vector', label: 'Vector/Flat' },
                          { id: 'low_poly', label: 'Low Poly' },
                        ].map(s => (
                          <button
                            key={s.id}
                            onClick={() => setVisionStyle(s.id)}
                            className={`py-2 text-[8px] uppercase tracking-widest border transition-all ${
                              visionStyle === s.id ? 'border-[#D4AF37] bg-[#D4AF37]/10 text-[#D4AF37]' : 'border-zinc-800 text-zinc-600 hover:text-zinc-300'
                            }`}
                            data-testid={`art-style-${s.id}`}
                          >
                            {s.label}
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Resolution */}
                    <div>
                      <label className="block text-[9px] text-[#D4AF37] mb-2 uppercase tracking-widest font-bold">3. Resolution</label>
                      <div className="grid grid-cols-3 gap-1.5">
                        {[
                          { id: '1024x1024', label: '1024x1024' },
                          { id: '1536x1024', label: '1536x1024' },
                          { id: '1024x1536', label: '1024x1536' },
                        ].map(sz => (
                          <button
                            key={sz.id}
                            onClick={() => setVisionSize(sz.id)}
                            className={`py-2 text-[8px] uppercase tracking-widest border transition-all ${
                              visionSize === sz.id ? 'border-[#D4AF37] bg-[#D4AF37]/10 text-[#D4AF37]' : 'border-zinc-800 text-zinc-600 hover:text-zinc-300'
                            }`}
                          >
                            {sz.label}
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Style Anchor */}
                    <div>
                      <label className="block text-[9px] text-[#D4AF37] mb-2 uppercase tracking-widest font-bold">4. Style Anchor (Optional)</label>
                      <div className={`border-2 border-dashed transition-all p-4 text-center relative group bg-black/50 ${referenceFile ? 'border-emerald-500/50' : 'border-zinc-800 hover:border-[#D4AF37]/50'}`}>
                        <input type="file" className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10" onChange={(e) => setReferenceFile(e.target.files[0])} data-testid="style-anchor-upload" />
                        {referenceFile ? (
                          <div className="flex items-center justify-center gap-2">
                            <span className="text-emerald-400 text-[9px] font-bold uppercase tracking-widest">Locked:</span>
                            <span className="text-zinc-500 text-[9px] truncate max-w-[120px]">{referenceFile.name}</span>
                          </div>
                        ) : (
                          <div className="text-zinc-600 flex items-center justify-center gap-2">
                            <Scan size={14} />
                            <span className="text-[9px] uppercase tracking-widest">Upload Reference Art</span>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Engine Preset */}
                    <div>
                      <label className="block text-[9px] text-[#D4AF37] mb-2 uppercase tracking-widest font-bold">5. Game Engine</label>
                      <select value={selectedPreset} onChange={(e) => setSelectedPreset(e.target.value)} className="input-dark uppercase tracking-widest text-[10px] focus:border-[#D4AF37]" data-testid="engine-preset-select">
                        {ENGINE_PRESETS.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
                      </select>
                    </div>

                    {/* Directive */}
                    <div>
                      <label className="block text-[9px] text-[#D4AF37] mb-2 uppercase tracking-widest font-bold">6. Directive</label>
                      <textarea rows={3} value={prompt} onChange={(e) => setPrompt(e.target.value)} placeholder="Describe what you want to create..." className="input-dark resize-none focus:border-[#D4AF37] text-sm" data-testid="vision-directive-input" />
                    </div>

                    {/* Generate */}
                    <button onClick={handleVisionSmith} disabled={visionLoading || !prompt} className={`w-full py-4 font-bold tracking-[0.3em] uppercase transition-all text-xs border ${visionLoading || !prompt ? 'border-zinc-800 text-zinc-700 bg-black' : 'border-[#D4AF37] text-black bg-[#D4AF37] hover:bg-[#F3E5AB]'}`} data-testid="engage-smith-btn">
                      {visionLoading ? 'Forging...' : !prompt ? 'Directive Required' : `Forge ${visionAssetType.replace(/_/g, ' ').toUpperCase()}`}
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
              <AudioForgePanel API={API} audioAssets={audioAssets} setAudioAssets={setAudioAssets} fetchData={fetchData} />
            )}


            {/* VAULT: BUILD PIPELINE */}
            {partition === 'vault' && activeTab === 'BUILD PIPELINE' && (
              <div className="grid grid-cols-12 gap-6 animate-in fade-in max-w-7xl mx-auto w-full" data-testid="build-pipeline-panel">
                <div className="col-span-5 space-y-6">
                  <div className="glass-panel border-red-500/20 p-8 space-y-6 tech-border-red">
                    <h3 className="text-red-500 text-xs font-black uppercase tracking-[4px] border-b border-red-500/20 pb-4 flex items-center gap-3"><Rocket size={16}/> Compile Engine</h3>
                    <div className="space-y-4">
                      <div>
                        <label className="text-[9px] text-zinc-500 uppercase tracking-widest block mb-2">Source Project</label>
                        <select className="input-dark focus:border-red-500 uppercase tracking-widest" data-testid="build-project-select" id="build-project-select">
                          {projects.map(p => <option key={p.id} value={p.id}>{p.name} ({p.game_type})</option>)}
                          {projects.length === 0 && <option>No projects — create one first</option>}
                        </select>
                      </div>
                      <div>
                        <label className="text-[9px] text-zinc-500 uppercase tracking-widest block mb-2">Target Format</label>
                        <div className="grid grid-cols-3 gap-2">
                          {['webgl', 'apk', 'both'].map(t => (
                            <button key={t} onClick={() => setBuildTarget(t)} className={`py-2 text-[9px] uppercase tracking-widest border transition-all ${buildTarget === t ? 'border-red-500 bg-red-500/10 text-red-400' : 'border-zinc-800 text-zinc-600 hover:text-zinc-300'}`} data-testid={`build-target-${t}`}>
                              {t === 'webgl' ? 'WebGL' : t === 'apk' ? 'APK' : 'Both'}
                            </button>
                          ))}
                        </div>
                      </div>
                      <div>
                        <label className="text-[9px] text-zinc-500 uppercase tracking-widest block mb-2">Optimization</label>
                        <div className="grid grid-cols-3 gap-2">
                          {['speed', 'balanced', 'size'].map(o => (
                            <button key={o} onClick={() => setBuildOptimization(o)} className={`py-2 text-[9px] uppercase tracking-widest border transition-all ${buildOptimization === o ? 'border-red-500 bg-red-500/10 text-red-400' : 'border-zinc-800 text-zinc-600 hover:text-zinc-300'}`}>
                              {o}
                            </button>
                          ))}
                        </div>
                      </div>
                    </div>
                    <button
                      onClick={async () => {
                        const sel = document.getElementById('build-project-select');
                        const pid = sel?.value;
                        if (!pid || projects.length === 0) return;
                        await axios.post(`${API}/builds`, { project_id: pid, target: buildTarget, optimization: buildOptimization });
                        fetchData();
                      }}
                      disabled={projects.length === 0}
                      className="w-full py-4 font-bold tracking-[3px] uppercase text-[10px] border border-red-500 text-black bg-red-500 hover:bg-red-400 transition-all disabled:opacity-30 disabled:cursor-not-allowed"
                      data-testid="start-build-btn"
                    >
                      Initialize Build
                    </button>
                  </div>
                </div>
                <div className="col-span-7 space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-red-500 text-[10px] font-bold uppercase tracking-[3px]">Build Queue ({builds.length})</span>
                  </div>
                  <div className="space-y-3 max-h-[500px] overflow-y-auto custom-scrollbar">
                    {builds.length === 0 && <div className="glass-panel border-red-500/10 p-12 text-center text-zinc-600 text-[10px] uppercase tracking-widest">No builds yet</div>}
                    {builds.map(b => (
                      <div key={b.id} className="glass-panel border-red-500/20 p-5 space-y-3">
                        <div className="flex justify-between items-start">
                          <div>
                            <span className="text-zinc-200 text-xs font-bold">{b.id}</span>
                            <span className="text-zinc-500 text-[9px] ml-3">{b.project_name} / {b.target.toUpperCase()}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className={`px-2 py-0.5 text-[8px] uppercase tracking-widest border font-bold ${
                              b.status === 'completed' ? 'border-emerald-500/30 text-emerald-500 bg-emerald-500/10' :
                              b.status === 'building' ? 'border-cyan-500/30 text-cyan-400 bg-cyan-500/10' :
                              'border-zinc-700 text-zinc-400 bg-zinc-800/50'
                            }`}>{b.status}</span>
                            {b.status === 'queued' && (
                              <button
                                onClick={async () => {
                                  setCompilingBuild(b.id);
                                  try {
                                    await axios.post(`${API}/builds/${b.id}/compile`);
                                    await fetchData();
                                  } catch (e) { console.error("Compile failed:", e); }
                                  setCompilingBuild(null);
                                }}
                                disabled={compilingBuild === b.id}
                                className="text-[9px] border border-[#D4AF37]/50 bg-[#D4AF37]/10 text-[#D4AF37] px-3 py-1 hover:bg-[#D4AF37] hover:text-black transition-all font-bold"
                                data-testid={`compile-build-${b.id}`}
                              >
                                {compilingBuild === b.id ? 'Compiling...' : 'Compile AAA'}
                              </button>
                            )}
                            {b.status !== 'completed' && b.status !== 'queued' && (
                              <button onClick={async () => { await axios.post(`${API}/builds/${b.id}/advance`); fetchData(); }} className="text-[9px] border border-red-500/30 bg-red-500/10 text-red-400 px-2 py-1 hover:bg-red-500 hover:text-black transition-all" data-testid={`advance-build-${b.id}`}>
                                Advance
                              </button>
                            )}
                            <button onClick={async () => { await axios.delete(`${API}/builds/${b.id}`); fetchData(); }} className="text-zinc-600 hover:text-red-500 transition-colors"><XCircle size={14}/></button>
                          </div>
                        </div>
                        <div className="space-y-1.5">
                          {b.stages?.map((s, i) => (
                            <div key={i} className="flex items-center gap-3 text-[9px]">
                              <span className={`w-16 uppercase tracking-widest truncate ${s.status === 'completed' ? 'text-emerald-500' : s.status === 'processing' ? 'text-cyan-400' : 'text-zinc-600'}`}>{s.status === 'completed' ? 'DONE' : s.status === 'processing' ? `${s.progress}%` : 'WAIT'}</span>
                              <div className="flex-1 h-1 bg-black border border-zinc-900 overflow-hidden">
                                <div className={`h-full transition-all ${s.status === 'completed' ? 'bg-emerald-500' : s.status === 'processing' ? 'bg-cyan-500' : 'bg-zinc-900'}`} style={{width: `${s.progress}%`}}/>
                              </div>
                              <span className="text-zinc-500 w-32 truncate">{s.name}</span>
                            </div>
                          ))}
                        </div>
                        {b.download_url && (
                          <a
                            href={`${process.env.REACT_APP_BACKEND_URL}${b.download_url}`}
                            className="flex items-center justify-between bg-emerald-500/5 border border-emerald-500/20 p-3 mt-2 hover:bg-emerald-500/10 transition-all group"
                            data-testid={`download-build-${b.id}`}
                          >
                            <div className="flex items-center gap-2">
                              <Package size={14} className="text-emerald-400"/>
                              <span className="text-emerald-400 text-[10px] font-mono">{b.output}</span>
                            </div>
                            <div className="flex items-center gap-3">
                              <span className="text-zinc-500 text-[9px]">{b.size_mb} MB</span>
                              <span className="text-emerald-400 text-[9px] font-bold uppercase tracking-widest group-hover:underline">Download ZIP</span>
                            </div>
                          </a>
                        )}
                        {b.output && !b.download_url && (
                          <div className="flex items-center justify-between bg-emerald-500/5 border border-emerald-500/20 p-3 mt-2">
                            <span className="text-emerald-400 text-[10px] font-mono">{b.output}</span>
                            <span className="text-zinc-500 text-[9px]">{b.size_mb} MB</span>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* VAULT: COMPLIANCE */}
            {partition === 'vault' && activeTab === 'COMPLIANCE' && (
              <div className="grid grid-cols-12 gap-6 animate-in fade-in max-w-7xl mx-auto w-full" data-testid="compliance-panel">
                <div className="col-span-4 space-y-6">
                  <div className="glass-panel border-red-500/20 p-8 space-y-6 tech-border-red">
                    <h3 className="text-red-500 text-xs font-black uppercase tracking-[4px] border-b border-red-500/20 pb-4 flex items-center gap-3"><FileCheck size={16}/> Certification Scan</h3>
                    <div className="space-y-4">
                      <div>
                        <label className="text-[9px] text-zinc-500 uppercase tracking-widest block mb-2">Target Project</label>
                        <select className="input-dark focus:border-red-500 uppercase tracking-widest" data-testid="compliance-project-select" id="compliance-project-select">
                          {projects.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
                          {projects.length === 0 && <option>No projects</option>}
                        </select>
                      </div>
                      <div>
                        <label className="text-[9px] text-zinc-500 uppercase tracking-widest block mb-2">Jurisdiction</label>
                        <div className="grid grid-cols-2 gap-2">
                          {['GLI', 'MGA', 'UKGC', 'CURACAO'].map(j => (
                            <button key={j} onClick={() => setComplianceJurisdiction(j)} className={`py-2 text-[9px] uppercase tracking-widest border transition-all ${complianceJurisdiction === j ? 'border-red-500 bg-red-500/10 text-red-400' : 'border-zinc-800 text-zinc-600 hover:text-zinc-300'}`} data-testid={`jurisdiction-${j}`}>
                              {j}
                            </button>
                          ))}
                        </div>
                      </div>
                    </div>
                    <button
                      onClick={async () => {
                        const sel = document.getElementById('compliance-project-select');
                        const pid = sel?.value;
                        if (!pid || projects.length === 0) return;
                        await axios.post(`${API}/compliance/check`, { project_id: pid, jurisdiction: complianceJurisdiction });
                        fetchData();
                      }}
                      disabled={projects.length === 0}
                      className="w-full py-4 font-bold tracking-[3px] uppercase text-[10px] border border-red-500 text-black bg-red-500 hover:bg-red-400 transition-all disabled:opacity-30"
                      data-testid="run-compliance-btn"
                    >
                      Run Certification Scan
                    </button>

                    <div className="relative">
                      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-emerald-500/30 to-transparent"></div>
                      <button
                        onClick={async () => {
                          const sel = document.getElementById('compliance-project-select');
                          const pid = sel?.value;
                          if (!pid || projects.length === 0) return;
                          setAutoCertifying(true);
                          setCertifySteps([{ step: 'INIT', detail: 'Starting Auto-Certify pipeline...', status: 'running' }]);
                          try {
                            const res = await axios.post(`${API}/compliance/auto-certify`, { project_id: pid, jurisdiction: complianceJurisdiction });
                            setCertifySteps(res.data.steps || []);
                            fetchData();
                          } catch (e) {
                            setCertifySteps(prev => [...prev, { step: 'ERROR', detail: e.response?.data?.detail || e.message, status: 'error' }]);
                          }
                          setAutoCertifying(false);
                        }}
                        disabled={projects.length === 0 || autoCertifying}
                        className="w-full py-4 mt-3 font-bold tracking-[3px] uppercase text-[10px] border border-emerald-500 text-emerald-400 bg-emerald-500/10 hover:bg-emerald-500 hover:text-black transition-all disabled:opacity-30 flex items-center justify-center gap-2"
                        data-testid="auto-certify-btn"
                      >
                        {autoCertifying ? (
                          <><RefreshCw size={12} className="animate-spin" /> Certifying...</>
                        ) : (
                          <><ShieldCheck size={12} /> Auto-Certify</>
                        )}
                      </button>
                    </div>

                    {/* Auto-Certify Step Log */}
                    {certifySteps.length > 0 && (
                      <div className="space-y-2 mt-4" data-testid="certify-steps">
                        <span className="text-[8px] text-zinc-600 uppercase tracking-widest">Certification Pipeline</span>
                        {certifySteps.map((s, i) => (
                          <div key={i} className={`p-3 border text-[10px] font-mono ${
                            s.status === 'done' ? 'border-emerald-500/20 bg-emerald-500/5' :
                            s.status === 'running' ? 'border-cyan-500/20 bg-cyan-500/5' :
                            'border-red-500/20 bg-red-500/5'
                          }`}>
                            <div className="flex items-center gap-2">
                              {s.status === 'done' && <CheckCircle2 size={10} className="text-emerald-400" />}
                              {s.status === 'running' && <RefreshCw size={10} className="text-cyan-400 animate-spin" />}
                              {s.status === 'error' && <XCircle size={10} className="text-red-400" />}
                              <span className={`font-bold uppercase tracking-wider ${
                                s.status === 'done' ? 'text-emerald-400' : s.status === 'running' ? 'text-cyan-400' : 'text-red-400'
                              }`}>{s.step}</span>
                            </div>
                            <p className="text-zinc-400 mt-1 text-[9px]">{s.detail}</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
                <div className="col-span-8 space-y-4">
                  <span className="text-red-500 text-[10px] font-bold uppercase tracking-[3px]">Compliance Reports ({complianceReports.length})</span>
                  <div className="space-y-4 max-h-[500px] overflow-y-auto custom-scrollbar">
                    {complianceReports.length === 0 && <div className="glass-panel border-red-500/10 p-12 text-center text-zinc-600 text-[10px] uppercase tracking-widest">No compliance reports</div>}
                    {complianceReports.map(r => (
                      <div key={r.id} className="glass-panel border-red-500/20 p-5 space-y-4">
                        <div className="flex justify-between items-start">
                          <div>
                            <span className="text-zinc-200 text-xs font-bold">{r.id}</span>
                            <span className="text-zinc-500 text-[9px] ml-3">{r.project_name} / {r.jurisdiction}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className={`px-3 py-1 text-[9px] uppercase tracking-widest border font-bold ${
                              r.status === 'CERTIFIED' ? 'border-emerald-500/30 text-emerald-500 bg-emerald-500/10' : r.status === 'CONDITIONAL' ? 'border-amber-500/30 text-amber-500 bg-amber-500/10' : 'border-red-500/30 text-red-500 bg-red-500/10'
                            }`}>{r.status}</span>
                            <span className="text-zinc-500 text-[9px] font-mono">{r.pass_rate}</span>
                            <button onClick={async () => { await axios.delete(`${API}/compliance/${r.id}`); fetchData(); }} className="text-zinc-600 hover:text-red-500 transition-colors"><XCircle size={14}/></button>
                          </div>
                        </div>
                        {/* RTP Info Bar */}
                        {r.actual_rtp && (
                          <div className="flex gap-3 text-[9px]">
                            <div className="bg-black/50 border border-zinc-800 px-3 py-1.5 flex gap-2">
                              <span className="text-zinc-600 uppercase">Actual RTP:</span>
                              <span className={r.actual_rtp === 'Not generated' ? 'text-amber-400' : 'text-emerald-400 font-bold'}>{r.actual_rtp}</span>
                            </div>
                            <div className="bg-black/50 border border-zinc-800 px-3 py-1.5 flex gap-2">
                              <span className="text-zinc-600 uppercase">Min Required:</span>
                              <span className="text-zinc-400 font-bold">{r.min_rtp_required || 'N/A'}</span>
                            </div>
                            {r.has_logic_data !== undefined && (
                              <div className="bg-black/50 border border-zinc-800 px-3 py-1.5 flex gap-2">
                                <span className="text-zinc-600 uppercase">Logic Data:</span>
                                <span className={r.has_logic_data ? 'text-emerald-400' : 'text-amber-400'}>{r.has_logic_data ? 'YES' : 'NO'}</span>
                              </div>
                            )}
                          </div>
                        )}
                        <div className="grid grid-cols-2 gap-2">
                          {r.results?.map((c, i) => (
                            <div key={i} className={`p-3 border text-[10px] ${c.status === 'PASS' ? 'border-emerald-500/20 bg-emerald-500/5' : c.status === 'WARN' ? 'border-amber-500/20 bg-amber-500/5' : 'border-red-500/20 bg-red-500/5'}`}>
                              <div className="flex justify-between items-center">
                                <span className={c.status === 'PASS' ? 'text-emerald-400' : c.status === 'WARN' ? 'text-amber-400' : 'text-red-400'}>{c.check}</span>
                                <span className={`font-bold ${c.status === 'PASS' ? 'text-emerald-500' : c.status === 'WARN' ? 'text-amber-500' : 'text-red-500'}`}>{c.status}</span>
                              </div>
                              {c.value && <span className="text-zinc-500 text-[9px] font-mono">{c.value}</span>}
                              {c.details && <p className="text-zinc-600 text-[8px] mt-1 leading-relaxed">{c.details}</p>}
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* VAULT: ARTTECH NEXUS */}
            {partition === 'vault' && activeTab === 'ARTTECH NEXUS' && (
              <ArtTechNexusPanel nexusPipelines={nexusPipelines} osModules={osModules} />
            )}

            {/* VAULT: MATRIX PARAMS */}
            {partition === 'vault' && activeTab === 'MATRIX PARAMS' && (
              <MatrixParamsPanel matrixParams={matrixParams} />
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
              <div className="animate-in fade-in max-w-7xl mx-auto w-full space-y-4" data-testid="night-queue-panel">
                {/* View Toggle */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-red-500 text-[10px] font-bold uppercase tracking-[3px]">Night Queue ({queue.length})</span>
                    {workerStatus.running && <span className="text-[9px] text-emerald-500 uppercase tracking-widest flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span> Auto-Processing</span>}
                    {workerStatus.blocked_jobs > 0 && <span className="text-[9px] text-amber-500 uppercase tracking-widest">{workerStatus.blocked_jobs} blocked</span>}
                  </div>
                  <div className="flex gap-1">
                    {['list','graph'].map(v => (
                      <button key={v} onClick={() => setNightQueueView(v)} className={`px-4 py-1.5 text-[9px] uppercase tracking-widest border transition-all ${nightQueueView === v ? 'border-red-500 bg-red-500/10 text-red-400' : 'border-zinc-800 text-zinc-600 hover:text-zinc-300'}`} data-testid={`nq-view-${v}`}>
                        {v}
                      </button>
                    ))}
                  </div>
                </div>

                {nightQueueView === 'graph' ? (
                  <div className="glass-panel border-red-500/20 h-[480px] overflow-hidden">
                    <DependencyGraph
                      nodes={depGraph.nodes}
                      edges={depGraph.edges}
                      onLink={async (childId, parentId) => {
                        await axios.post(`${API}/jobs/${childId}/link?depends_on_id=${parentId}`);
                        fetchData();
                      }}
                      onUnlink={async (childId, parentId) => {
                        await axios.delete(`${API}/jobs/${childId}/link/${parentId}`);
                        fetchData();
                      }}
                    />
                  </div>
                ) : (
                  <div className="grid grid-cols-12 gap-6">
                    {/* Controls Sidebar */}
                    <div className="col-span-4 space-y-5">
                      {/* Worker Status */}
                      <div className="glass-panel border-red-500/20 p-6 space-y-4">
                        <div className="flex items-center justify-between">
                          <h3 className="text-red-500 text-[10px] font-bold uppercase tracking-[3px] flex items-center gap-2"><Moon size={14}/> Worker Engine</h3>
                          <span className={`w-2.5 h-2.5 rounded-full ${workerStatus.running ? 'bg-emerald-500 animate-pulse' : 'bg-zinc-700'}`}></span>
                        </div>
                        <div className="grid grid-cols-4 gap-2 text-center">
                          <div className="border border-zinc-800 bg-black p-2">
                            <div className="text-base font-bold text-cyan-400">{workerStatus.active_jobs}</div>
                            <div className="text-[7px] text-zinc-500 uppercase tracking-widest">Active</div>
                          </div>
                          <div className="border border-zinc-800 bg-black p-2">
                            <div className="text-base font-bold text-amber-500">{workerStatus.blocked_jobs || 0}</div>
                            <div className="text-[7px] text-zinc-500 uppercase tracking-widest">Blocked</div>
                          </div>
                          <div className="border border-zinc-800 bg-black p-2">
                            <div className="text-base font-bold text-emerald-500">{workerStatus.completed_jobs}</div>
                            <div className="text-[7px] text-zinc-500 uppercase tracking-widest">Done</div>
                          </div>
                          <div className="border border-zinc-800 bg-black p-2">
                            <div className="text-base font-bold text-zinc-400">{workerStatus.total_jobs}</div>
                            <div className="text-[7px] text-zinc-500 uppercase tracking-widest">Total</div>
                          </div>
                        </div>
                        <button
                          onClick={async () => { await axios.post(`${API}/worker/toggle`); const r = await axios.get(`${API}/worker/status`); setWorkerStatus(r.data); }}
                          className={`w-full py-2.5 text-[10px] uppercase tracking-[3px] font-bold border transition-all ${
                            workerStatus.running
                              ? 'border-red-500 bg-red-500/10 text-red-400 hover:bg-red-500 hover:text-black'
                              : 'border-emerald-500 bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500 hover:text-black'
                          }`}
                          data-testid="toggle-worker-btn"
                        >
                          {workerStatus.running ? 'Stop Worker' : 'Start Worker'}
                        </button>
                      </div>

                      {/* Queue New Job */}
                      <div className="glass-panel border-red-500/20 p-6 space-y-4">
                        <h3 className="text-red-500 text-[10px] font-bold uppercase tracking-[3px] flex items-center gap-2"><Plus size={14}/> Queue Job</h3>
                        <div>
                          <label className="text-[9px] text-zinc-500 uppercase tracking-widest block mb-2">Preset</label>
                          <select
                            value={newJobPreset} onChange={e => setNewJobPreset(e.target.value)}
                            className="input-dark focus:border-red-500 uppercase tracking-widest text-[10px]"
                            data-testid="job-preset-select"
                          >
                            {Object.entries(CATEGORY_META).map(([catId, meta]) => (
                              <optgroup key={catId} label={meta.label}>
                                {UNIVERSAL_GAME_TYPES.filter(g => g.cat === catId).map(g => (
                                  <option key={g.id} value={g.id.toUpperCase()}>{g.label}</option>
                                ))}
                              </optgroup>
                            ))}
                          </select>
                        </div>
                        <div>
                          <label className="text-[9px] text-zinc-500 uppercase tracking-widest block mb-2">Priority</label>
                          <div className="grid grid-cols-3 gap-2">
                            {['low','normal','high'].map(pr => (
                              <button key={pr} onClick={() => setNewJobPriority(pr)} className={`py-1.5 text-[9px] uppercase tracking-widest border transition-all ${newJobPriority === pr ? 'border-red-500 bg-red-500/10 text-red-400' : 'border-zinc-800 text-zinc-600'}`}>
                                {pr}
                              </button>
                            ))}
                          </div>
                        </div>
                        {/* Dependency Picker */}
                        <div>
                          <label className="text-[9px] text-zinc-500 uppercase tracking-widest block mb-2">Depends On ({newJobDeps.length})</label>
                          <div className="max-h-28 overflow-y-auto space-y-1 custom-scrollbar">
                            {queue.filter(j => j.status !== 'completed').length === 0 && (
                              <div className="text-[8px] text-zinc-700 py-2">No active jobs to depend on</div>
                            )}
                            {queue.filter(j => j.status !== 'completed').map(j => (
                              <button
                                key={j.id}
                                onClick={() => setNewJobDeps(prev => prev.includes(j.id) ? prev.filter(d => d !== j.id) : [...prev, j.id])}
                                className={`w-full text-left px-2 py-1 text-[9px] font-mono border transition-all flex items-center gap-2 ${
                                  newJobDeps.includes(j.id) ? 'border-amber-500/50 bg-amber-500/10 text-amber-400' : 'border-zinc-800 text-zinc-500 hover:text-zinc-300'
                                }`}
                                data-testid={`dep-pick-${j.id}`}
                              >
                                <Link2 size={8} className={newJobDeps.includes(j.id) ? 'text-amber-500' : 'text-zinc-700'} />
                                {j.id} <span className="text-zinc-600 ml-auto">{j.preset}</span>
                              </button>
                            ))}
                          </div>
                        </div>
                        <button
                          onClick={async () => {
                            await axios.post(`${API}/jobs`, { preset: newJobPreset, priority: newJobPriority, depends_on: newJobDeps.length > 0 ? newJobDeps : null });
                            setNewJobDeps([]);
                            fetchData();
                            const r = await axios.get(`${API}/worker/status`);
                            setWorkerStatus(r.data);
                          }}
                          className="w-full py-3 font-bold tracking-[3px] uppercase text-[10px] border border-red-500 text-black bg-red-500 hover:bg-red-400 transition-all"
                          data-testid="queue-job-btn"
                        >
                          Queue Job {newJobDeps.length > 0 ? `(${newJobDeps.length} deps)` : ''}
                        </button>
                      </div>
                    </div>

                    {/* Job Queue List */}
                    <div className="col-span-8 space-y-3 max-h-[550px] overflow-y-auto custom-scrollbar">
                      {queue.length === 0 && <div className="glass-panel border-red-500/10 p-12 text-center text-zinc-600 text-[10px] uppercase tracking-widest">Queue empty — add a job to begin.</div>}
                      {queue.map(item => (
                        <div key={item.id} className={`glass-panel p-4 space-y-3 ${
                          item.status === 'completed' ? 'border-emerald-500/20' :
                          item.status === 'processing' ? 'border-cyan-500/20' :
                          item.status === 'blocked' ? 'border-amber-500/20' :
                          'border-red-500/15'
                        }`}>
                          <div className="flex justify-between items-start">
                            <div className="flex items-center gap-2 flex-wrap">
                              <span className="text-zinc-200 text-xs font-bold">{item.id}</span>
                              <span className="text-red-400 text-[9px] font-mono">{item.preset}</span>
                              <span className={`text-[8px] uppercase tracking-widest ${item.priority === 'high' ? 'text-amber-500' : item.priority === 'low' ? 'text-zinc-600' : 'text-zinc-500'}`}>{item.priority}</span>
                              {item.depends_on?.length > 0 && (
                                <span className="text-[8px] text-amber-500/70 flex items-center gap-1"><Link2 size={8}/> {item.depends_on.length} dep{item.depends_on.length > 1 ? 's' : ''}</span>
                              )}
                              {item.dependents?.length > 0 && (
                                <span className="text-[8px] text-cyan-500/70 flex items-center gap-1">{item.dependents.length} child{item.dependents.length > 1 ? 'ren' : ''}</span>
                              )}
                            </div>
                            <div className="flex items-center gap-2">
                              <span className={`px-2 py-0.5 text-[8px] uppercase tracking-widest border font-bold ${
                                item.status === 'completed' ? 'border-emerald-500/30 text-emerald-500 bg-emerald-500/10' :
                                item.status === 'processing' ? 'border-cyan-500/30 text-cyan-400 bg-cyan-500/10' :
                                item.status === 'blocked' ? 'border-amber-500/30 text-amber-500 bg-amber-500/10' :
                                item.status === 'failed' ? 'border-red-500/30 text-red-500 bg-red-500/10' :
                                'border-zinc-700 text-zinc-400'
                              }`}>{item.status}</span>
                              <span className="text-[10px] font-mono text-zinc-500">{item.progress}%</span>
                              <button onClick={() => removeQueueItem(item.id)} className="text-zinc-600 hover:text-red-500 transition-colors"><XCircle size={14}/></button>
                            </div>
                          </div>
                          {/* Blocked reason */}
                          {item.status === 'blocked' && item.depends_on?.length > 0 && (
                            <div className="text-[8px] text-amber-500/60 uppercase tracking-widest bg-amber-500/5 border border-amber-500/10 px-3 py-1.5">
                              Waiting on: {item.depends_on.join(', ')}
                            </div>
                          )}
                          {/* Stage Progress */}
                          {item.stages && item.stages.length > 0 && item.status !== 'blocked' && (
                            <div className="space-y-1">
                              {item.stages.map((s, i) => (
                                <div key={i} className="flex items-center gap-3 text-[9px]">
                                  <span className={`w-12 uppercase tracking-widest truncate font-mono ${s.status === 'completed' ? 'text-emerald-500' : s.status === 'processing' ? 'text-cyan-400' : 'text-zinc-700'}`}>{s.status === 'completed' ? 'DONE' : s.status === 'processing' ? `${s.progress}%` : '---'}</span>
                                  <div className="flex-1 h-1 bg-black border border-zinc-900 overflow-hidden">
                                    <div className={`h-full transition-all duration-500 ${s.status === 'completed' ? 'bg-emerald-500' : s.status === 'processing' ? 'bg-cyan-500' : 'bg-zinc-900'}`} style={{width: `${s.progress}%`}}/>
                                  </div>
                                  <span className="text-zinc-500 w-28 truncate text-right">{s.name}</span>
                                </div>
                              ))}
                            </div>
                          )}
                          {/* Stages placeholder for blocked jobs */}
                          {item.status === 'blocked' && (
                            <div className="text-[9px] text-zinc-700 font-mono">— {item.stages?.length || 0} stages waiting —</div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
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
