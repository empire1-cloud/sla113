import React from 'react';
import { Link } from 'react-router-dom';
import ArcadeChrome from './ArcadeChrome';

const bossCard = (index) => ({ backgroundImage: 'url(/arcade/fish/boss_' + index + '.webp)', backgroundSize: 'auto 100%', backgroundRepeat: 'no-repeat', backgroundPosition: '0 0' });

const CABINETS = [
  {
    to: '/sla113/fish/rooster',
    art: bossCard('rooster'),
    name: "QUETZALCOATL'S QUEST",
    kind: 'Fish shooter · Boss table',
    pitch: 'Feathered-serpent rooster boss over the Mictlan background.',
    tags: ['Owner art', 'Boss after 12 kills'],
    accent: '#f2b632',
  },
  {
    to: '/sla113/fish/xolotl',
    art: bossCard('xolotl'),
    name: "XOLOTL'S DESCENT",
    kind: 'Fish shooter · Boss table',
    pitch: 'Xolotl wolf-warrior boss over the Mictlan background.',
    tags: ['Owner art', 'Boss after 12 kills'],
    accent: '#1fb5a3',
  },
  {
    to: '/sla113/xolotl',
    glyph: '🐟',
    name: 'XOLOTL HUNT',
    kind: 'Fish shooter',
    pitch: 'Take aim over the underworld waters. Spirits, jaguars, warriors, and the Golden Xolotl himself.',
    tags: ['Combo multiplier', 'Boss: Xolotl', 'Auto-fire'],
    accent: '#1fb5a3',
  },
  {
    to: '/sla113/arcade/slots',
    glyph: '☀️',
    name: 'PIEDRA DEL SOL',
    kind: 'Reels',
    pitch: 'Five reels, ten lines. The sun stone is wild, and three Templos anywhere pay the bonus.',
    tags: ['97% math, unit-tested', '10 lines', 'Scatter bonus'],
    accent: '#f2b632',
  },
  {
    to: '/sla113/arcade/kart',
    glyph: '🚗',
    name: 'LOWRIDER RALLY',
    kind: 'Kart racing',
    pitch: 'Candy paint, gold spokes, three laps down the Calzada del Sol. Hit the hydraulics to hop clean over the pack.',
    tags: ['Hydraulic HOP', '6-car field', 'Top 3 paid'],
    accent: '#e4007c',
  },
];

const CSS = `
.al-hero{text-align:center;padding:28px 0 26px}
.al-hero h1{margin:0;font-size:clamp(34px,7vw,72px);font-weight:900;letter-spacing:6px;line-height:1;
  background:linear-gradient(180deg,#fff2b8,#f2b632 45%,#b9771b);-webkit-background-clip:text;background-clip:text;color:transparent;
  filter:drop-shadow(0 6px 0 #4a1942) drop-shadow(0 0 30px #e4007c55)}
.al-hero p{margin:12px auto 0;max-width:620px;color:#cdbf9f;font-size:15px;line-height:1.5}
.al-hero .al-glyphs{font-size:12px;letter-spacing:10px;color:#1fb5a3;margin-top:12px}
.al-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:18px}
.al-cab{position:relative;display:flex;flex-direction:column;text-decoration:none;color:inherit;border-radius:22px;overflow:hidden;
  background:linear-gradient(180deg,#22142c,#0f0a12);border:2px solid var(--accent);box-shadow:0 0 0 4px #0b0806,0 0 40px color-mix(in srgb,var(--accent) 30%,transparent);
  transition:transform .18s ease,box-shadow .18s ease}
.al-cab:hover{transform:translateY(-4px);box-shadow:0 0 0 4px #0b0806,0 0 60px color-mix(in srgb,var(--accent) 55%,transparent)}
.al-screen{height:170px;display:flex;align-items:center;justify-content:center;font-size:84px;position:relative;
  background:radial-gradient(circle at 50% 60%,color-mix(in srgb,var(--accent) 45%,#0b0806),#0b0806 70%)}
.al-screen:before{content:"";position:absolute;inset:0;background:repeating-linear-gradient(0deg,transparent 0 3px,#ffffff08 3px 4px)}
.al-screen:after{content:"";position:absolute;left:0;right:0;bottom:0;height:12px;
  background:repeating-linear-gradient(90deg,var(--accent) 0 12px,#f2b632 12px 24px,#0b0806 24px 30px)}
.al-body{padding:16px 18px 18px;display:flex;flex-direction:column;gap:8px;flex:1}
.al-body small{font-size:10px;letter-spacing:3px;text-transform:uppercase;color:var(--accent);font-weight:800}
.al-body h2{margin:0;font-size:24px;font-weight:900;letter-spacing:2px}
.al-body p{margin:0;color:#cdbf9f;font-size:14px;line-height:1.45}
.al-tags{display:flex;gap:6px;flex-wrap:wrap;margin-top:4px}
.al-tags span{font-size:10px;letter-spacing:1px;border:1px solid #ffffff22;border-radius:999px;padding:4px 9px;color:#f6ead0}
.al-play{margin-top:auto;padding-top:10px}
.al-strip{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin-top:22px}
.al-strip div{border:1px dashed #f2b63255;border-radius:14px;padding:12px 14px;font-size:13px;color:#cdbf9f;line-height:1.45}
.al-strip b{display:block;color:#ffd86b;font-size:12px;letter-spacing:2px;margin-bottom:4px}
`;

export default function ArcadeLobby() {
  return (
    <ArcadeChrome>
      <style>{CSS}</style>
      <div className="al-hero">
        <h1>SOUTHERN LIFESTYLE ARCADE</h1>
        <div className="al-glyphs">◆ FISH · SPIN · RIDE ◆</div>
        <p>Three cabinets and one cacao wallet. The Aztecs traded in cacao beans, and here you play with them. Aztec gods meet Chicano lowriders, all running in your browser.</p>
      </div>
      <div className="al-grid">
        {CABINETS.map((c) => (
          <Link key={c.to} to={c.to} className="al-cab" style={{ '--accent': c.accent }}>
            <div className="al-screen">{c.art
                ? <div aria-hidden="true" style={{ width: 170, height: 170, position: 'relative', zIndex: 1, ...c.art }} />
                : <span style={{ position: 'relative', zIndex: 1 }}>{c.glyph}</span>}</div>
            <div className="al-body">
              <small>{c.kind}</small>
              <h2>{c.name}</h2>
              <p>{c.pitch}</p>
              <div className="al-tags">{c.tags.map((t) => <span key={t}>{t}</span>)}</div>
              <div className="al-play"><span className="az-btn primary">Play →</span></div>
            </div>
          </Link>
        ))}
      </div>
      <div className="al-strip">
        <div><b>ONE WALLET</b>Cacao you win in one cabinet carries into the others.</div>
        <div><b>OUR OWN CULTURE</b>Sun stones, xolos, nopales, papel picado and candy paint, not the same recycled ocean theme.</div>
        <div><b>PLAY ONLY</b>Virtual credits with no purchase, no cash value and no prizes.</div>
      </div>
    </ArcadeChrome>
  );
}
