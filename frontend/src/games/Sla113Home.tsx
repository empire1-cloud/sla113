'use client';

import React, { useState, useEffect } from 'react';
import { 
  Activity, Database, 
  Zap, 
  Cpu, Wallet, SlidersHorizontal,
  Scissors, Save, Shield, CheckCircle2, XCircle,
  Box, Play, RefreshCw
} from 'lucide-react';

// --- Constants & Styles ---

const STYLES = `
  :root {
    --obsidian: #050505;
    --gold: #D4AF37;
    --cyan: #00C8FF;
    --syntax-green: #50fa7b;
    --syntax-purple: #bd93f9;
  }
  .liquid-chrome { color: #fff; text-transform: uppercase; letter-spacing: 0.2em; font-weight: 800; }
  .glass-panel {
    background: rgba(13, 13, 13, 0.98);
    border: 1px solid #1a1a1a;
    box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.5);
  }
  .input-dark {
    background: #000; border: 1px solid #1a1a1a; color: var(--cyan);
    padding: 12px; font-size: 0.75rem; outline: none; width: 100%;
    font-family: monospace; transition: border-color 0.2s;
  }
  .input-dark:focus { border-color: var(--syntax-purple); }
  .btn-action {
    background: #0f0f0f; border: 1px solid #1f1f1f; color: #666;
    transition: 0.2s steps(4); text-transform: uppercase;
    font-size: 0.65rem; letter-spacing: 0.1em;
  }
  .btn-action:hover:not(:disabled) {
    border-color: var(--cyan); color: var(--cyan); background: rgba(0, 200, 255, 0.03);
  }
  @keyframes scanline { 0% { transform: translateY(-100%); } 100% { transform: translateY(100%); } }
  .scanline {
    position: absolute; top: 0; left: 0; width: 100%; height: 2px;
    background: rgba(0, 200, 255, 0.05);
    animation: scanline 6s linear infinite; pointer-events: none;
  }
  .os-card { border: 1px solid #111; background: rgba(0,0,0,0.4); transition: 0.2s; cursor: pointer; }
  .os-card:hover { border-color: #333; }
  .os-card.selected { border-color: var(--cyan); background: rgba(0, 200, 255, 0.02); }
  .hitbox-overlay { position: absolute; border: 1px solid red; background: rgba(255,0,0,0.1); pointer-events: none; }
`;

type OsKey = 'AAA_FISH_SLOT' | 'GTA5_TYPE' | 'COD_WARFARE' | 'FANTASY_RPG' | 'BPO_PANO';
type SlaModeKey = 'FACTORY' | 'EMPIRE_1' | 'FOUNDRY' | 'VAULT' | 'TECH' | 'HUMAN';

const ENGINE_PRESETS: Record<OsKey, { title: string, desc: string, base: string }> = {
  AAA_FISH_SLOT: { title: "Arcade Pipeline", desc: "Lounge // Fish // Slots", base: "industrial casino grade, luxury obsidian textures, neon gold filigree" },
  GTA5_TYPE: { title: "Open World", desc: "Urban // Vehicles // Grit", base: "urban cinematic realism, realistic vehicle surfaces, dramatic sunset lighting" },
  COD_WARFARE: { title: "Tactical FPS", desc: "Mil-Spec // Polymer", base: "tactical military spec, polymer matte black, industrial steel wear" },
  FANTASY_RPG: { title: "Epic RPG", desc: "Mythic // Boss // Canon", base: "epic fantasy mythical architect, aztec stone motifs, deep obsidian shadows" },
  BPO_PANO: { title: "Paño Arte", desc: "Paño // Chicano", base: "authentic chicano paño arte, blue ballpoint pen ink on white handkerchief cloth" }
};

const MODE_SWITCHER: Array<{ key: SlaModeKey; label: string; subtitle: string; defaultTab: string; nav: string[] }> = [
  { key: 'FACTORY', label: 'FACTORY', subtitle: 'LIVE_OPERATIONS', defaultTab: 'FACTORY_OVERVIEW', nav: ['FRONTLINE', 'WHITE_LABEL_MINT', 'DEPLOY_CENTER', 'UNIVERSES', 'FISH_ARENA'] },
  { key: 'EMPIRE_1', label: 'EMPIRE 1', subtitle: 'REVENUE_MATRIX', defaultTab: 'EMPIRE_OVERVIEW', nav: ['MINT_LEDGER', 'REVENUE_PIPELINES', 'BESTIARY', 'SLOT_SYMBOLS'] },
  { key: 'FOUNDRY', label: 'FOUNDRY', subtitle: 'CREATIVE_TOOLS', defaultTab: 'FOUNDRY_OVERVIEW', nav: ['OS_BUILDER', 'VISION_SMITH', 'AUDIO_FORGE', 'SPRITE_REGISTRY', 'GAME_COMPOSER'] },
  { key: 'VAULT', label: 'VAULT', subtitle: 'SECURITY_CORE', defaultTab: 'VAULT_COMPLIANCE', nav: ['BUILD_PIPELINE', 'COMPLIANCE', 'ARTTECH_NEXUS', 'MATRIX_PARAMS', 'SYSTEM_CORE', 'NIGHT_QUEUE'] },
  { key: 'TECH', label: 'TECH', subtitle: 'SYSTEM_GRID', defaultTab: 'Universal_Builder', nav: ['ROUTER_GRID', 'KERNEL_HEALTH', 'DRIFT_WATCH', 'TELEMETRY'] },
  { key: 'HUMAN', label: 'HUMAN', subtitle: 'OPERATOR_LINK', defaultTab: 'Sprite_Cutter', nav: ['OPERATOR_NOTES', 'CREATIVE_BRIEF', 'TONE_ENFORCER', 'SUPPORT_QUEUE'] },
];

