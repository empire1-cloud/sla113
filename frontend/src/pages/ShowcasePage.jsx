import React, { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import axios from 'axios';
import {
  Rocket, ExternalLink, Cpu, Layers, Sparkles, Crown, Gamepad2,
  Music, Palette, Network, ArrowRight, Zap, ChevronRight, Github, Mail, Activity
} from 'lucide-react';

const BASE = process.env.REACT_APP_BACKEND_URL || '';
const API = BASE + '/api';

const PILLARS_FALLBACK = [
  { id: 'empire1', name: 'Empire 1', tag: 'Control Plane', icon: Cpu, color: '#3b82ff', desc: 'Hybrid Intelligence Core orchestrating 15+ specialized AI engines.', status: 'live', deeplink: '/' },
  { id: 'ecosystem', name: 'Empire-Lyrica', tag: 'Integration Layer', icon: Network, color: '#ff2d92', desc: 'Cross-app glue. Shared auth, billing, agent runtime.', status: 'linked', deeplink: null },
  { id: 'lyrica', name: 'Lyrica 3 Pro', tag: 'Sonic IP', icon: Music, color: '#00c8ff', desc: 'Music, lyrics, audio generation pillar.', status: 'linked', deeplink: null },
  { id: 'cultura', name: 'Cultura Vibe Forge', tag: 'Cultural IP', icon: Palette, color: '#ff4488', desc: 'Aztec, Chicano, SGV, IELA aesthetic engine.', status: 'linked', deeplink: null },
  { id: 'sla113', name: 'SLA113', tag: 'Arcade OS', icon: Gamepad2, color: '#4488ff', desc: 'Sovereign game compiler + public arcade portal.', status: 'live', deeplink: '/sla113' },
];

const ICON_BY_ID = { empire1: Cpu, ecosystem: Network, lyrica: Music, cultura: Palette, sla113: Gamepad2 };

const SESSION_ID = (() => {
  try {
    let s = sessionStorage.getItem('sla_showcase_sid');
    if (!s) { s = 'sid_' + Date.now().toString(36) + Math.random().toString(36).slice(2, 8); sessionStorage.setItem('sla_showcase_sid', s); }
    return s;
  } catch (_) { return 'sid_anon'; }
})();

const track = (type, meta = {}) => {
  try {
    axios.post(API + '/empire1/analytics/event', {
      type, meta,
      session_id: SESSION_ID,
      referrer: document.referrer || null,
      ua: navigator.userAgent || null,
    }).catch(() => {});
  } catch (_) {}
};

const TIERS = [
  { tier: 'I', name: 'Methodology License', price: '$5–25K /yr', color: '#3b82ff', desc: 'The Emergent DNA framework codified — templates, checklists, decision trees, 4hr video, workbooks, quarterly office hours.', target: 'Founders · Engineering teams', cta: 'License the DNA' },
  { tier: 'II', name: 'Architecture Consulting', price: '$5–15K /project', color: '#00c8ff', desc: '3-week engagement. Discovery → Blueprint → Implementation guide. Apply the DNA to your specific problem.', target: 'PMF startups scaling 1x → 10x', cta: 'Book a Sprint' },
  { tier: 'III', name: 'Done-For-You Systems', price: '$50–250K', color: '#ff4488', desc: '8–12 weeks. We design, spec, and launch your entire platform using Emergent DNA — architecture, design systems, MVP launchpad.', target: 'Series B+ teams moving fast', cta: 'Spec Your Build' },
  { tier: 'IV', name: 'Platform Licensing', price: '25% rev share', color: '#ff2d92', desc: 'White-label our system templates — clarity-creator, hybrid-ai-core, saas-oversight. Passive revenue cut on $1M+ systems.', target: 'Enterprises white-labeling AI', cta: 'Partner Up' },
];

const FEATURES = [
  { icon: Layers, title: 'Sprite to Game in <30s', desc: 'Pick lobby template, deploy live HTML5 in one click. Proof the DNA scales.' },
  { icon: Cpu, title: 'Hybrid Multi-Model Orchestration', desc: 'Router auto-selects best model (Gemini, Claude, GPT) per task. Canon enforcer + drift monitor.' },
  { icon: Sparkles, title: 'Cultural Asset Pipeline', desc: 'Vision Smith (Gemini 3 Pro), Sprite Registry, CORS-safe CDN injection — structural, not surface.' },
  { icon: Crown, title: 'Pick-Mix-Deploy Composer', desc: 'Mix bosses, backgrounds, jackpot tiers — each lobby compiles to its own playable URL.' },
];

const STACK_GROUPS = [
  { label: 'Routing', items: ['Multi-model dispatcher', 'Cost-aware selection', 'Fallback chains'] },
  { label: 'Reasoning', items: ['Strategy Engine', 'Plan Builder', 'Canon Enforcer'] },
  { label: 'Generation', items: ['Vision Smith / Gemini 3', 'Audio Forge / Vertex', 'Composer Engine'] },
  { label: 'Operations', items: ['Drift Monitor', 'Error Handler', 'Execution Logger'] },
];

function StatCell({ label, value, c }) {
  const style = { color: c, textShadow: '0 0 20px ' + c + '55', fontFamily: '"Orbitron",sans-serif' };
  return (
    <div className="bg-[#040010] p-5 md:p-6 text-center">
      <div className="text-2xl md:text-4xl font-black tabular-nums" style={style}>{value}</div>
      <div className="text-[9px] uppercase tracking-[3px] text-zinc-500 mt-1">{label}</div>
    </div>
  );
}

function TierCard({ t }) {
  const cardStyle = { borderColor: t.color + '44' };
  const accentStyle = { color: t.color };
  const numStyle = { color: t.color, textShadow: '0 0 20px ' + t.color + '66', fontFamily: '"Cinzel",serif' };
  const ctaStyle = { borderColor: t.color, color: t.color, background: t.color + '12' };
  return (
    <div className="relative p-6 border bg-black/40 backdrop-blur-sm transition-all hover:scale-[1.02]" style={cardStyle} data-testid={'tier-' + t.tier}>
      <div className="absolute top-0 right-0 px-2 py-0.5 text-[9px] font-black tracking-widest" style={ctaStyle}>TIER {t.tier}</div>
      <div className="text-5xl font-black mb-2 mt-2" style={numStyle}>{t.tier}</div>
      <div className="text-[9px] uppercase tracking-[4px] text-zinc-500 mb-1">{t.target}</div>
      <h3 className="text-lg font-black uppercase tracking-wider mb-2" style={accentStyle}>{t.name}</h3>
      <div className="text-2xl font-black mb-3" style={{ fontFamily: '"Orbitron",sans-serif' }}>{t.price}</div>
      <p className="text-[12px] text-zinc-400 leading-relaxed mb-4">{t.desc}</p>
      <a href="mailto:founder@empire1cloud.com" className="inline-flex items-center gap-1 text-[10px] uppercase tracking-widest font-bold px-3 py-1.5 border transition-all hover:scale-105" style={ctaStyle}>
        {t.cta} <ArrowRight size={10}/>
      </a>
    </div>
  );
}

function PillarCard({ p }) {
  const Icon = p.icon;
  const cls = 'group relative p-6 border bg-black/40 backdrop-blur-sm transition-all overflow-hidden ' + (p.deeplink ? 'cursor-pointer hover:scale-[1.02]' : 'cursor-default');
  const style = { borderColor: p.color + '44' };
  const overlayStyle = { background: 'radial-gradient(ellipse at top right, ' + p.color + '22, transparent 70%)' };
  const iconBoxStyle = { borderColor: p.color, background: p.color + '15', boxShadow: '0 0 20px ' + p.color + '33' };
  const liveColor = p.status === 'live' ? '#44ff44' : '#888';
  const liveBorder = p.status === 'live' ? '#44ff4477' : '#88888844';
  const statusStyle = { borderColor: liveBorder, color: liveColor };
  const titleStyle = { color: p.color, fontFamily: '"Cinzel",serif' };
  const linkStyle = { color: p.color };
  const iconStyle = { color: p.color };
  const inner = (
    <>
      <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity" style={overlayStyle}/>
      <div className="relative">
        <div className="flex items-start justify-between mb-4">
          <div className="w-11 h-11 flex items-center justify-center border" style={iconBoxStyle}>
            <Icon size={18} style={iconStyle}/>
          </div>
          <span className="text-[9px] uppercase tracking-[3px] px-2 py-0.5 border" style={statusStyle}>
            {p.status === 'live' ? '● LIVE' : '○ LINKED'}
          </span>
        </div>
        <div className="text-[9px] uppercase tracking-[4px] text-zinc-500 mb-1">{p.tag}</div>
        <h3 className="text-xl font-black uppercase tracking-wider mb-2" style={titleStyle}>{p.name}</h3>
        <p className="text-[12px] text-zinc-400 leading-relaxed">{p.desc}</p>
        {p.deeplink ? (
          <div className="mt-4 inline-flex items-center gap-1 text-[10px] uppercase tracking-widest font-bold opacity-60 group-hover:opacity-100" style={linkStyle}>
            Enter <ChevronRight size={11} className="group-hover:translate-x-0.5 transition-transform"/>
          </div>
        ) : null}
      </div>
    </>
  );
  if (p.deeplink) {
    return <a href={p.deeplink} className={cls} style={style} data-testid={'pillar-' + p.id}>{inner}</a>;
  }
  return <div className={cls} style={style} data-testid={'pillar-' + p.id}>{inner}</div>;
}

function FeatureCard({ f, idx }) {
  const Icon = f.icon;
  return (
    <div className="p-6 border border-zinc-800 bg-black/30 hover:border-[#3b82ff66] transition-all" data-testid={'feature-' + idx}>
      <div className="flex items-start gap-4">
        <div className="w-10 h-10 flex items-center justify-center bg-[#3b82ff12] border border-[#3b82ff44] shrink-0">
          <Icon size={16} className="text-[#3b82ff]"/>
        </div>
        <div className="flex-1">
          <h3 className="text-base font-bold uppercase tracking-wider mb-1">{f.title}</h3>
          <p className="text-[12px] text-zinc-400 leading-relaxed">{f.desc}</p>
        </div>
      </div>
    </div>
  );
}

function StackItem({ text }) {
  return <li className="flex items-start gap-1.5"><span className="text-[#3b82ff] mt-1">·</span>{text}</li>;
}

function StackGroup({ g }) {
  const items = g.items;
  return (
    <div>
      <div className="text-[9px] uppercase tracking-[3px] text-[#3b82ff] mb-2 pb-2 border-b border-[#3b82ff22]">{g.label}</div>
      <ul className="space-y-1.5 text-zinc-400">
        {items.map(it => <StackItem key={it} text={it}/>)}
      </ul>
    </div>
  );
}

export default function ShowcasePage() {
  const [stats, setStats] = useState({ LOBBIES: 0, SPRITES: 0 });
  const [demoUrl, setDemoUrl] = useState(null);
  const [demoBusy, setDemoBusy] = useState(false);
  const [lobbies, setLobbies] = useState([]);
  const [pillars, setPillars] = useState(PILLARS_FALLBACK);
  const iframeRef = useRef(null);

  const demoLobby = useMemo(() => lobbies.find(l => l.slug === 'shadow_pack') || lobbies[0] || null, [lobbies]);

  const loadStats = useCallback(async () => {
    try {
      const lRes = await axios.get(API + '/sla113/lobbies');
      const sRes = await axios.get(API + '/sla113/sprites');
      const eRes = await axios.get(API + '/empire1/ecosystem').catch(() => ({ data: { repos: [] } }));
      const lobs = lRes.data.lobbies || [];
      const sprs = sRes.data.sprites || [];
      const repos = eRes.data.repos || [];
      setLobbies(lobs);
      setStats({ LOBBIES: lobs.length, SPRITES: sprs.length });
      if (repos.length) {
        setPillars(repos.map(r => ({ ...r, icon: ICON_BY_ID[r.id] || Cpu })));
      }
    } catch (e) { console.error(e); }
  }, []);
  useEffect(() => { loadStats(); }, [loadStats]);

  // Track page view once
  useEffect(() => { track('view', { page: 'showcase' }); }, []);

  // Track scroll depth at thresholds 25/50/75/100
  useEffect(() => {
    const sent = new Set();
    const onScroll = () => {
      const h = document.documentElement;
      const pct = Math.round(((h.scrollTop + window.innerHeight) / h.scrollHeight) * 100);
      [25, 50, 75, 100].forEach(t => { if (pct >= t && !sent.has(t)) { sent.add(t); track('scroll_depth', { depth: t }); } });
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const runDemo = useCallback(async () => {
    if (!demoLobby) return;
    track('demo_run', { lobby: demoLobby.name });
    setDemoBusy(true);
    setDemoUrl(null);
    try {
      const res = await axios.post(API + '/sla113/lobbies/' + demoLobby.id + '/deploy');
      setDemoUrl(BASE + res.data.preview_url);
      setTimeout(() => { if (iframeRef.current) iframeRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' }); }, 200);
    } catch (e) { alert('Demo failed: ' + (e?.response?.data?.detail || e.message)); }
    setDemoBusy(false);
  }, [demoLobby]);

  const trackCta = (target) => track('cta_click', { target });

  const heroBgStyle = { background: 'radial-gradient(ellipse at top, rgba(212,175,55,0.12) 0%, transparent 50%), radial-gradient(ellipse at bottom right, rgba(153,68,255,0.08) 0%, transparent 50%), radial-gradient(ellipse at bottom left, rgba(0,200,255,0.06) 0%, transparent 50%)' };
  const gridLineStyle = { backgroundImage: 'repeating-linear-gradient(0deg, transparent, transparent 2px, #fff 2px, #fff 3px)' };
  const heroH1Style = { fontFamily: '"Cinzel",serif', fontSize: 'clamp(48px, 9vw, 110px)' };
  const heroLine1Style = { textShadow: '0 0 60px rgba(212,175,55,0.3)' };
  const heroLine2Style = { backgroundImage: 'linear-gradient(135deg, #67aaff 0%, #3b82ff 40%, #9944ff 100%)' };
  const heroPStyle = { fontFamily: '"Rajdhani",sans-serif' };
  const brandSpanStyle = { fontFamily: '"Dancing Script",cursive' };
  const sectionTitleStyle = { fontFamily: '"Cinzel",serif' };

  const showDemoSection = demoBusy || demoUrl;

  return (
    <div className="min-h-screen bg-[#040010] text-white overflow-x-hidden" style={{ fontFamily: "'Rajdhani','Orbitron',monospace" }} data-testid="showcase-page">
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute inset-0" style={heroBgStyle}/>
        <div className="absolute inset-0 opacity-[0.03]" style={gridLineStyle}/>
      </div>

      <header className="sticky top-0 z-40 backdrop-blur-xl bg-[#040010]/85 border-b border-[#3b82ff22]" data-testid="showcase-header">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-[#3b82ff] via-[#1a4dd4] to-[#0a1a4d] flex items-center justify-center shadow-[0_0_30px_rgba(59,130,255,0.5)]">
              <Sparkles size={16} className="text-black"/>
            </div>
            <div>
              <div className="text-[8px] uppercase tracking-[5px] text-zinc-500">empire1cloud</div>
              <div className="font-black text-sm tracking-[3px]" style={sectionTitleStyle}>SHOWCASE</div>
            </div>
          </div>
          <div className="flex items-center gap-2 text-[10px] uppercase tracking-widest">
            <span className="hidden md:inline-flex items-center gap-1.5 text-emerald-400"><span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"/>Live</span>
            <span className="hidden md:inline text-zinc-700">·</span>
            <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="text-zinc-500 hover:text-zinc-200 inline-flex items-center gap-1.5"><Github size={11}/> Org</a>
          </div>
        </div>
      </header>

      <section className="relative z-10 max-w-6xl mx-auto px-6 pt-20 pb-12 md:pt-32 md:pb-20 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 border border-[#3b82ff44] bg-[#3b82ff10] mb-8 text-[10px] uppercase tracking-[4px] text-[#3b82ff]">
          <Zap size={10}/> A16z Speedrun · TC Battlefield · 2026
        </div>
        <h1 className="font-black uppercase mb-6 leading-[0.95]" style={heroH1Style}>
          <span className="block text-white" style={heroLine1Style}>We Don't Build Features.</span>
          <span className="block bg-clip-text text-transparent" style={heroLine2Style}>We Architect Empires.</span>
        </h1>
        <p className="text-zinc-300 text-base md:text-xl max-w-3xl mx-auto mb-4 leading-relaxed" style={heroPStyle}>
          <span className="text-[#67aaff] italic" style={brandSpanStyle}>Empire1Cloud</span> sells <span className="text-white font-bold">structural engineering for software</span> — not prompts, not scripts. The Emergent DNA framework turns AI chaos into clarity at enterprise scale.
        </p>
        <p className="text-zinc-500 text-sm md:text-base max-w-2xl mx-auto mb-10">One stack · Five universes · Four monetization tiers · Live and shipping.</p>
        <div className="flex flex-wrap gap-3 justify-center">
          <button onClick={runDemo} disabled={demoBusy || !demoLobby} className="group inline-flex items-center gap-3 px-7 py-4 bg-gradient-to-r from-[#3b82ff] to-[#1a4dd4] text-black font-black uppercase tracking-[3px] text-xs disabled:opacity-50 hover:scale-[1.03] transition-all shadow-[0_0_40px_rgba(212,175,55,0.4)]" data-testid="showcase-run-demo">
            {demoBusy ? <><Activity size={14} className="animate-pulse"/> Compiling Live…</> : <><Rocket size={14}/> See The DNA Run Live<ArrowRight size={14} className="group-hover:translate-x-1 transition-transform"/></>}
          </button>
          <a href="#tiers" onClick={() => trackCta('tiers_hero')} className="inline-flex items-center gap-2 px-6 py-4 border border-[#ff2d9266] text-[#ff2d92] hover:bg-[#ff2d9212] uppercase tracking-[3px] text-xs font-bold transition-all" data-testid="showcase-tiers-link">
            <Crown size={13}/> View Tiers
          </a>
          <a href="/sla113" onClick={() => trackCta('sla113_console')} className="inline-flex items-center gap-2 px-6 py-4 border border-zinc-700 text-zinc-300 hover:border-zinc-400 hover:text-white uppercase tracking-[3px] text-xs font-bold transition-all" data-testid="showcase-admin-link">
            <Cpu size={13}/> SLA113 Console
          </a>
        </div>
      </section>

      <section className="relative z-10 max-w-6xl mx-auto px-6 mb-16 md:mb-24" data-testid="showcase-stats">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-px bg-[#3b82ff22] border border-[#3b82ff22]">
          <StatCell label="Lobbies Live" value={stats.LOBBIES} c="#3b82ff"/>
          <StatCell label="Sprites Registered" value={stats.SPRITES} c="#9944ff"/>
          <StatCell label="AI Engines" value="15+" c="#00c8ff"/>
          <StatCell label="Compile Time" value="<30s" c="#44ff44"/>
          <StatCell label="Universes" value="5" c="#ff4488"/>
        </div>
      </section>

      {showDemoSection ? (
        <section ref={iframeRef} className="relative z-10 max-w-6xl mx-auto px-6 mb-16 md:mb-24" data-testid="showcase-demo-stage">
          <div className="flex items-center justify-between mb-4">
            <div>
              <div className="text-[10px] uppercase tracking-[4px] text-emerald-400">● Live Compilation</div>
              <h2 className="text-2xl font-black mt-1" style={sectionTitleStyle}>
                {demoLobby ? demoLobby.name : 'Loading…'}
              </h2>
            </div>
            {demoUrl ? (
              <a href={demoUrl} target="_blank" rel="noopener noreferrer" className="text-[10px] uppercase tracking-widest text-[#3b82ff] inline-flex items-center gap-1 hover:underline" data-testid="showcase-open-demo">
                <ExternalLink size={11}/> Open Standalone
              </a>
            ) : null}
          </div>
          <div className="border border-[#3b82ff44] bg-black relative aspect-video shadow-[0_0_60px_rgba(212,175,55,0.2)]">
            {demoBusy && !demoUrl ? (
              <div className="absolute inset-0 flex flex-col items-center justify-center gap-4">
                <div className="w-12 h-12 border-2 border-[#3b82ff33] border-t-[#3b82ff] rounded-full animate-spin"/>
                <div className="text-[10px] uppercase tracking-[5px] text-[#3b82ff]">Hybrid Core → Build → Deploy</div>
              </div>
            ) : null}
            {demoUrl ? <iframe src={demoUrl} title="demo" className="w-full h-full border-0" allow="autoplay; fullscreen" data-testid="showcase-demo-iframe"/> : null}
          </div>
        </section>
      ) : null}

      <section id="tiers" className="relative z-10 max-w-6xl mx-auto px-6 mb-16 md:mb-24" data-testid="showcase-tiers">
        <div className="text-center mb-10">
          <div className="text-[10px] uppercase tracking-[6px] text-zinc-500 mb-3">The Offer Ladder</div>
          <h2 className="text-3xl md:text-5xl font-black uppercase" style={sectionTitleStyle}>Four Tiers · One Empire</h2>
          <p className="text-zinc-500 text-sm md:text-base mt-3 max-w-2xl mx-auto">From self-serve license to white-label revenue share. Pick the entry point that matches your scale.</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          {TIERS.map(t => <TierCard key={t.tier} t={t}/>)}
        </div>
        <div className="mt-10 grid grid-cols-3 gap-px bg-[#3b82ff22] border border-[#3b82ff22]" data-testid="showcase-trajectory">
          <div className="bg-[#040010] p-5 md:p-6 text-center">
            <div className="text-[9px] uppercase tracking-[3px] text-zinc-500 mb-1">Year 1 Target</div>
            <div className="text-2xl md:text-3xl font-black" style={{ color: '#3b82ff', fontFamily: '"Orbitron",sans-serif' }}>$270K</div>
            <div className="text-[9px] text-zinc-600 mt-1">Tier I + II + 1× Tier III</div>
          </div>
          <div className="bg-[#040010] p-5 md:p-6 text-center">
            <div className="text-[9px] uppercase tracking-[3px] text-zinc-500 mb-1">Year 2 Target</div>
            <div className="text-2xl md:text-3xl font-black" style={{ color: '#00c8ff', fontFamily: '"Orbitron",sans-serif' }}>$2M</div>
            <div className="text-[9px] text-zinc-600 mt-1">Scaled consulting + Tier IV rev-share</div>
          </div>
          <div className="bg-[#040010] p-5 md:p-6 text-center">
            <div className="text-[9px] uppercase tracking-[3px] text-zinc-500 mb-1">Year 3+ Target</div>
            <div className="text-2xl md:text-3xl font-black" style={{ color: '#ff2d92', fontFamily: '"Orbitron",sans-serif' }}>$5M+</div>
            <div className="text-[9px] text-zinc-600 mt-1">Emergent Architects · 10-person firm</div>
          </div>
        </div>
      </section>

      <section className="relative z-10 max-w-6xl mx-auto px-6 mb-16 md:mb-24" data-testid="showcase-pillars">
        <div className="text-center mb-10">
          <div className="text-[10px] uppercase tracking-[6px] text-zinc-500 mb-3">The DNA In Production</div>
          <h2 className="text-3xl md:text-5xl font-black uppercase" style={sectionTitleStyle}>Five Universes · One Brain</h2>
          <p className="text-zinc-500 text-sm md:text-base mt-3 max-w-2xl mx-auto">Every universe runs on the same Emergent DNA framework. Five live proofs that the architecture scales across domains.</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {pillars.map(p => <PillarCard key={p.id} p={p}/>)}
        </div>
      </section>

      <section className="relative z-10 max-w-6xl mx-auto px-6 mb-16 md:mb-24" data-testid="showcase-features">
        <div className="text-center mb-10">
          <div className="text-[10px] uppercase tracking-[6px] text-zinc-500 mb-3">The Edge</div>
          <h2 className="text-3xl md:text-5xl font-black uppercase" style={sectionTitleStyle}>What It Actually Ships</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {FEATURES.map((f, i) => <FeatureCard key={f.title} f={f} idx={i}/>)}
        </div>
      </section>

      <section className="relative z-10 max-w-6xl mx-auto px-6 mb-16 md:mb-24" data-testid="showcase-stack">
        <div className="border border-[#3b82ff44] bg-black/40 p-6 md:p-10">
          <div className="text-[10px] uppercase tracking-[6px] text-zinc-500 mb-2">Under the Hood</div>
          <h3 className="text-2xl md:text-3xl font-black mb-6" style={sectionTitleStyle}>Hybrid Intelligence Architecture</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-[11px]">
            {STACK_GROUPS.map(g => <StackGroup key={g.label} g={g}/>)}
          </div>
        </div>
      </section>

      <section className="relative z-10 max-w-4xl mx-auto px-6 pb-20 text-center">
        <div className="text-[10px] uppercase tracking-[6px] text-[#ff2d92] mb-3">The Moat</div>
        <h3 className="text-2xl md:text-4xl font-black mb-4" style={sectionTitleStyle}>
          The DNA Is The Empire.
        </h3>
        <p className="text-zinc-400 mb-8 text-sm md:text-base max-w-2xl mx-auto">Once you own the framework, you own the market for systems architecture at scale. Every link on this page is a working surface — not a mockup.</p>
        <div className="flex flex-wrap gap-3 justify-center">
          <button onClick={runDemo} disabled={demoBusy || !demoLobby} className="px-6 py-3 bg-[#3b82ff] text-white font-black uppercase tracking-widest text-xs disabled:opacity-50 hover:bg-[#67aaff] transition-all" data-testid="showcase-cta-demo">
            {demoBusy ? 'Compiling…' : 'Spawn Game'}
          </button>
          <a href="#tiers" className="px-6 py-3 bg-[#ff2d92] text-white font-black uppercase tracking-widest text-xs hover:bg-[#ff4488] transition-all" data-testid="showcase-cta-tiers">
            Pick Your Tier
          </a>
          <a href="mailto:founder@empire1cloud.com" className="px-6 py-3 border border-zinc-700 hover:border-[#3b82ff] text-zinc-300 hover:text-[#3b82ff] uppercase tracking-widest text-xs font-bold transition-all inline-flex items-center gap-2" data-testid="showcase-contact">
            <Mail size={12}/> Founder Contact
          </a>
        </div>
        <div className="mt-16 pt-8 border-t border-zinc-900 text-[9px] uppercase tracking-[4px] text-zinc-600">
          Empire1Cloud · Crafted from SGV · IELA roots · © 2026
        </div>
      </section>
    </div>
  );
}
