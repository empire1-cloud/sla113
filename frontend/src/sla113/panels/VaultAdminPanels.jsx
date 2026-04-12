import React from 'react';
import {
  Grid3X3, Code, SlidersHorizontal, Cpu, Music, Server, Globe, Shield
} from 'lucide-react';

export const ArtTechNexusPanel = ({ nexusPipelines, osModules }) => (
  <div className="animate-in fade-in max-w-7xl mx-auto w-full space-y-6" data-testid="arttech-nexus-panel">
    <div className="flex items-center justify-between">
      <span className="text-red-500 text-[10px] font-bold uppercase tracking-[3px] flex items-center gap-2"><Grid3X3 size={14}/> ArtTech Nexus Generator</span>
      <span className="text-[8px] text-zinc-600 uppercase tracking-widest">Pipeline Archetypes</span>
    </div>
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {nexusPipelines.map(p => (
        <div key={p.id} className="glass-panel border-red-500/20 p-5 space-y-3 hover:scale-[1.02] transition-all group" data-testid={`nexus-pipeline-${p.id}`}>
          <div className="flex justify-between items-start">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: p.color }} />
            <span className={`px-1.5 py-0.5 text-[7px] uppercase tracking-widest border font-bold ${p.status === 'active' ? 'border-emerald-500/30 text-emerald-500 bg-emerald-500/10' : 'border-zinc-700 text-zinc-500'}`}>{p.status}</span>
          </div>
          <h4 className="text-zinc-200 text-xs font-bold tracking-wider">{p.name}</h4>
          <div className="flex flex-wrap gap-1">
            {p.tags.map(tag => (
              <span key={tag} className="px-1.5 py-0.5 text-[7px] uppercase tracking-widest border border-zinc-800 text-zinc-500 bg-black/50">{tag}</span>
            ))}
          </div>
        </div>
      ))}
    </div>
    <div className="mt-6">
      <span className="text-red-500 text-[10px] font-bold uppercase tracking-[3px] flex items-center gap-2 mb-4"><Code size={14}/> OS Module Functional Map</span>
      <div className="glass-panel border-red-500/20 overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-red-500/5 border-b border-red-500/20 text-[9px] uppercase tracking-widest text-zinc-500 font-normal">
            <tr><th className="p-4">OS Module</th><th className="p-4">FModel Utility</th><th className="p-4">Functional Output</th></tr>
          </thead>
          <tbody className="text-[10px] font-mono">
            {osModules.map((m, i) => (
              <tr key={i} className="border-b border-zinc-900/50 hover:bg-white/5 transition-all">
                <td className="p-4 text-red-400 font-bold uppercase tracking-wider">{m.os_module}</td>
                <td className="p-4 text-zinc-400">{m.fmodel_utility}</td>
                <td className="p-4 text-zinc-300 text-[9px]">{m.functional_output}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  </div>
);

export const MatrixParamsPanel = ({ matrixParams }) => (
  <div className="animate-in fade-in max-w-7xl mx-auto w-full space-y-6" data-testid="matrix-params-panel">
    <div className="flex items-center justify-between">
      <span className="text-red-500 text-[10px] font-bold uppercase tracking-[3px] flex items-center gap-2"><SlidersHorizontal size={14}/> Matrix Parameters</span>
      <span className="text-[8px] text-zinc-600 uppercase tracking-widest">Engine Config for AAA Compilation</span>
    </div>
    {matrixParams ? (
      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-7 space-y-4">
          <span className="text-[9px] text-zinc-500 uppercase tracking-widest">Active Engine Parameters</span>
          <div className="grid grid-cols-1 gap-3">
            {Object.entries(matrixParams.parameters || {}).map(([key, param]) => (
              <div key={key} className="glass-panel border-red-500/20 p-5 flex items-center justify-between group hover:border-red-500/40 transition-all" data-testid={`matrix-param-${key}`}>
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 border border-red-500/20 bg-red-500/5 flex items-center justify-center">
                    {param.icon === 'cpu' && <Cpu size={16} className="text-red-400"/>}
                    {param.icon === 'volume-2' && <Music size={16} className="text-red-400"/>}
                    {param.icon === 'monitor' && <Server size={16} className="text-red-400"/>}
                    {param.icon === 'globe' && <Globe size={16} className="text-red-400"/>}
                    {param.icon === 'shield' && <Shield size={16} className="text-red-400"/>}
                  </div>
                  <div>
                    <h4 className="text-zinc-200 text-xs font-bold tracking-wider uppercase">{key.replace(/_/g, ' ')}</h4>
                    <p className="text-[#D4AF37] text-[10px] font-mono mt-0.5">{param.value}</p>
                  </div>
                </div>
                <span className={`px-2 py-0.5 text-[7px] uppercase tracking-widest border font-bold ${param.status === 'active' ? 'border-emerald-500/30 text-emerald-500 bg-emerald-500/10' : 'border-zinc-700 text-zinc-500'}`}>{param.status}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="col-span-5 space-y-4">
          <span className="text-[9px] text-zinc-500 uppercase tracking-widest">FModel Utility Status</span>
          <div className="glass-panel border-red-500/20 p-6 space-y-4 tech-border-red">
            {Object.entries(matrixParams.fmodel_utility || {}).map(([key, val]) => (
              <div key={key} className="flex justify-between items-center py-2 border-b border-zinc-900/50 last:border-0">
                <span className="text-[9px] text-zinc-500 uppercase tracking-widest">{key.replace(/_/g, ' ')}</span>
                <span className={`text-[10px] font-bold uppercase tracking-wider ${
                  val === 'ACTIVE' || val === 'READY' || val === 'STABLE' ? 'text-emerald-400' :
                  val === 'ADMIN_OVERRIDE' ? 'text-[#D4AF37]' : 'text-zinc-300'
                }`}>{val}</span>
              </div>
            ))}
          </div>
          <div className="glass-panel border-red-500/20 p-6 space-y-3">
            <h4 className="text-red-400 text-[9px] font-bold uppercase tracking-[3px]">Compilation Readiness</h4>
            <div className="h-3 bg-black border border-zinc-800 overflow-hidden">
              <div className="h-full bg-gradient-to-r from-red-600 via-[#D4AF37] to-emerald-500 w-full" />
            </div>
            <div className="flex justify-between text-[8px] text-zinc-500 uppercase tracking-widest">
              <span>Physics</span><span>Audio</span><span>Render</span><span>Biome</span><span>Archetype</span>
            </div>
          </div>
        </div>
      </div>
    ) : (
      <div className="glass-panel border-red-500/10 p-16 text-center">
        <SlidersHorizontal size={32} className="text-zinc-700 mx-auto mb-4"/>
        <p className="text-zinc-600 text-[10px] uppercase tracking-widest">Loading matrix parameters...</p>
      </div>
    )}
  </div>
);