const MODE_NAV_TO_TAB: Record<string, string> = {
  FRONTLINE: 'FACTORY_OVERVIEW',
  WHITE_LABEL_MINT: 'FACTORY_OVERVIEW',
  DEPLOY_CENTER: 'FACTORY_OVERVIEW',
  UNIVERSES: 'FACTORY_OVERVIEW',
  FISH_ARENA: 'FACTORY_OVERVIEW',
  MINT_LEDGER: 'EMPIRE_OVERVIEW',
  REVENUE_PIPELINES: 'EMPIRE_OVERVIEW',
  BESTIARY: 'EMPIRE_OVERVIEW',
  SLOT_SYMBOLS: 'EMPIRE_OVERVIEW',
  OS_BUILDER: 'FOUNDRY_OVERVIEW',
  VISION_SMITH: 'FOUNDRY_OVERVIEW',
  AUDIO_FORGE: 'FOUNDRY_OVERVIEW',
  SPRITE_REGISTRY: 'FOUNDRY_REGISTRY',
  GAME_COMPOSER: 'FOUNDRY_OVERVIEW',
  BUILD_PIPELINE: 'VAULT_PIPELINE',
  COMPLIANCE: 'VAULT_COMPLIANCE',
  ARTTECH_NEXUS: 'VAULT_COMPLIANCE',
  MATRIX_PARAMS: 'VAULT_COMPLIANCE',
  SYSTEM_CORE: 'VAULT_PIPELINE',
  NIGHT_QUEUE: 'VAULT_PIPELINE',
  ROUTER_GRID: 'Universal_Builder',
  KERNEL_HEALTH: 'Universal_Builder',
  DRIFT_WATCH: 'Southern_Foundry',
  TELEMETRY: 'Universal_Builder',
  OPERATOR_NOTES: 'Sprite_Cutter',
  CREATIVE_BRIEF: 'Sprite_Cutter',
  TONE_ENFORCER: 'Universal_Builder',
  SUPPORT_QUEUE: 'Sprite_Cutter',
};

const MODE_THEME: Record<SlaModeKey, { accent: string; border: string; panel: string }> = {
  FACTORY: { accent: 'text-cyan-400', border: 'border-cyan-500', panel: 'bg-cyan-900/20' },
  EMPIRE_1: { accent: 'text-indigo-400', border: 'border-indigo-500', panel: 'bg-indigo-900/20' },
  FOUNDRY: { accent: 'text-yellow-400', border: 'border-yellow-500', panel: 'bg-yellow-900/20' },
  VAULT: { accent: 'text-red-400', border: 'border-red-500', panel: 'bg-red-900/20' },
  TECH: { accent: 'text-zinc-200', border: 'border-zinc-500', panel: 'bg-zinc-800/70' },
  HUMAN: { accent: 'text-emerald-400', border: 'border-emerald-500', panel: 'bg-emerald-900/20' },
};

const BUILD_ARCHITECTURE_LEDGER = [
  { id: 'OS_BUILD_1775530940808', project: 'Neon Fish Hunt', className: 'fish_shooter' },
  { id: 'OS_BUILD_1775597123678', project: 'Gold Rush Slots', className: 'slot_machine' },
  { id: 'OS_BUILD_1775597773789', project: 'Barrio Runner', className: 'platformer' },
  { id: 'OS_BUILD_1775597869804', project: 'Aztec Gold', className: 'slot_machine' },
  { id: 'OS_BUILD_17756039865459', project: 'Sovereign Fish Arena', className: 'fish_shooter' },
  { id: 'OS_BUILD_1775683989804', project: 'Shadow Pack', className: 'fish_shooter' },
  { id: 'OS_BUILD_1775803915307', project: 'Jaguar Champion', className: 'boss_hunt' },
  { id: 'OS_BUILD_1776061875297', project: 'Aztec Gold Sovereign', className: 'slot_machine' },
  { id: 'OS_BUILD_1776221025501', project: 'Sovereign Fish Arena v2', className: 'fish_shooter' },
  { id: 'OS_BUILD_1776408841208', project: 'Aztec Depths', className: 'fish_shooter' },
  { id: 'OS_BUILD_1776502200011', project: 'Aztec Depths v3', className: 'fish_shooter' },
];

const SPRITE_ASSET_REGISTRY = [
  { name: 'Southern Lifestyle Loader', type: 'UI', frames: 1, size: '1080x1080' },
  { name: 'Slam Members Only', type: 'UI', frames: 1, size: '1920x1920' },
  { name: 'SouthernLyfestyle Arcade Lobby', type: 'BACKGROUND', frames: 1, size: '2048x2048' },
  { name: 'G-Wolf', type: 'BOSS', frames: 19, size: '410x512' },
  { name: 'Aztec Fish Species V2', type: 'FISH', frames: 15, size: '512x512' },
  { name: 'Jaguar Warrior Champion', type: 'BOSS', frames: 19, size: '400x400' },
  { name: 'Jaguar Warrior Elite', type: 'BOSS', frames: 23, size: '320x400' },
  { name: 'Wolf Xolotl Pack', type: 'BOSS', frames: 27, size: '512x512' },
];

