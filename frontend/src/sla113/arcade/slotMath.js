/**
 * Piedra del Sol — 5x3 slot math contract (virtual cacao only).
 *
 * Pure functions, no DOM: the reel strips, paytable and evaluator here are the
 * single source of truth for the cabinet UI and for the RTP test. Line pays are
 * multiples of the line bet; scatter pays are multiples of the total bet.
 */

export const SYMBOLS = {
  sol:      { glyph: '☀️', name: 'Piedra del Sol', role: 'wild' },
  templo:   { glyph: '🛕', name: 'Templo Mayor', role: 'scatter' },
  jaguar:   { glyph: '🐆', name: 'Guerrero Jaguar' },
  quetzal:  { glyph: '🦜', name: 'Quetzal' },
  lowrider: { glyph: '🚗', name: 'Lowrider' },
  calavera: { glyph: '💀', name: 'Calavera' },
  rosa:     { glyph: '🌹', name: 'Rosa' },
  chile:    { glyph: '🌶️', name: 'Chile' },
  maiz:     { glyph: '🌽', name: 'Maíz' },
  nopal:    { glyph: '🌵', name: 'Nopal' },
};

export const WILD = 'sol';
export const SCATTER = 'templo';
export const ROWS = 3;
export const REELS = 5;

// Pays for 3, 4, 5 of a kind on a line, in line-bet multiples.
export const PAYTABLE = {
  sol:      [50, 200, 1000],
  jaguar:   [25, 100, 750],
  quetzal:  [15, 60, 300],
  lowrider: [12, 50, 200],
  calavera: [8, 25, 100],
  rosa:     [6, 20, 80],
  chile:    [4, 12, 50],
  maiz:     [3, 10, 40],
  nopal:    [2, 6, 25],
};

// Scatter pays for 3, 4, 5 Templos anywhere, in total-bet multiples.
export const SCATTER_PAYS = { 3: 4, 4: 20, 5: 100 };

// Rows indexed top=0, mid=1, bottom=2 for each of the 5 reels.
export const PAYLINES = [
  [1, 1, 1, 1, 1],
  [0, 0, 0, 0, 0],
  [2, 2, 2, 2, 2],
  [0, 1, 2, 1, 0],
  [2, 1, 0, 1, 2],
  [0, 0, 1, 2, 2],
  [2, 2, 1, 0, 0],
  [1, 0, 0, 0, 1],
  [1, 2, 2, 2, 1],
  [1, 0, 1, 2, 1],
];

// Symbol counts per reel. The middle reels carry extra wilds.
const COUNTS = [
  { sol: 2, templo: 1, jaguar: 2, quetzal: 2, lowrider: 3, calavera: 3, rosa: 3, chile: 4, maiz: 4, nopal: 4 },
  { sol: 3, templo: 1, jaguar: 2, quetzal: 2, lowrider: 3, calavera: 3, rosa: 3, chile: 4, maiz: 4, nopal: 4 },
  { sol: 3, templo: 1, jaguar: 2, quetzal: 2, lowrider: 3, calavera: 3, rosa: 3, chile: 4, maiz: 4, nopal: 4 },
  { sol: 3, templo: 1, jaguar: 2, quetzal: 2, lowrider: 3, calavera: 3, rosa: 3, chile: 4, maiz: 4, nopal: 4 },
  { sol: 2, templo: 1, jaguar: 2, quetzal: 2, lowrider: 3, calavera: 3, rosa: 3, chile: 4, maiz: 4, nopal: 4 },
];

/** Deterministically interleave counts into a strip so symbols spread out. */
function buildStrip(counts) {
  const pool = Object.entries(counts).sort((a, b) => b[1] - a[1]);
  const total = pool.reduce((s, [, n]) => s + n, 0);
  const slots = new Array(total).fill(null);
  let cursor = 0;
  for (const [sym, n] of pool) {
    const step = total / n;
    for (let i = 0; i < n; i++) {
      let pos = Math.floor(cursor + i * step) % total;
      while (slots[pos] !== null) pos = (pos + 1) % total;
      slots[pos] = sym;
    }
    cursor += 1;
  }
  return slots;
}

