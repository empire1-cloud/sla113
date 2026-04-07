import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Grid3X3, Download, Scissors, ZoomIn, ZoomOut, RotateCcw, Move, Crosshair } from 'lucide-react';

const GRID_COLOR = 'rgba(212, 175, 55, 0.7)';
const GRID_COLOR_HOVER = 'rgba(212, 175, 55, 1)';
const SELECTION_COLOR = 'rgba(0, 200, 255, 0.3)';
const SELECTION_BORDER = 'rgba(0, 200, 255, 0.9)';

export default function SpriteCutter({ imageBase64, onClose }) {
  const canvasRef = useRef(null);
  const overlayRef = useRef(null);
  const containerRef = useRef(null);
  const imgRef = useRef(null);

  const [rows, setRows] = useState(4);
  const [cols, setCols] = useState(4);
  const [showGrid, setShowGrid] = useState(true);
  const [cutSprites, setCutSprites] = useState([]);
  const [isCutting, setIsCutting] = useState(false);
  const [hoveredCell, setHoveredCell] = useState(null);
  const [selectedCells, setSelectedCells] = useState(new Set());
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imgDimensions, setImgDimensions] = useState({ w: 0, h: 0 });
  const [mode, setMode] = useState('grid'); // 'grid' or 'freehand'
  const [zoom, setZoom] = useState(1);

  // Load image
  useEffect(() => {
    if (!imageBase64) return;
    const img = new Image();
    img.onload = () => {
      imgRef.current = img;
      setImgDimensions({ w: img.width, h: img.height });
      setImageLoaded(true);
    };
    img.src = `data:image/png;base64,${imageBase64}`;
  }, [imageBase64]);

  // Draw canvas
  const drawCanvas = useCallback(() => {
    const canvas = canvasRef.current;
    const overlay = overlayRef.current;
    const img = imgRef.current;
    if (!canvas || !overlay || !img || !imageLoaded) return;

    const container = containerRef.current;
    const maxW = container ? container.clientWidth : 600;
    const maxH = 500;

    const scale = Math.min(maxW / img.width, maxH / img.height) * zoom;
    const cw = Math.floor(img.width * scale);
    const ch = Math.floor(img.height * scale);

    canvas.width = cw;
    canvas.height = ch;
    overlay.width = cw;
    overlay.height = ch;

    // Draw image
    const ctx = canvas.getContext('2d');
    ctx.imageSmoothingEnabled = true;
    ctx.drawImage(img, 0, 0, cw, ch);

    // Draw grid overlay
    const octx = overlay.getContext('2d');
    octx.clearRect(0, 0, cw, ch);

    if (showGrid) {
      const cellW = cw / cols;
      const cellH = ch / rows;

      // Draw selected cells
      selectedCells.forEach(key => {
        const [r, c] = key.split('-').map(Number);
        octx.fillStyle = SELECTION_COLOR;
        octx.fillRect(c * cellW, r * cellH, cellW, cellH);
        octx.strokeStyle = SELECTION_BORDER;
        octx.lineWidth = 2;
        octx.strokeRect(c * cellW, r * cellH, cellW, cellH);
      });

      // Draw hovered cell
      if (hoveredCell) {
        const [r, c] = hoveredCell;
        octx.fillStyle = 'rgba(212, 175, 55, 0.15)';
        octx.fillRect(c * cellW, r * cellH, cellW, cellH);
      }

      // Draw grid lines
      octx.strokeStyle = GRID_COLOR;
      octx.lineWidth = 1;
      octx.setLineDash([4, 4]);

      for (let i = 1; i < cols; i++) {
        const x = Math.floor(i * cellW);
        octx.beginPath();
        octx.moveTo(x, 0);
        octx.lineTo(x, ch);
        octx.stroke();
      }
      for (let i = 1; i < rows; i++) {
        const y = Math.floor(i * cellH);
        octx.beginPath();
        octx.moveTo(0, y);
        octx.lineTo(cw, y);
        octx.stroke();
      }
      octx.setLineDash([]);

      // Cell labels
      octx.font = '9px monospace';
      octx.fillStyle = 'rgba(212, 175, 55, 0.5)';
      for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
          octx.fillText(`${r},${c}`, c * cellW + 4, r * cellH + 12);
        }
      }
    }
  }, [imageLoaded, rows, cols, showGrid, hoveredCell, selectedCells, zoom]);

  useEffect(() => { drawCanvas(); }, [drawCanvas]);

  // Mouse handlers for overlay
  const getCellFromEvent = (e) => {
    const rect = overlayRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const cellW = rect.width / cols;
    const cellH = rect.height / rows;
    const c = Math.floor(x / cellW);
    const r = Math.floor(y / cellH);
    if (r >= 0 && r < rows && c >= 0 && c < cols) return [r, c];
    return null;
  };

  const handleMouseMove = (e) => {
    const cell = getCellFromEvent(e);
    setHoveredCell(cell);
  };

  const handleClick = (e) => {
    const cell = getCellFromEvent(e);
    if (!cell) return;
    const key = `${cell[0]}-${cell[1]}`;
    setSelectedCells(prev => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

  const selectAll = () => {
    const all = new Set();
    for (let r = 0; r < rows; r++)
      for (let c = 0; c < cols; c++)
        all.add(`${r}-${c}`);
    setSelectedCells(all);
  };

  const selectNone = () => setSelectedCells(new Set());

  // Cut sprites
  const handleCut = async () => {
    if (!imgRef.current) return;
    setIsCutting(true);

    const img = imgRef.current;
    const cellW = img.width / cols;
    const cellH = img.height / rows;
    const targets = selectedCells.size > 0 ? [...selectedCells] : [];

    // If none selected, cut all
    if (targets.length === 0) {
      for (let r = 0; r < rows; r++)
        for (let c = 0; c < cols; c++)
          targets.push(`${r}-${c}`);
    }

    const sprites = [];
    for (const key of targets) {
      const [r, c] = key.split('-').map(Number);
      const offscreen = document.createElement('canvas');
      offscreen.width = Math.floor(cellW);
      offscreen.height = Math.floor(cellH);
      const ctx = offscreen.getContext('2d');
      ctx.drawImage(img, c * cellW, r * cellH, cellW, cellH, 0, 0, cellW, cellH);
      const dataUrl = offscreen.toDataURL('image/png');
      sprites.push({
        id: `sprite_${r}_${c}`,
        row: r,
        col: c,
        dataUrl,
        width: Math.floor(cellW),
        height: Math.floor(cellH),
      });
    }

    setCutSprites(sprites);
    setIsCutting(false);
  };

  const downloadSprite = (sprite) => {
    const a = document.createElement('a');
    a.href = sprite.dataUrl;
    a.download = `${sprite.id}.png`;
    a.click();
  };

  const downloadAll = () => {
    cutSprites.forEach((sprite, i) => {
      setTimeout(() => downloadSprite(sprite), i * 100);
    });
  };

  if (!imageBase64) return null;

  return (
    <div className="fixed inset-0 z-[200] bg-black/95 backdrop-blur-xl flex flex-col" data-testid="sprite-cutter-modal">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-3 border-b border-[#D4AF37]/30 bg-[#050505] shrink-0">
        <div className="flex items-center gap-3">
          <Scissors size={16} className="text-[#D4AF37]" />
          <span className="text-[#D4AF37] text-xs font-bold uppercase tracking-[4px]">Sprite Cutter</span>
          <span className="text-zinc-500 text-[9px] uppercase tracking-widest ml-4">
            {imgDimensions.w}x{imgDimensions.h}px | {rows}x{cols} grid = {rows * cols} cells
          </span>
        </div>
        <button
          onClick={onClose}
          className="text-zinc-500 hover:text-white text-xs uppercase tracking-widest border border-zinc-800 px-4 py-2 hover:border-zinc-600 transition-all"
          data-testid="sprite-cutter-close"
        >
          Close
        </button>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Controls Sidebar */}
        <div className="w-64 border-r border-zinc-800 bg-[#0a0a0a] p-5 flex flex-col gap-5 shrink-0 overflow-y-auto">
          {/* Grid Controls */}
          <div className="space-y-4">
            <h4 className="text-[#D4AF37] text-[10px] font-bold uppercase tracking-[3px] border-b border-[#D4AF37]/20 pb-2">
              Grid Config
            </h4>
            <div className="space-y-3">
              <div>
                <label className="text-[9px] text-zinc-500 uppercase tracking-widest block mb-1">Rows</label>
                <div className="flex items-center gap-2">
                  <button onClick={() => setRows(Math.max(1, rows - 1))} className="w-8 h-8 border border-zinc-800 bg-black text-zinc-400 hover:text-white hover:border-zinc-600 flex items-center justify-center text-sm">-</button>
                  <input
                    type="number" min="1" max="32" value={rows}
                    onChange={e => setRows(Math.max(1, Math.min(32, parseInt(e.target.value) || 1)))}
                    className="flex-1 bg-black border border-zinc-800 text-center text-[#D4AF37] font-bold text-sm py-1.5 focus:outline-none focus:border-[#D4AF37]/50"
                    data-testid="sprite-rows-input"
                  />
                  <button onClick={() => setRows(Math.min(32, rows + 1))} className="w-8 h-8 border border-zinc-800 bg-black text-zinc-400 hover:text-white hover:border-zinc-600 flex items-center justify-center text-sm">+</button>
                </div>
              </div>
              <div>
                <label className="text-[9px] text-zinc-500 uppercase tracking-widest block mb-1">Columns</label>
                <div className="flex items-center gap-2">
                  <button onClick={() => setCols(Math.max(1, cols - 1))} className="w-8 h-8 border border-zinc-800 bg-black text-zinc-400 hover:text-white hover:border-zinc-600 flex items-center justify-center text-sm">-</button>
                  <input
                    type="number" min="1" max="32" value={cols}
                    onChange={e => setCols(Math.max(1, Math.min(32, parseInt(e.target.value) || 1)))}
                    className="flex-1 bg-black border border-zinc-800 text-center text-[#D4AF37] font-bold text-sm py-1.5 focus:outline-none focus:border-[#D4AF37]/50"
                    data-testid="sprite-cols-input"
                  />
                  <button onClick={() => setCols(Math.min(32, cols + 1))} className="w-8 h-8 border border-zinc-800 bg-black text-zinc-400 hover:text-white hover:border-zinc-600 flex items-center justify-center text-sm">+</button>
                </div>
              </div>
            </div>

            {/* Quick presets */}
            <div>
              <label className="text-[9px] text-zinc-500 uppercase tracking-widest block mb-2">Presets</label>
              <div className="grid grid-cols-3 gap-1">
                {[[2,2],[4,4],[8,8],[2,4],[4,8],[1,4]].map(([r,c]) => (
                  <button
                    key={`${r}x${c}`}
                    onClick={() => { setRows(r); setCols(c); }}
                    className={`py-1.5 text-[9px] border transition-all ${rows === r && cols === c ? 'border-[#D4AF37] bg-[#D4AF37]/10 text-[#D4AF37]' : 'border-zinc-800 text-zinc-500 hover:text-zinc-300'}`}
                  >
                    {r}x{c}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* View Controls */}
          <div className="space-y-3">
            <h4 className="text-[#D4AF37] text-[10px] font-bold uppercase tracking-[3px] border-b border-[#D4AF37]/20 pb-2">
              View
            </h4>
            <div className="flex items-center justify-between">
              <span className="text-[9px] text-zinc-500 uppercase tracking-widest">Grid Overlay</span>
              <button
                onClick={() => setShowGrid(!showGrid)}
                className={`w-10 h-5 border transition-all relative ${showGrid ? 'border-[#D4AF37] bg-[#D4AF37]/10' : 'border-zinc-800 bg-black'}`}
                data-testid="grid-toggle"
              >
                <div className={`absolute top-[2px] w-3 h-3 transition-all ${showGrid ? 'right-1 bg-[#D4AF37]' : 'left-1 bg-zinc-700'}`} />
              </button>
            </div>
            <div className="flex items-center gap-2">
              <button onClick={() => setZoom(z => Math.max(0.25, z - 0.25))} className="flex-1 py-1.5 border border-zinc-800 text-zinc-500 hover:text-white flex items-center justify-center gap-1 text-[9px]">
                <ZoomOut size={12} /> Out
              </button>
              <span className="text-[10px] text-[#D4AF37] font-bold w-12 text-center">{Math.round(zoom * 100)}%</span>
              <button onClick={() => setZoom(z => Math.min(3, z + 0.25))} className="flex-1 py-1.5 border border-zinc-800 text-zinc-500 hover:text-white flex items-center justify-center gap-1 text-[9px]">
                <ZoomIn size={12} /> In
              </button>
            </div>
            <button onClick={() => setZoom(1)} className="w-full py-1.5 border border-zinc-800 text-zinc-500 hover:text-white text-[9px] flex items-center justify-center gap-1">
              <RotateCcw size={10} /> Reset Zoom
            </button>
          </div>

          {/* Selection */}
          <div className="space-y-3">
            <h4 className="text-[#D4AF37] text-[10px] font-bold uppercase tracking-[3px] border-b border-[#D4AF37]/20 pb-2">
              Selection ({selectedCells.size}/{rows * cols})
            </h4>
            <div className="flex gap-2">
              <button onClick={selectAll} className="flex-1 py-1.5 border border-zinc-800 text-zinc-400 hover:text-white text-[9px] uppercase tracking-widest">All</button>
              <button onClick={selectNone} className="flex-1 py-1.5 border border-zinc-800 text-zinc-400 hover:text-white text-[9px] uppercase tracking-widest">None</button>
            </div>
            <p className="text-[8px] text-zinc-600 leading-relaxed">Click cells on canvas to select. Selected cells will be cut. If none selected, all cells are cut.</p>
          </div>

          {/* Cut Action */}
          <div className="mt-auto space-y-3">
            <button
              onClick={handleCut}
              disabled={isCutting}
              className={`w-full py-3 font-bold tracking-[3px] uppercase text-[10px] border transition-all ${
                isCutting ? 'border-zinc-800 text-zinc-700 bg-black' : 'border-[#D4AF37] text-black bg-[#D4AF37] hover:bg-[#F3E5AB]'
              }`}
              data-testid="cut-sprites-btn"
            >
              {isCutting ? 'Cutting...' : `Cut ${selectedCells.size > 0 ? selectedCells.size : rows * cols} Sprites`}
            </button>
            {cutSprites.length > 0 && (
              <button
                onClick={downloadAll}
                className="w-full py-2.5 border border-cyan-500/50 bg-cyan-500/10 text-cyan-400 font-bold uppercase text-[9px] tracking-widest hover:bg-cyan-500 hover:text-black transition-all"
                data-testid="download-all-sprites"
              >
                <Download size={12} className="inline mr-2" />
                Download All ({cutSprites.length})
              </button>
            )}
          </div>
        </div>

        {/* Canvas Area */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <div ref={containerRef} className="flex-1 overflow-auto p-6 flex items-start justify-center bg-[#080808]" data-testid="sprite-canvas-area">
            {imageLoaded ? (
              <div className="relative inline-block" style={{ cursor: showGrid ? 'crosshair' : 'default' }}>
                <canvas ref={canvasRef} className="block" style={{ imageRendering: zoom >= 2 ? 'pixelated' : 'auto' }} />
                <canvas
                  ref={overlayRef}
                  className="absolute top-0 left-0"
                  onMouseMove={handleMouseMove}
                  onMouseLeave={() => setHoveredCell(null)}
                  onClick={handleClick}
                  data-testid="sprite-overlay-canvas"
                />
              </div>
            ) : (
              <div className="flex items-center justify-center h-full text-zinc-600 text-[10px] uppercase tracking-widest">
                Loading image...
              </div>
            )}
          </div>

          {/* Cut Results */}
          {cutSprites.length > 0 && (
            <div className="border-t border-[#D4AF37]/20 bg-[#0a0a0a] p-4 max-h-[240px] overflow-y-auto" data-testid="cut-sprites-output">
              <div className="flex items-center justify-between mb-3">
                <span className="text-[#D4AF37] text-[10px] font-bold uppercase tracking-[3px]">
                  Cut Output — {cutSprites.length} sprites ({cutSprites[0]?.width}x{cutSprites[0]?.height}px each)
                </span>
                <button onClick={() => setCutSprites([])} className="text-zinc-600 hover:text-zinc-300 text-[9px] uppercase tracking-widest">Clear</button>
              </div>
              <div className="flex gap-2 flex-wrap">
                {cutSprites.map(sprite => (
                  <div
                    key={sprite.id}
                    className="group relative border border-zinc-800 bg-black hover:border-[#D4AF37]/50 transition-all cursor-pointer"
                    onClick={() => downloadSprite(sprite)}
                    title={`${sprite.id} — Click to download`}
                    data-testid={`cut-sprite-${sprite.id}`}
                  >
                    <img
                      src={sprite.dataUrl}
                      alt={sprite.id}
                      className="block"
                      style={{ width: Math.min(80, sprite.width), height: Math.min(80, sprite.height), objectFit: 'contain', imageRendering: sprite.width < 100 ? 'pixelated' : 'auto' }}
                    />
                    <div className="absolute inset-0 bg-black/70 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                      <Download size={14} className="text-[#D4AF37]" />
                    </div>
                    <div className="absolute bottom-0 left-0 right-0 bg-black/80 text-[7px] text-zinc-500 text-center py-0.5 font-mono">
                      {sprite.row},{sprite.col}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
