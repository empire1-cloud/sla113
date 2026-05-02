import React, { useState, useEffect, useRef } from 'react';
import { Zap, Cpu, HardDrive, Clock, Globe, Activity, Users, Package, Shield, DollarSign } from 'lucide-react';

const FrontlinePanel = ({ API, projects, stats }) => {
  const [metrics, setMetrics] = useState(null);
  const [feed, setFeed] = useState([]);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef(null);
  const feedRef = useRef(null);

  useEffect(() => {
    // Construct WS URL from API
    const wsBase = API.replace('/api/sla113', '').replace('https://', 'wss://').replace('http://', 'ws://');
    const wsUrl = `${wsBase}/api/sla113/frontline/ws`;

    const connect = () => {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setConnected(true);
        addFeedEntry('LINK_UP', 'WebSocket connected. Frontline active.');
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'frontline_update') {
            const prev = metrics;
            setMetrics(data.metrics);

            // Generate contextual feed entries from metric changes
            if (prev) {
              if (data.metrics.active_jobs > prev.active_jobs) addFeedEntry('QUEUE', `${data.metrics.active_jobs - prev.active_jobs} new job(s) entered Night Queue.`);
              if (data.metrics.completed_jobs > prev.completed_jobs) addFeedEntry('DONE', `Job completed. Total: ${data.metrics.completed_jobs}`);
              if (data.metrics.active_builds > prev.active_builds) addFeedEntry('BUILD', `Build pipeline active. ${data.metrics.active_builds} in progress.`);
              if (data.metrics.live_deployments > prev.live_deployments) addFeedEntry('DEPLOY', `New deployment live. Total: ${data.metrics.live_deployments}`);
              if (data.metrics.total_revenue > prev.total_revenue) addFeedEntry('REVENUE', `Revenue pulse: +$${data.metrics.total_revenue - prev.total_revenue}`);
            }
          }
        } catch (e) { /* ignore parse errors */ }
      };

      ws.onclose = () => {
        setConnected(false);
        addFeedEntry('LINK_DOWN', 'WebSocket disconnected. Reconnecting...');
        setTimeout(connect, 3000);
      };

      ws.onerror = () => ws.close();
    };

    connect();
    return () => { if (wsRef.current) wsRef.current.close(); };
  }, [API]);

  // Auto-scroll feed
  useEffect(() => {
    if (feedRef.current) feedRef.current.scrollTop = feedRef.current.scrollHeight;
  }, [feed]);

  const addFeedEntry = (type, message) => {
    const time = new Date().toLocaleTimeString('en-US', { hour12: false });
    setFeed(prev => [...prev.slice(-50), { time, type, message }]);
  };

  // Keep a reference for the metrics closure in the ws callback
  const metricsRef = useRef(metrics);
  useEffect(() => { metricsRef.current = metrics; }, [metrics]);

  const m = metrics || {};

  const feedColors = {
    LINK_UP: 'text-emerald-400', LINK_DOWN: 'text-red-400', QUEUE: 'text-cyan-400',
    DONE: 'text-emerald-400', BUILD: 'text-amber-400', DEPLOY: 'text-indigo-400',
    REVENUE: 'text-[#D4AF37]', INFO: 'text-zinc-400',
  };

  const MetricCard = ({ icon: Icon, label, value, color = 'cyan', pulse = false }) => (
    <div className={`bg-black/50 border border-${color}-500/20 p-4 space-y-2`}>
      <div className="flex items-center gap-2">
        <Icon size={12} className={`text-${color}-500`} />
        <span className="text-[8px] text-zinc-600 uppercase tracking-widest">{label}</span>
      </div>
      <span className={`text-lg font-bold text-${color}-400 ${pulse ? 'animate-pulse' : ''}`} data-testid={`frontline-${label.toLowerCase().replace(/\s/g, '-')}`}>{value}</span>
    </div>
  );

  return (
    <div className="grid grid-cols-12 gap-6 h-full animate-in fade-in" data-testid="frontline-panel">
      {/* Live Feed */}
      <div className="col-span-8 flex flex-col gap-4">
        <div className="flex-1 glass-panel border-cyan-500/20 flex flex-col min-h-0">
          <div className="p-4 border-b border-cyan-500/20 bg-cyan-900/10 flex justify-between items-center text-[10px] uppercase tracking-widest shrink-0">
            <span className="flex items-center gap-2 text-cyan-400"><Zap size={12} fill="currentColor" /> Live Frontline Feed</span>
            <div className="flex items-center gap-3">
              <span className={`flex items-center gap-1 ${connected ? 'text-emerald-400' : 'text-red-400'}`}>
                <span className={`w-1.5 h-1.5 rounded-full ${connected ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'}`}></span>
                {connected ? 'LINKED' : 'OFFLINE'}
              </span>
              <span className="text-zinc-600">{m.universes_online || 0} universes online</span>
            </div>
          </div>
          <div ref={feedRef} className="flex-1 p-4 font-mono text-[10px] space-y-1.5 overflow-y-auto custom-scrollbar">
            {feed.length === 0 && (
              <p className="text-zinc-700 italic">Awaiting real-time data stream...</p>
            )}
            {feed.map((entry, i) => (
              <p key={i} className={feedColors[entry.type] || 'text-zinc-400'}>
                <span className="text-zinc-600">[{entry.time}]</span>{' '}
                <span className="text-zinc-500 font-bold">{entry.type}</span>{' '}
                {entry.message}
              </p>
            ))}
            {projects.slice(0, 5).map((p, i) => (
              <p key={`proj-${i}`} className="text-zinc-500">
                <span className="text-zinc-700">[ACTIVE]</span> {p.name} | {p.game_type} | {p.status}
              </p>
            ))}
          </div>
        </div>
      </div>

      {/* Metrics Sidebar */}
      <div className="col-span-4 space-y-4">
        {/* Sovereign Gauge */}
        <div className="glass-panel border-cyan-500/20 p-6">
          <h3 className="text-cyan-400 text-[9px] font-bold uppercase tracking-[3px] border-b border-cyan-500/20 pb-3 mb-4">Sovereign Pulse</h3>
          <div className="flex justify-center py-4">
            <div className="w-28 h-28 rounded-full bg-cyan-500/5 border border-cyan-500/30 flex items-center justify-center relative shadow-[0_0_40px_rgba(0,200,255,0.1)]">
              <div className={`w-20 h-20 rounded-full border-2 border-t-cyan-400 border-r-transparent border-b-transparent border-l-transparent ${connected ? 'animate-spin' : ''}`} style={{ animationDuration: '3s' }} />
              <div className="absolute flex flex-col items-center">
                <span className="text-cyan-400 font-bold text-lg" data-testid="frontline-cpu">{m.cpu_percent || '—'}%</span>
                <span className="text-[7px] text-zinc-500 uppercase tracking-widest">CPU</span>
              </div>
            </div>
          </div>
        </div>

        {/* Metric Grid */}
        <div className="grid grid-cols-2 gap-2">
          <MetricCard icon={Package} label="Projects" value={m.total_projects || 0} color="cyan" />
          <MetricCard icon={Activity} label="Active Jobs" value={m.active_jobs || 0} color="cyan" pulse={m.active_jobs > 0} />
          <MetricCard icon={Shield} label="Blocked" value={m.blocked_jobs || 0} color="red" />
          <MetricCard icon={Package} label="Completed" value={m.completed_jobs || 0} color="emerald" />
          <MetricCard icon={Users} label="Tenants" value={m.total_tenants || 0} color="indigo" />
          <MetricCard icon={Globe} label="Universes" value={m.universes_online || 0} color="amber" />
          <MetricCard icon={HardDrive} label="RAM" value={`${m.ram_gb || '—'} GB`} color="zinc" />
          <MetricCard icon={DollarSign} label="Revenue" value={`$${m.total_revenue || 0}`} color="amber" pulse={true} />
        </div>

        {/* Worker Status */}
        <div className="glass-panel border-cyan-500/10 p-4">
          <div className="flex justify-between text-[9px] uppercase tracking-widest">
            <span className="text-zinc-500">Worker</span>
            <span className={m.worker_running ? 'text-emerald-400' : 'text-red-400'}>{m.worker_running ? 'RUNNING' : 'STOPPED'}</span>
          </div>
          <div className="flex justify-between text-[9px] uppercase tracking-widest mt-1">
            <span className="text-zinc-500">Uptime</span>
            <span className="text-zinc-400">{m.uptime_hours || '—'}h</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FrontlinePanel;