export const STRIPS = COUNTS.map(buildStrip);

function defaultRng() {
  if (typeof crypto !== 'undefined' && crypto.getRandomValues) {
    const buf = new Uint32Array(1);
    crypto.getRandomValues(buf);
    return buf[0] / 2 ** 32;
  }
  return Math.random();
}

/** Returns stops (top index per reel) and the visible grid grid[reel][row]. */
export function spinReels(rng = defaultRng) {
  const stops = STRIPS.map((strip) => Math.floor(rng() * strip.length));
  return { stops, grid: gridFromStops(stops) };
}

export function gridFromStops(stops) {
  return stops.map((stop, r) => {
    const strip = STRIPS[r];
    return Array.from({ length: ROWS }, (_, row) => strip[(stop + row) % strip.length]);
  });
}

/** Best pay for one line of 5 symbols, left to right, wild substitutes. */
export function evaluateLine(symbols) {
  let best = { symbol: null, count: 0, pay: 0 };

  // Pure-wild run pays on its own table.
  let wildRun = 0;
  while (wildRun < symbols.length && symbols[wildRun] === WILD) wildRun++;
  if (wildRun >= 3) best = { symbol: WILD, count: wildRun, pay: PAYTABLE[WILD][wildRun - 3] };

  const base = symbols.find((s) => s !== WILD);
  if (!base || base === SCATTER) return best;
  let count = 0;
  while (count < symbols.length && (symbols[count] === base || symbols[count] === WILD)) count++;
  if (count >= 3) {
    const pay = PAYTABLE[base][count - 3];
    if (pay > best.pay) best = { symbol: base, count, pay };
  }
  return best;
}

/** Evaluates a grid for a total bet. Returns cacao won and the winning lines. */
export function evaluateGrid(grid, totalBet) {
  const lineBet = totalBet / PAYLINES.length;
  const wins = [];
  PAYLINES.forEach((line, index) => {
    const symbols = line.map((row, reel) => grid[reel][row]);
    const { symbol, count, pay } = evaluateLine(symbols);
    if (pay > 0) wins.push({ line: index, symbol, count, amount: pay * lineBet });
  });

  const scatters = grid.flat().filter((s) => s === SCATTER).length;
  const scatterPay = (SCATTER_PAYS[scatters] || 0) * totalBet;

  const total = Math.floor(wins.reduce((s, w) => s + w.amount, 0) + scatterPay);
  return { total, wins, scatters, scatterPay };
}

/**
 * Exact theoretical return-to-player, computed by enumeration rather than
 * simulation. Every row of a reel is marginally uniform over its strip, so a
 * line's expected pay is the same for all 10 lines.
 */
export function theoreticalRtp() {
  const freqs = STRIPS.map((strip) => {
    const f = {};
    strip.forEach((s) => { f[s] = (f[s] || 0) + 1 / strip.length; });
    return Object.entries(f);
  });

  let lineEv = 0;
  const walk = (reel, picked, p) => {
    if (reel === REELS) { lineEv += p * evaluateLine(picked).pay; return; }
    for (const [sym, q] of freqs[reel]) walk(reel + 1, [...picked, sym], p * q);
  };
  walk(0, [], 1);

  // Each strip has one scatter, so a reel shows it with probability ROWS/len.
  let dist = [1];
  STRIPS.forEach((strip) => {
    const n = strip.filter((s) => s === SCATTER).length;
    const p = Math.min(1, (ROWS * n) / strip.length);
    const next = new Array(dist.length + 1).fill(0);
    dist.forEach((v, k) => { next[k] += v * (1 - p); next[k + 1] += v * p; });
    dist = next;
  });
  const scatterEv = dist.reduce((s, v, k) => s + v * (SCATTER_PAYS[k] || 0), 0);

  // Line EV is per line bet; 10 lines at totalBet/10 each sum to lineEv.
  return { line: lineEv, scatter: scatterEv, total: lineEv + scatterEv };
}