const VAULT_COMPLIANCE_REPORTS = [
  { id: 'CMP-00310256', target: 'Aztec Depths v3 / GLI', status: 'NEEDS_REMEDIATION', checks: '3/6' },
  { id: 'CMP-0776EF14', target: 'Aztec Depths v3 / GLI', status: 'CONDITIONAL', checks: '3/6' },
  { id: 'CMP-500E4730', target: 'Build_1775597123678 / UKGC', status: 'NEEDS_REMEDIATION', checks: '2/6' },
  { id: 'CMP-91A10391', target: 'Sovereign Fish Arena / MGA', status: 'PASS', checks: '6/6' },
];

const FACTORY_BUILD_LEDGER = [
  'Neon Fish Hunt',
  'Deploy Test Game',
  'Gold Rush Slots',
  'Barrio Runner',
  'Aztec Gold Slots',
  'Southern Gold Slots',
  'Sovereign Fish Arena',
  'Aztec Depths v5',
];

const FOUNDRY_ASSETS = [
  { name: 'Southern Lifestyle Loader', type: 'UI', frames: 1, resolution: '1080x1080', grid: '1x1' },
  { name: 'Slam Members Only', type: 'UI', frames: 1, resolution: '1920x1920', grid: '1x1' },
  { name: 'SouthernLyfestyle Arcade Lobby', type: 'BACKGROUND', frames: 1, resolution: '2048x2048', grid: '1x1' },
  { name: 'G-Wolf', type: 'BOSS', frames: 19, resolution: '410x512', grid: '5x4' },
  { name: 'Aztec Fish Species V2', type: 'FISH', frames: 15, resolution: '512x512', grid: '4x4' },
  { name: 'Jaguar Warrior Champion', type: 'BOSS', frames: 19, resolution: '400x400', grid: '4x5' },
  { name: 'Jaguar Warrior Elite', type: 'BOSS', frames: 23, resolution: '320x400', grid: '5x5' },
  { name: 'Wolf Xolotl Pack', type: 'BOSS', frames: 24, resolution: '640x640', grid: '6x4' },
];

const VAULT_REPORTS = [
  { id: 'CMP-00310256', target: 'Aztec Depths v3 / GLI', status: 'NEEDS_REMEDIATION', checks: ['RTP Verification', 'RNG Seed Audit', 'Paytable Integrity', 'Max Bet Limits'] },
  { id: 'CMP-D776EF14', target: 'Aztec Depths v3 / GLI', status: 'CONDITIONAL', checks: ['RTP Verification', 'RNG Seed Audit', 'Session Timeout Compliance', 'Responsible Gaming Controls'] },
  { id: 'CMP-500E4730', target: 'OS_BUILD_1775597123678 / UKGC', status: 'NEEDS_REMEDIATION', checks: ['RTP Verification', 'RNG Seed Audit', 'Paytable Integrity', 'Responsible Gaming Controls'] },
];

const EMPIRE_BOSS_ROSTER = [
  { name: 'Xochipilli Scathed', tier: 'MYTHIC', hp: '850K' },
  { name: 'Lobo Negro', tier: 'LEGENDARY', hp: '628K' },
  { name: 'La Reina Oscura', tier: 'MYTHIC', hp: '780K' },
];

/**
 * SLA113 // OPERATOR_CONSOLE
 * Admin dashboard for sla113.southernlifestyle.org
 */
