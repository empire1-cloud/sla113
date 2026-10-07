import React from 'react';

/**
 * Southern Lyfestyle reel art — hand-built inline SVG, ink on cream.
 * Original drawings only. The sneaker carries the Empire mark (stepped fret from the
 * Empire coin) instead of any third-party logo.
 */

const INK = '#1a1410';
const S = { stroke: INK, strokeWidth: 3, strokeLinecap: 'round', strokeLinejoin: 'round' };

/** Empire logo: stepped fret + square spiral (vector trace of the Empire coin glyph). */
function EmpireMarkPath({ color = INK }) {
  return (
    <path
      d="M8 64 H20 V52 H32 V40 H44 V26 H80 V80 H36 V44 H64 V64 H52"
      fill="none" stroke={color} strokeWidth="9" strokeLinejoin="miter" strokeLinecap="square"
    />
  );
}

export function EmpireMark({ size = 24, color = '#d9a441' }) {
  return (
    <svg viewBox="0 0 90 90" width={size} height={size} role="img" aria-label="Empire">
      <EmpireMarkPath color={color} />
    </svg>
  );
}

const ART = {
  // WILD — jaguar face carved in a sun stone.
  piedra: (
    <g {...S}>
      <circle cx="50" cy="50" r="42" fill="#a9a39a" />
      <circle cx="50" cy="50" r="34" fill="#c4beb4" />
      {Array.from({ length: 16 }, (_, i) => {
        const a = (i / 16) * Math.PI * 2;
        return <line key={i} x1={50 + Math.cos(a) * 34} y1={50 + Math.sin(a) * 34} x2={50 + Math.cos(a) * 42} y2={50 + Math.sin(a) * 42} />;
      })}
      <path d="M30 34 L36 22 L42 32 M58 32 L64 22 L70 34" fill="#c4beb4" />
      <path d="M30 36 Q50 26 70 36 L68 60 Q50 76 32 60 Z" fill="#8f897f" />
      <path d="M36 44 L45 47 M64 44 L55 47" strokeWidth="4" />
      <path d="M45 56 L50 60 L55 56 Z" fill={INK} />
      <path d="M40 64 Q50 70 60 64" />
      <path d="M38 52 l-6 1 M38 56 l-6 3 M62 52 l6 1 M62 56 l6 3" strokeWidth="2" />
    </g>
  ),
  // SCATTER — the rocola (jukebox).
  rocola: (
    <g {...S}>
      <path d="M22 90 L22 40 Q22 10 50 10 Q78 10 78 40 L78 90 Z" fill="#5b2a1c" />
      <path d="M30 86 L30 42 Q30 20 50 20 Q70 20 70 42 L70 86 Z" fill="#ffcf87" />
      <path d="M34 44 Q34 26 50 26 Q66 26 66 44" stroke="#d7263d" strokeWidth="4" fill="none" />
      <path d="M38 46 Q38 32 50 32 Q62 32 62 46" stroke="#1fb5a3" strokeWidth="4" fill="none" />
      <rect x="36" y="52" width="28" height="12" rx="2" fill="#2a180f" />
      <path d="M38 70 H62 M38 76 H62 M38 82 H62" strokeWidth="2" />
    </g>
  ),
  lowrider: (
    <g {...S}>
      <path d="M6 62 Q8 52 20 50 L34 48 L42 36 Q46 33 54 33 L68 33 Q74 33 78 40 L82 48 L92 50 Q96 52 96 60 L96 64 L6 64 Z" fill="#e9e3d6" />
      <path d="M44 38 L54 38 L54 48 L38 48 Z M58 38 L68 38 Q72 38 74 42 L76 48 L58 48 Z" fill="#9fb4bf" />
      <path d="M10 58 H92" strokeWidth="2" />
      <circle cx="26" cy="66" r="10" fill={INK} /><circle cx="26" cy="66" r="6" fill="#d9d9e3" />
      <circle cx="78" cy="66" r="10" fill={INK} /><circle cx="78" cy="66" r="6" fill="#d9d9e3" />
      <path d="M26 60 V72 M20 66 H32 M78 60 V72 M72 66 H84" strokeWidth="1.5" />
    </g>
  ),
  vinyl: (
    <g {...S}>
      <circle cx="50" cy="50" r="40" fill="#111" />
      <circle cx="50" cy="50" r="33" fill="none" stroke="#3a3a3a" strokeWidth="1.5" />
      <circle cx="50" cy="50" r="26" fill="none" stroke="#3a3a3a" strokeWidth="1.5" />
      <circle cx="50" cy="50" r="13" fill="#7cc243" stroke="#111" />
      <circle cx="50" cy="50" r="2.5" fill="#f3e6c8" stroke="none" />
      <path d="M26 30 Q34 22 44 20" stroke="#ffffff55" strokeWidth="3" fill="none" />
    </g>
  ),
  rosa: (
    <g {...S}>
      <path d="M50 52 L50 92" stroke="#2f6b3a" strokeWidth="4" />
      <path d="M50 74 Q36 64 30 72 Q40 80 50 76 M50 66 Q64 56 70 64 Q60 72 50 68" fill="#3f8a4d" stroke="#2f6b3a" strokeWidth="2" />
      <path d="M50 54 Q28 52 30 30 Q40 18 50 22 Q60 18 70 30 Q72 52 50 54 Z" fill="#b3202a" />
      <path d="M50 46 Q40 44 40 34 Q46 28 52 32 Q58 30 60 38 Q58 46 50 46 Z" fill="#d6363f" strokeWidth="2" />
      <path d="M48 38 Q52 34 54 39" strokeWidth="2" fill="none" />
    </g>
  ),
  hoops: (
    <g strokeLinecap="round" fill="none">
      <path d="M34 14 Q30 10 34 6 M66 14 Q62 10 66 6" stroke={INK} strokeWidth="3" />
      <circle cx="34" cy="44" r="24" stroke={INK} strokeWidth="9" />
      <circle cx="34" cy="44" r="24" stroke="#cfd2d8" strokeWidth="5" />
      <circle cx="66" cy="50" r="24" stroke={INK} strokeWidth="9" />
      <circle cx="66" cy="50" r="24" stroke="#e6e8ec" strokeWidth="5" />
    </g>
  ),
  tenis: (
    <g {...S}>
      <path d="M8 66 Q8 58 16 56 L40 50 Q48 40 58 40 L66 42 Q72 50 84 54 Q94 57 94 64 L94 70 L8 70 Z" fill="#fbfaf6" />
      <path d="M8 70 L94 70 L94 74 Q50 78 8 74 Z" fill="#e8e1d2" />
      <g transform="translate(40 44) scale(0.27)"><EmpireMarkPath color={INK} /></g>
      <path d="M50 44 L55 47 M54 42 L59 45" strokeWidth="2" />
    </g>
  ),
  peine: (
    <g {...S}>
      <path d="M12 70 L60 22 Q66 18 70 22 L78 30 Q82 34 78 40 L30 88 Z" fill="#1c1c1c" />
      {Array.from({ length: 11 }, (_, i) => {
        const t = i / 10;
        const x = 34 + t * 40; const y = 82 - t * 40;
        return <line key={i} x1={x} y1={y} x2={x + 9} y2={y + 9} stroke="#1c1c1c" strokeWidth="3" />;
      })}
    </g>
  ),
  concha: (
    <g {...S}>
      <path d="M12 68 Q12 30 50 28 Q88 30 88 68 Z" fill="#d99a52" />
      <path d="M12 68 Q50 76 88 68" fill="#b8793a" />
      <path d="M22 60 Q30 42 50 38 M30 64 Q38 48 50 46 M78 60 Q70 42 50 38 M70 64 Q62 48 50 46 M50 38 V66" strokeWidth="2.5" fill="none" stroke="#7a4a1d" />
    </g>
  ),
  nopal: (
    <g {...S}>
      <ellipse cx="50" cy="66" rx="18" ry="24" fill="#3f8a4d" />
      <ellipse cx="30" cy="36" rx="13" ry="18" fill="#4f9e5c" transform="rotate(-25 30 36)" />
      <ellipse cx="70" cy="34" rx="12" ry="17" fill="#4f9e5c" transform="rotate(25 70 34)" />
      <circle cx="72" cy="15" r="5" fill="#e4007c" />
      <path d="M44 58 l-3 -2 M56 64 l3 -2 M48 76 l-3 2 M28 32 l-3 -1 M70 30 l3 -1" strokeWidth="2" />
    </g>
  ),
};

export default function LyfestyleSymbol({ id, size = '100%', title }) {
  return (
    <svg viewBox="0 0 100 100" width={size} height={size} role="img" aria-label={title || id}>
      {ART[id] || null}
    </svg>
  );
}
