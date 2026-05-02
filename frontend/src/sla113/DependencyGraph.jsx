import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Link2, Unlink, ZoomIn, ZoomOut, RotateCcw } from 'lucide-react';

const STATUS_COLORS = {
  completed: { fill: '#10b981', stroke: '#059669', text: '#d1fae5' },
  processing: { fill: '#06b6d4', stroke: '#0891b2', text: '#cffafe' },
  pending: { fill: '#71717a', stroke: '#52525b', text: '#e4e4e7' },
  blocked: { fill: '#f59e0b', stroke: '#d97706', text: '#fef3c7' },
  failed: { fill: '#ef4444', stroke: '#dc2626', text: '#fecaca' },
};

export default function DependencyGraph({ nodes, edges, onLink, onUnlink }) {
  const svgRef = useRef(null);
  const containerRef = useRef(null);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [dragging, setDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [linking, setLinking] = useState(null); // source node id for new link
  const [hoveredNode, setHoveredNode] = useState(null);

  // Layout: position nodes in columns by dependency depth
  const layout = useCallback(() => {
    if (!nodes.length) return { positioned: [], w: 0, h: 0 };

    // Calculate depth for each node
    const depthMap = {};
    const visited = new Set();

    const calcDepth = (nodeId, depth = 0) => {
      if (visited.has(nodeId)) return;
      visited.add(nodeId);
      depthMap[nodeId] = Math.max(depthMap[nodeId] || 0, depth);
      const node = nodes.find(n => n.id === nodeId);
      if (node) {
        (node.dependents || []).forEach(dId => calcDepth(dId, depth + 1));
      }
    };

    // Find root nodes (no dependencies)
    const roots = nodes.filter(n => !n.depends_on || n.depends_on.length === 0);
    roots.forEach(r => calcDepth(r.id, 0));
    // Handle orphans
    nodes.forEach(n => { if (!(n.id in depthMap)) depthMap[n.id] = 0; });

    // Group by depth
    const columns = {};
    nodes.forEach(n => {
      const d = depthMap[n.id] || 0;
      if (!columns[d]) columns[d] = [];
      columns[d].push(n);
    });

    const nodeW = 160;
    const nodeH = 56;
    const colGap = 220;
    const rowGap = 76;
    const padX = 40;
    const padY = 40;

    const positioned = [];
    const maxCols = Math.max(...Object.keys(columns).map(Number), 0);

    Object.entries(columns).forEach(([depth, colNodes]) => {
      const d = Number(depth);
      colNodes.forEach((n, i) => {
        positioned.push({
          ...n,
          x: padX + d * colGap,
          y: padY + i * rowGap,
          w: nodeW,
          h: nodeH,
        });
      });
    });

    const totalW = padX * 2 + (maxCols + 1) * colGap;
    const maxRows = Math.max(...Object.values(columns).map(c => c.length), 0);
    const totalH = padY * 2 + maxRows * rowGap;

    return { positioned, w: totalW, h: totalH };
  }, [nodes]);

  const { positioned, w: svgW, h: svgH } = layout();

  const getNodeCenter = (nodeId) => {
    const n = positioned.find(p => p.id === nodeId);
    if (!n) return null;
    return { x: n.x + n.w / 2, y: n.y + n.h / 2 };
  };

  const handleMouseDown = (e) => {
    if (e.target === svgRef.current || e.target.tagName === 'line' || e.target.tagName === 'polygon') {
      setDragging(true);
      setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
    }
  };

  const handleMouseMove = (e) => {
    if (dragging) {
      setPan({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y });
    }
  };

  const handleMouseUp = () => setDragging(false);

  const handleNodeClick = (nodeId) => {
    if (linking) {
      if (linking !== nodeId) {
        onLink?.(nodeId, linking); // nodeId depends on linking
      }
      setLinking(null);
    }
  };

  if (!nodes.length) {
    return (
      <div className="flex items-center justify-center h-full text-zinc-600 text-[10px] uppercase tracking-widest">
        No jobs to graph. Queue jobs to see dependencies.
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full" data-testid="dependency-graph">
      {/* Toolbar */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-zinc-800 bg-[#0a0a0a] shrink-0">
        <div className="flex items-center gap-2">
          <span className="text-red-500 text-[9px] font-bold uppercase tracking-[2px]">Dependency Graph</span>
          <span className="text-zinc-600 text-[8px]">{nodes.length} nodes, {edges.length} edges</span>
        </div>
        <div className="flex items-center gap-2">
          {linking && (
            <span className="text-amber-500 text-[9px] uppercase tracking-widest animate-pulse mr-2">
              Click target node...
            </span>
          )}
          <button
            onClick={() => setLinking(linking ? null : '__start__')}
            className={`px-3 py-1.5 text-[9px] uppercase tracking-widest border flex items-center gap-1 transition-all ${
              linking ? 'border-amber-500 bg-amber-500/10 text-amber-400' : 'border-zinc-800 text-zinc-500 hover:text-zinc-300'
            }`}
            data-testid="start-link-btn"
          >
            <Link2 size={10} /> {linking ? 'Cancel' : 'Link'}
          </button>
          <button onClick={() => setZoom(z => Math.min(2, z + 0.2))} className="p-1.5 border border-zinc-800 text-zinc-500 hover:text-white"><ZoomIn size={12}/></button>
          <button onClick={() => setZoom(z => Math.max(0.3, z - 0.2))} className="p-1.5 border border-zinc-800 text-zinc-500 hover:text-white"><ZoomOut size={12}/></button>
          <button onClick={() => { setZoom(1); setPan({ x: 0, y: 0 }); }} className="p-1.5 border border-zinc-800 text-zinc-500 hover:text-white"><RotateCcw size={12}/></button>
        </div>
      </div>

      {/* Canvas */}
      <div
        ref={containerRef}
        className="flex-1 overflow-hidden bg-[#080808] cursor-grab active:cursor-grabbing"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        <svg
          ref={svgRef}
          width="100%"
          height="100%"
          viewBox={`0 0 ${Math.max(svgW, 800)} ${Math.max(svgH, 400)}`}
          style={{ transform: `scale(${zoom}) translate(${pan.x / zoom}px, ${pan.y / zoom}px)` }}
          className="transition-transform"
        >
          <defs>
            <marker id="arrowhead" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
              <polygon points="0 0, 8 3, 0 6" fill="#D4AF37" opacity="0.6" />
            </marker>
            <marker id="arrowhead-active" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
              <polygon points="0 0, 8 3, 0 6" fill="#06b6d4" />
            </marker>
          </defs>

          {/* Grid background */}
          <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1a1a1a" strokeWidth="0.5" />
          </pattern>
          <rect width="100%" height="100%" fill="url(#grid)" />

          {/* Edges */}
          {edges.map((e, i) => {
            const from = getNodeCenter(e.from);
            const to = getNodeCenter(e.to);
            if (!from || !to) return null;
            const isHovered = hoveredNode === e.from || hoveredNode === e.to;
            return (
              <line
                key={i}
                x1={from.x + 80} y1={from.y}
                x2={to.x - 80} y2={to.y}
                stroke={isHovered ? '#06b6d4' : '#D4AF37'}
                strokeWidth={isHovered ? 2 : 1}
                strokeDasharray={isHovered ? '' : '4 4'}
                opacity={isHovered ? 1 : 0.4}
                markerEnd={isHovered ? 'url(#arrowhead-active)' : 'url(#arrowhead)'}
              />
            );
          })}

          {/* Nodes */}
          {positioned.map(n => {
            const colors = STATUS_COLORS[n.status] || STATUS_COLORS.pending;
            const isHovered = hoveredNode === n.id;
            const isLinkSource = linking === n.id;
            return (
              <g
                key={n.id}
                transform={`translate(${n.x}, ${n.y})`}
                onMouseEnter={() => setHoveredNode(n.id)}
                onMouseLeave={() => setHoveredNode(null)}
                onClick={() => handleNodeClick(n.id)}
                style={{ cursor: linking ? 'crosshair' : 'pointer' }}
                data-testid={`graph-node-${n.id}`}
              >
                {/* Shadow */}
                <rect x="2" y="2" width={n.w} height={n.h} rx="2" fill="black" opacity="0.5" />
                {/* Node body */}
                <rect
                  width={n.w} height={n.h} rx="2"
                  fill="#0a0a0a"
                  stroke={isLinkSource ? '#f59e0b' : isHovered ? colors.stroke : '#333'}
                  strokeWidth={isHovered || isLinkSource ? 2 : 1}
                />
                {/* Progress bar */}
                <rect x="0" y={n.h - 4} width={n.w * (n.progress / 100)} height="4" fill={colors.fill} rx="0" opacity="0.8" />
                {/* ID */}
                <text x="10" y="18" fill={colors.text} fontSize="10" fontFamily="monospace" fontWeight="bold">{n.id}</text>
                {/* Preset */}
                <text x="10" y="32" fill="#71717a" fontSize="8" fontFamily="monospace">{n.preset}</text>
                {/* Status badge */}
                <text x={n.w - 10} y="18" fill={colors.fill} fontSize="8" fontFamily="monospace" textAnchor="end" fontWeight="bold">{n.status.toUpperCase()}</text>
                {/* Progress */}
                <text x={n.w - 10} y="32" fill="#52525b" fontSize="8" fontFamily="monospace" textAnchor="end">{n.progress}%</text>
                {/* Dependency indicators */}
                {(n.depends_on?.length > 0) && (
                  <circle cx="-6" cy={n.h / 2} r="4" fill="#D4AF37" opacity="0.6" />
                )}
                {(n.dependents?.length > 0) && (
                  <circle cx={n.w + 6} cy={n.h / 2} r="4" fill="#06b6d4" opacity="0.6" />
                )}
                {/* Link source mode indicator */}
                {linking && linking !== n.id && linking !== '__start__' && (
                  <rect width={n.w} height={n.h} rx="2" fill="rgba(245,158,11,0.1)" stroke="#f59e0b" strokeWidth="1" strokeDasharray="4 2" />
                )}
              </g>
            );
          })}
        </svg>
      </div>

      {/* Legend */}
      <div className="flex items-center gap-6 px-4 py-2 border-t border-zinc-800 bg-[#0a0a0a] text-[8px] uppercase tracking-widest">
        {Object.entries(STATUS_COLORS).map(([status, colors]) => (
          <div key={status} className="flex items-center gap-1.5">
            <div className="w-2 h-2" style={{ backgroundColor: colors.fill }} />
            <span style={{ color: colors.text }}>{status}</span>
          </div>
        ))}
        <div className="flex items-center gap-1.5 ml-4">
          <div className="w-2 h-2 rounded-full bg-[#D4AF37]" />
          <span className="text-zinc-500">Has parent</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-2 h-2 rounded-full bg-cyan-500" />
          <span className="text-zinc-500">Has children</span>
        </div>
      </div>
    </div>
  );
}