export default function Sla113Home() {
  const [activeTab, setActiveTab] = useState('Universal_Builder');
  const [activeMode, setActiveMode] = useState<SlaModeKey>('FACTORY');
  const [activeModeNav, setActiveModeNav] = useState('FRONTLINE');
  const API_KEY = process.env.NEXT_PUBLIC_GOOGLE_API_KEY || "AIzaSyBvWiHFNhdicOrYhq3xsmJ0LBqylNWnSR0"; 
  
  // --- Universal Builder State ---
  const [currentOS, setCurrentOS] = useState<OsKey>('FANTASY_RPG');
  const [nexusPrompt, setNexusPrompt] = useState("");
  const [nexusPreview, setNexusPreview] = useState<string | null>(null);
  const [isGeneratingNexus, setIsGeneratingNexus] = useState(false);

  // AAA Matrix Selections
  const [sysCore, setSysCore] = useState('UE5_CHAOS');
  const [sysAudio, setSysAudio] = useState('FMOD_STUDIO');
  const [sysRender, setSysRender] = useState('LUMEN_RTX');
  const [sysBiome, setSysBiome] = useState('ABYSSAL_WASTES');
  const [sysBoss, setSysBoss] = useState('MECHA_DEITY');

  // --- Sprite Cutter State ---
  const [selectedSprite, setSelectedSprite] = useState("fish_boss_01.png");
  const [hitbox, setHitbox] = useState({ x: 20, y: 20, w: 60, h: 60 });

  // --- Southern Foundry State ---
  const [auditState, setAuditState] = useState<any>(null);

  useEffect(() => {
    if (activeTab === 'Southern_Foundry') {
      fetch('/api/foundry/api/audit-state')
        .then(r => r.json())
        .then(d => setAuditState(d));
    }
  }, [activeTab]);

  useEffect(() => {
    const mode = MODE_SWITCHER.find((entry) => entry.key === activeMode);
    const targetTab = mode?.defaultTab;
    if (targetTab) {
      setActiveTab(targetTab);
    }
    if (mode?.nav?.[0]) {
      setActiveModeNav(mode.nav[0]);
    }
  }, [activeMode]);

  const handleUniversalRender = async () => {
    setIsGeneratingNexus(true);
    setNexusPreview(null);
    const masterPrompt = `[SLA113_RENDER_TARGET]: AAA Game Asset Production [BASE_PIPELINE]: ${ENGINE_PRESETS[currentOS].base} [RENDER_ENGINE]: ${sysRender} [ENVIRONMENT_BIOME]: ${sysBiome.replace('_', ' ')} [ENTITY_ARCHETYPE]: ${sysBoss.replace('_', ' ')} [CUSTOM_SPEC]: ${nexusPrompt || "Center framed, hyper-detailed, masterpiece"} [ISOLATION]: Solid #050505 background for sprite extraction. 8k resolution, volumetric lighting.`;
    try {
      const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:predict?key=${API_KEY}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ instances: [{ prompt: masterPrompt }], parameters: { sampleCount: 1 } })
      });
      const data = await response.json();
      const b64 = data.predictions?.[0]?.bytesBase64Encoded;
      if (b64) setNexusPreview(`data:image/png;base64,${b64}`);
    } catch (e) {
      console.error("Render Failed", e);
    } finally {
      setIsGeneratingNexus(false);
    }
  };

  const handleAuditAction = async (action: 'approve' | 'reject') => {
    const endpoint = `/api/foundry/api/${action}`;
    const body = action === 'approve' ? { mode: 'arcade_hybrid' } : { prompt: 'Universal Regen' };
    await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    // Refresh audit state
    const res = await fetch('/api/foundry/api/audit-state');
    setAuditState(await res.json());
  };

  const OS_MODULES = [
    { name: "Lounge", utility: "Texture Extraction", output: "UI Skins: High-end gold/rose textures applied to the Slot machines." },
    { name: "Abyssal Wastes", utility: "Static Mesh Extraction", output: "Environment Kit: Modular urban ruins from El Monte/SGV used as the tactical map." },
    { name: "Southern Foundry", utility: "Material Logic", output: "Shader Tool: Auto-applies the \"Gold Foil\" PBR to any new asset imported into the OS." }
  ];

  const TABS = [
    { name: 'Universal_Builder', icon: Cpu },
    { name: 'Sprite_Cutter', icon: Scissors },
    { name: 'Southern_Foundry', icon: Database },
    { name: 'Ledger_Sync', icon: Wallet },
  ];
  const activeModeConfig = MODE_SWITCHER.find((entry) => entry.key === activeMode) || MODE_SWITCHER[0];
  const activeModeTheme = MODE_THEME[activeMode];
  const hasDedicatedModeSurface = activeMode === 'FOUNDRY' || activeMode === 'VAULT' || activeMode === 'EMPIRE_1';
  const isLegacyMode = activeMode === 'TECH' || activeMode === 'HUMAN';

  return (
    <>
      <style>{STYLES}</style>
      <div className="flex h-screen bg-[#050505] text-gray-200 font-mono overflow-hidden selection:bg-cyan-900 selection:text-white"
           style={{ backgroundImage: 'linear-gradient(rgba(0, 200, 255, 0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 200, 255, 0.02) 1px, transparent 1px)', backgroundSize: '40px 40px' }}>
        
        {/* SIDEBAR */}
        <aside className="w-64 bg-black/80 border-r border-zinc-900 flex flex-col z-20">
          <div className="p-6 border-b border-zinc-900">
            <h1 className="liquid-chrome text-xl tracking-tight text-white italic font-black">
              SLA113 <span className={activeModeTheme.accent}>{'//'} {activeModeConfig.label}</span>
            </h1>
            <p className="text-[9px] text-zinc-500 uppercase tracking-widest mt-1 font-bold">
              {activeModeConfig.subtitle.replace('_', ' ')}
            </p>
          </div>

          <div className="p-3 border-b border-zinc-900 bg-black/70">
            <p className="text-[8px] text-zinc-600 uppercase tracking-[0.18em] mb-2">Mode_Navigation</p>
            <div className="space-y-1">
              {activeModeConfig.nav.map((item) => (
                <button
                  key={item}
                  onClick={() => {
                    setActiveModeNav(item);
                    const nextTab = MODE_NAV_TO_TAB[item];
                    if (nextTab) setActiveTab(nextTab);
                  }}
                  className={`w-full text-left px-3 py-2 rounded-sm text-[9px] uppercase tracking-[0.16em] border ${
                    activeModeNav === item
                      ? `${activeModeTheme.border} ${activeModeTheme.accent} ${activeModeTheme.panel}`
                      : 'border-transparent text-zinc-500 hover:text-zinc-300 hover:bg-zinc-900/50'
                  }`}
                >
                  {item.replace(/_/g, ' ')}
                </button>
              ))}
            </div>
          </div>
          
          <nav className="flex-1 py-6 space-y-1 px-3 overflow-y-auto">
            {TABS.map((item) => (
              <button
                key={item.name}
                onClick={() => setActiveTab(item.name)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-sm text-[10px] uppercase tracking-widest transition-all ${
                  activeTab === item.name 
                    ? 'text-cyan-400 bg-cyan-900/10 border-l-2 border-cyan-400' 
                    : 'text-zinc-500 hover:text-zinc-300 hover:bg-zinc-900/50 border-l-2 border-transparent'
                }`}
              >
                <item.icon size={16} />
                {item.name.replace('_', ' ')}
              </button>
            ))}
          </nav>

          {/* DAEMON STATUS */}
          <div className="p-4 border-t border-zinc-900 bg-black/40">
            <div className={`text-[9px] uppercase tracking-[0.2em] border px-3 py-1 ${activeModeTheme.border} ${activeModeTheme.accent}`}>
              Daemon_Uplink
            </div>
            <div className="mt-3 space-y-2 text-[9px] uppercase tracking-wider">
              <div className="flex justify-between text-zinc-500">
                <span>CPU / RAM</span>
                <span>14% / 42.8 GB</span>
              </div>
              <div className="flex justify-between text-zinc-500">
                <span>NIGHT_QUEUE</span>
                <span className={activeModeTheme.accent}>0 PENDING</span>
              </div>
            </div>
          </div>
        </aside>

        {/* MAIN CONTENT AREA */}
        <main className="flex-1 flex flex-col h-screen overflow-y-auto relative z-10">
          <header className="sticky top-0 z-50 flex justify-between items-center px-8 py-3 border-b border-zinc-900 bg-black/90 backdrop-blur-md text-[9px]">
            <div className="flex items-center gap-6">
              <div className="text-white font-bold tracking-widest uppercase">Operator_Environment_v2.0.4</div>
              <div className="text-zinc-500 uppercase tracking-widest">Net_Revenue <span className="text-white text-2xl align-middle ml-1">$142,500</span></div>
              <div className="text-zinc-600">ID: <span className="text-zinc-400">ADMIN_OVERRIDE</span></div>
            </div>
            <div className="flex items-center gap-5">
              <div className="hidden lg:flex items-center gap-1 rounded-sm border border-zinc-800 bg-black/70 p-1">
                {MODE_SWITCHER.map((mode) => (
                  <button
                    key={mode.key}
                    onClick={() => setActiveMode(mode.key)}
                    className={`px-2 py-1 text-[8px] uppercase tracking-widest border ${
                      activeMode === mode.key
                        ? `${MODE_THEME[mode.key].border} ${MODE_THEME[mode.key].accent} ${MODE_THEME[mode.key].panel}`
                        : 'border-transparent text-zinc-500 hover:text-zinc-300'
                    }`}
                  >
                    {mode.label}
                  </button>
                ))}
              </div>
              <div className="text-zinc-600 uppercase tracking-widest text-[8px] hidden lg:block">Auto_Discovery_Active</div>
              <div className="text-[#50fa7b] font-bold flex items-center gap-2 uppercase">
                <Activity size={12} /> {activeModeConfig.label}_Stable
              </div>
            </div>
          </header>

          <div className="p-8 lg:p-12 max-w-7xl mx-auto w-full space-y-10 relative">
            <div className="scanline"></div>

            {activeMode === 'FOUNDRY' && (
              <div className="space-y-6 animate-in fade-in duration-500">
                {activeModeNav === 'SPRITE_REGISTRY' ? (
                  <div className="glass-panel border border-yellow-700/30 overflow-hidden">
                    <div className="p-4 border-b border-zinc-900 flex items-center justify-between">
                      <h2 className="text-yellow-300 uppercase tracking-[0.25em] text-[11px] font-black">Sprite Asset Registry</h2>
                      <button className="px-3 py-1 border border-yellow-500/40 text-yellow-300 text-[9px] uppercase tracking-widest">Register Sprite</button>
                    </div>
                    <div className="divide-y divide-zinc-900">
                      {SPRITE_ASSET_REGISTRY.map((asset) => (
                        <div key={asset.name} className="grid grid-cols-12 px-4 py-3 text-[10px] uppercase tracking-wider">
                          <div className="col-span-5 text-zinc-200">{asset.name}</div>
                          <div className="col-span-2 text-yellow-300">{asset.type}</div>
                          <div className="col-span-2 text-zinc-500">{asset.frames} Frames</div>
                          <div className="col-span-3 text-zinc-500">{asset.size}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
                    <section className="xl:col-span-6 glass-panel border border-yellow-700/30">
                      <div className="p-4 border-b border-zinc-900">
                        <h2 className="text-yellow-300 text-2xl font-black tracking-[0.16em] uppercase">Universal Builder V7</h2>
                        <p className="text-zinc-600 text-[9px] uppercase tracking-[0.2em] mt-1">Allocate Custom Clusters</p>
                      </div>
                      <div className="p-4 space-y-4">
                        <div className="grid grid-cols-2 gap-3">
                          <div className="border border-zinc-800 bg-black px-3 py-2">
                            <div className="text-zinc-600 text-[8px] uppercase">OS Clusters</div>
                            <div className="text-zinc-100 text-sm uppercase tracking-wider mt-1">Fish Shooting</div>
                          </div>
                          <div className="border border-yellow-600/30 bg-yellow-900/10 px-3 py-2">
                            <div className="text-zinc-600 text-[8px] uppercase">Units</div>
                            <div className="text-yellow-300 text-sm uppercase tracking-wider mt-1">1</div>
                          </div>
                        </div>
                        <div className="grid grid-cols-2 gap-3">
                          <div className="border border-zinc-800 bg-black px-3 py-2">
                            <div className="text-zinc-600 text-[8px] uppercase">Generation Mode</div>
                            <div className="text-zinc-100 text-sm uppercase tracking-wider mt-1">Fast Render</div>
                          </div>
                          <div className="border border-yellow-600/30 bg-yellow-900/10 px-3 py-2">
                            <div className="text-zinc-600 text-[8px] uppercase">Night Shift</div>
                            <div className="text-yellow-300 text-sm uppercase tracking-wider mt-1">Batch Queue</div>
                          </div>
                        </div>
                        <button className="w-full py-2 border border-yellow-500 bg-yellow-800/30 text-yellow-200 uppercase text-[10px] tracking-[0.2em] font-black">Forge OS Container</button>
                      </div>
                    </section>
                    <section className="xl:col-span-6 glass-panel border border-yellow-700/30 overflow-hidden">
                      <div className="p-4 border-b border-zinc-900">
                        <h3 className="text-yellow-300 uppercase tracking-[0.2em] text-[11px] font-black">Build Architecture Ledger</h3>
                      </div>
                      <div className="max-h-[420px] overflow-y-auto divide-y divide-zinc-900">
                        {BUILD_ARCHITECTURE_LEDGER.map((entry) => (
                          <div key={entry.id} className="grid grid-cols-12 px-4 py-2 text-[10px] uppercase tracking-wider">
                            <div className="col-span-6 text-zinc-300">{entry.id}</div>
                            <div className="col-span-4 text-zinc-100">{entry.project}</div>
                            <div className="col-span-2 text-cyan-300">{entry.className.replace('_', ' ')}</div>
                          </div>
                        ))}
                      </div>
                    </section>
                  </div>
                )}
              </div>
            )}

            {activeMode === 'VAULT' && (
              <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 animate-in fade-in duration-500">
                <section className="xl:col-span-4 glass-panel border border-red-700/30 p-4 space-y-4">
                  <h2 className="text-red-400 uppercase tracking-[0.2em] text-[11px] font-black">Certification Scan</h2>
                  <div className="space-y-3 text-[10px] uppercase tracking-wider">
                    <div className="border border-zinc-800 px-3 py-2">
                      <div className="text-zinc-600">Target Project</div>
                      <div className="text-zinc-100 mt-1">Neon Fish Hunt</div>
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <button className="border border-red-500/40 py-2 text-red-300">GLI</button>
                      <button className="border border-zinc-700 py-2 text-zinc-500">MGA</button>
                    </div>
                    <button className="w-full border border-red-600 bg-red-900/30 text-red-200 py-2 font-black tracking-[0.2em]">Run Certification Scan</button>
                  </div>
                </section>
                <section className="xl:col-span-8 glass-panel border border-red-700/30 overflow-hidden">
                  <div className="p-4 border-b border-zinc-900">
                    <h3 className="text-red-400 uppercase tracking-[0.2em] text-[11px] font-black">Compliance Reports</h3>
                  </div>
                  <div className="max-h-[420px] overflow-y-auto divide-y divide-zinc-900">
                    {VAULT_COMPLIANCE_REPORTS.map((report) => (
                      <div key={report.id} className="px-4 py-3">
                        <div className="flex justify-between items-center text-[10px] uppercase tracking-wider">
                          <span className="text-zinc-100">{report.id} {report.target}</span>
                          <span className={`${report.status === 'PASS' ? 'text-emerald-400' : report.status === 'CONDITIONAL' ? 'text-yellow-300' : 'text-red-400'}`}>{report.status}</span>
                        </div>
                        <div className="text-zinc-500 text-[9px] uppercase tracking-widest mt-1">Checks: {report.checks}</div>
                      </div>
                    ))}
                  </div>
                </section>
              </div>
            )}

            {activeMode === 'EMPIRE_1' && (
              <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 animate-in fade-in duration-500">
                <aside className="xl:col-span-3 glass-panel border border-indigo-700/30 p-4">
                  <h2 className="text-indigo-300 uppercase tracking-[0.2em] text-[11px] font-black mb-3">Boss Roster (3)</h2>
                  <div className="space-y-2">
                    {EMPIRE_BOSS_ROSTER.map((boss) => (
                      <div key={boss.name} className="border border-zinc-800 p-2">
                        <div className="text-zinc-100 text-[10px] uppercase">{boss.name}</div>
                        <div className="text-indigo-300 text-[9px] uppercase">{boss.tier} · HP {boss.hp}</div>
                      </div>
                    ))}
                  </div>
                </aside>
                <section className="xl:col-span-9 glass-panel border border-indigo-700/30 p-4 space-y-4">
                  <h3 className="text-white text-4xl font-black tracking-[0.12em] uppercase">Xochipilli Scathed</h3>
                  <p className="text-indigo-300 text-[11px] uppercase tracking-[0.2em]">Sun Priest of the Burning Codex · 850,000 HP</p>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-[10px] uppercase tracking-wider">
                    <div className="border border-zinc-800 p-3"><p className="text-zinc-600 mb-2">Attack Kit</p><p className="text-zinc-100">Solar Flare Staff</p><p className="text-zinc-100">Calendra Shield Bash</p></div>
                    <div className="border border-zinc-800 p-3"><p className="text-zinc-600 mb-2">Weakness</p><p className="text-cyan-300">Water / Ice</p><p className="text-yellow-300">Aztec / Mesoamerican</p></div>
                    <div className="border border-zinc-800 p-3"><p className="text-zinc-600 mb-2">Credit Values</p><p className="text-yellow-300 text-lg">3500 / 2400</p><p className="text-zinc-500">RTP 94.2%</p></div>
                  </div>
                </section>
              </div>
            )}

            {/* TAB: UNIVERSAL BUILDER */}
            {!hasDedicatedModeSurface && activeTab === 'Universal_Builder' && (
              <div className="space-y-8 animate-in fade-in duration-500">
                <div className="flex justify-between items-center border-b border-zinc-900 pb-4">
                  <h2 className="text-cyan-400 text-xs tracking-widest uppercase flex items-center gap-2">
                    <Zap size={14} /> ArtTech_Nexus_Generator
                  </h2>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                  {(Object.keys(ENGINE_PRESETS) as OsKey[]).map((os) => (
                    <div key={os} onClick={() => setCurrentOS(os)} className={`os-card p-4 rounded-sm ${currentOS === os ? 'selected' : ''}`}>
                      <h4 className={`text-[10px] uppercase mb-1 ${currentOS === os ? 'text-[#bd93f9]' : 'text-white'}`}>{ENGINE_PRESETS[os].title}</h4>
                      <p className="text-[8px] text-zinc-600 uppercase mt-2 truncate">{ENGINE_PRESETS[os].desc}</p>
                    </div>
                  ))}
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 mt-8">
                  <div className="col-span-12 lg:col-span-5 space-y-6">
                    <div className="glass-panel p-6 border border-zinc-900 space-y-5">
                      <h3 className="text-[9px] text-[#D4AF37] uppercase flex items-center gap-2 border-b border-zinc-900 pb-3">
                        <SlidersHorizontal size={14} /> Matrix_Parameters
                      </h3>
                      <div className="space-y-4 text-[10px]">
                        <div>
                          <label className="text-zinc-500 uppercase block mb-1">Physics_Engine</label>
                          <select className="input-dark py-2" value={sysCore} onChange={e => setSysCore(e.target.value)}>
                            <option value="UE5_CHAOS">Unreal Engine 5 // Chaos</option>
                            <option value="UNITY_DOTS">Unity 6 // DOTS</option>
                            <option value="SLA113_NATIVE">SLA113 Native Custom</option>
                          </select>
                        </div>
                        <div>
                          <label className="text-zinc-500 uppercase block mb-1">Audio_Middleware</label>
                          <select className="input-dark py-2" value={sysAudio} onChange={e => setSysAudio(e.target.value)}>
                            <option value="FMOD_STUDIO">FMOD Studio</option>
                            <option value="WWISE_MASTER">Wwise Master</option>
                          </select>
                        </div>
                        <div>
                          <label className="text-zinc-500 uppercase block mb-1">Render_Pipeline</label>
                          <select className="input-dark py-2" value={sysRender} onChange={e => setSysRender(e.target.value)}>
                            <option value="LUMEN_RTX">Lumen RTX</option>
                            <option value="HDRP_ULTRA">HDRP Ultra</option>
                          </select>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <label className="text-cyan-500 uppercase block mb-1">Biome</label>
                            <select className="input-dark py-2" value={sysBiome} onChange={e => setSysBiome(e.target.value)}>
                              <option value="ABYSSAL_WASTES">Abyssal Wastes</option>
                              <option value="NEON_DISTRICT">Neon District</option>
                            </select>
                          </div>
                          <div>
                            <label className="text-[#ff5555] uppercase block mb-1">Archetype</label>
                            <select className="input-dark py-2" value={sysBoss} onChange={e => setSysBoss(e.target.value)}>
                              <option value="MECHA_DEITY">Mecha Deity</option>
                              <option value="FLESH_TITAN">Flesh Titan</option>
                            </select>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <label className="text-[9px] text-zinc-500 uppercase">Custom_Asset_Modifiers</label>
                      <textarea 
                        value={nexusPrompt} 
                        onChange={(e) => setNexusPrompt(e.target.value)}
                        rows={2} 
                        placeholder="Additional specs..."
                        className="input-dark resize-none rounded-sm"
                      />
                    </div>
                    <button onClick={handleUniversalRender} disabled={isGeneratingNexus} className="w-full py-4 btn-action text-cyan-400 font-bold border-cyan-900/30 flex justify-center items-center gap-2 uppercase">
                      {isGeneratingNexus ? <RefreshCw className="animate-spin" size={16} /> : <Box size={16} />} Compile AAA Asset
                    </button>
                  </div>
                  <div className="col-span-12 lg:col-span-7">
                    <div className="glass-panel h-[500px] flex items-center justify-center relative overflow-hidden rounded-sm border border-zinc-900">
                      {nexusPreview ? <img src={nexusPreview} alt="Render" className="w-full h-full object-contain p-4" /> : <div className="text-zinc-700 uppercase tracking-widest text-[9px]">Awaiting_Compilation</div>}
                    </div>
                  </div>
                </div>

                {/* OS MODULE MATRIX TABLE */}
                <div className="mt-12 glass-panel border border-zinc-900 overflow-hidden">
                  <div className="bg-zinc-900/50 p-4 border-b border-zinc-800">
                    <h3 className="text-[10px] text-white uppercase tracking-[0.2em] flex items-center gap-3 font-black">
                      <Database size={14} className="text-cyan-400" /> OS_Module_Functional_Map
                    </h3>
                  </div>
                  <table className="w-full text-left font-mono text-[10px]">
                    <thead className="bg-black/60 text-zinc-500 uppercase">
                      <tr>
                        <th className="p-4 border-b border-zinc-800">OS Module</th>
                        <th className="p-4 border-b border-zinc-800">FModel Utility</th>
                        <th className="p-4 border-b border-zinc-800">Functional Output</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-zinc-900">
                      {OS_MODULES.map((m, i) => (
                        <tr key={i} className="hover:bg-cyan-900/5 transition-colors">
                          <td className="p-4 text-white font-bold">{m.name}</td>
                          <td className="p-4 text-cyan-400">{m.utility}</td>
                          <td className="p-4 text-zinc-400 italic">{m.output}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* TAB: SPRITE CUTTER */}
            {!hasDedicatedModeSurface && activeTab === 'Sprite_Cutter' && (
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 animate-in fade-in duration-500">
                <aside className="lg:col-span-3 space-y-6">
                  <div className="glass-panel p-4 border border-zinc-900">
                    <h3 className="text-[9px] text-[#bd93f9] uppercase mb-4 flex items-center gap-2">
                      <Box size={12} /> Visual_Assets_A
                    </h3>
                    <div className="space-y-2">
                      {["fish_boss_01.png", "g_shield_gold.png", "target_reticle.png"].map(asset => (
                        <div key={asset} onClick={() => setSelectedSprite(asset)} className={`p-3 text-[10px] cursor-pointer border ${selectedSprite === asset ? 'border-cyan-500 bg-cyan-900/10 text-cyan-400' : 'border-zinc-900 hover:bg-zinc-900/50'}`}>
                          {asset}
                        </div>
                      ))}
                    </div>
                  </div>
                </aside>
                <section className="lg:col-span-6 bg-[#010204] border border-zinc-900 relative min-h-[500px] flex items-center justify-center overflow-hidden">
                  <div className="absolute inset-0 opacity-10 pointer-events-none" style={{ backgroundImage: 'radial-gradient(circle, #333 1px, transparent 1px)', backgroundSize: '20px 20px' }}></div>
                  <div className="relative">
                    <img src={`/assets/${selectedSprite}`} alt="Cutter Stage" className="max-w-[400px] border border-dashed border-zinc-700" 
                         onError={(e: any) => e.target.src='https://placehold.co/400x400/050505/ffffff?text='+selectedSprite} />
                    <div className="hitbox-overlay" style={{ top: `${hitbox.y}%`, left: `${hitbox.x}%`, width: `${hitbox.w}%`, height: `${hitbox.h}%` }}></div>
                  </div>
                </section>
                <aside className="lg:col-span-3 space-y-6 text-[10px]">
                  <div className="glass-panel p-6 border border-zinc-900 space-y-4">
                    <h3 className="text-[9px] text-[#D4AF37] uppercase mb-4 flex items-center gap-2">
                      <SlidersHorizontal size={12} /> Hitbox_Logic
                    </h3>
                    <div className="space-y-3">
                      {Object.entries(hitbox).map(([k, v]) => (
                        <div key={k} className="flex justify-between items-center">
                          <span className="text-zinc-500 uppercase">{k}_OFFSET</span>
                          <input 
                            type="number" 
                            value={v} 
                            onChange={(e) => setHitbox({...hitbox, [k]: parseInt(e.target.value) || 0})}
                            className="bg-black border border-zinc-800 w-16 px-2 py-1 outline-none text-cyan-400" 
                          />
                        </div>
                      ))}
                    </div>
                    <button className="w-full py-3 btn-action text-[#50fa7b] border-[#50fa7b]/20 flex items-center justify-center gap-2 mt-4 uppercase font-black tracking-widest">
                      <Save size={12} /> Save_Manifest
                    </button>
                    <button className="w-full py-3 btn-action text-zinc-500 border-zinc-800 flex items-center justify-center gap-2 mt-2 uppercase text-[8px]">
                      <Play size={10} /> Preview_Extract
                    </button>
                  </div>
                </aside>
              </div>
            )}

            {/* TAB: SOUTHERN FOUNDRY */}
            {!hasDedicatedModeSurface && activeTab === 'Southern_Foundry' && ( auditState && (
              <div className="space-y-8 animate-in fade-in duration-500">
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                  <div className="lg:col-span-8 grid grid-cols-2 md:grid-cols-3 gap-6">
                    {[...(auditState.module_a_assets || []), ...(auditState.module_s_assets || [])].map((asset: any, i: number) => (
                      <div key={i} className="glass-panel p-4 border border-zinc-900 group">
                        <div className="aspect-square bg-black border border-zinc-800 mb-4 flex items-center justify-center overflow-hidden relative">
                          <img src={`/assets/${asset.file}`} alt="Audit" className="max-w-[80%] max-h-[80%] object-contain" 
                               onError={(e: any) => e.target.src='https://placehold.co/200x200/050505/ffffff?text='+asset.file} />
                          <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                            <Box size={12} className="text-zinc-600" />
                          </div>
                        </div>
                        <div className="flex justify-between text-[9px]">
                          <span className="text-white truncate font-bold">{asset.file}</span>
                          <span className="text-[#D4AF37] uppercase font-black">{asset.type}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="lg:col-span-4 space-y-6">
                    <div className="glass-panel p-8 border border-zinc-900">
                      <h3 className="text-xs text-white uppercase mb-6 flex items-center gap-2 font-black tracking-widest">
                        <Shield className="text-cyan-400" size={16} /> Production_Audit
                      </h3>
                      <div className="space-y-4 mb-10">
                        <div className="flex justify-between items-end border-b border-zinc-900 pb-2">
                          <span className="text-[10px] text-zinc-500 uppercase">Live_Gems</span>
                          <span className="text-xl text-[#D4AF37] font-bold">{auditState.gems?.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between items-end border-b border-zinc-900 pb-2">
                          <span className="text-[10px] text-zinc-500 uppercase">System_Load</span>
                          <span className="text-xl text-cyan-400 font-bold">{auditState.total_units} / 100</span>
                        </div>
                      </div>
                      <div className="flex gap-4">
                        <button onClick={() => handleAuditAction('reject')} className="flex-1 py-4 border border-red-900/30 bg-red-900/5 text-red-500 text-[10px] font-bold uppercase hover:bg-red-900/10 transition-all flex items-center justify-center gap-2">
                          <XCircle size={14} /> Purge
                        </button>
                        <button onClick={() => handleAuditAction('approve')} className="flex-1 py-4 border border-cyan-900/30 bg-cyan-900/10 text-cyan-400 text-[10px] font-bold uppercase hover:bg-cyan-900/20 transition-all flex items-center justify-center gap-2">
                          <CheckCircle2 size={14} /> Commit
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </main>
      </div>
    </>
  );
}
