"""Compose a self-contained HTML5 canvas game that plays the verified math.

The playable build spawns targets with the verified probabilities and pays the
verified paytable, so what is played is what was verified. One wager is charged
per resolved target (matching the RTP basis in logic.py); misses are free.
"""
from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any, Dict, List

_JS = r"""
const G = window.GENESIS;
const c = document.querySelector("canvas"), x = c.getContext("2d");
const imgs = {};
for (const a of G.assets) { const i = new Image(); i.src = a.path.replace(/^web\//, ""); imgs[a.target] = i; }
const keys = Object.keys(G.probabilities);
const cum = []; let acc = 0; for (const k of keys) { acc += G.probabilities[k]; cum.push(acc); }
function pick() { const r = Math.random() * acc; for (let i = 0; i < cum.length; i++) if (r <= cum[i]) return keys[i]; return keys[keys.length - 1]; }
const sfx = {}; for (const a of G.audio) sfx[a.name] = a.path.replace(/^web\//, "");
function play(n) { if (!sfx[n]) return; try { new Audio(sfx[n]).play(); } catch (e) {} }
let fish = [], credits = 1000, wagered = 0, paid = 0;
function mk(i) { const k = pick(); const a = G.assets.find(s => s.target === k) || {dimensions:{width:120,height:60}};
  return { k, w: a.dimensions.width * 0.6, h: a.dimensions.height * 0.6, x: Math.random() * c.width, y: 90 + Math.random() * (c.height - 150), v: 0.6 + Math.random() * 1.8 }; }
for (let i = 0; i < G.fish_count; i++) fish.push(mk(i));
function draw() {
  x.fillStyle = "#050505"; x.fillRect(0, 0, c.width, c.height);
  for (const f of fish) { const im = imgs[f.k];
    if (im && im.complete && im.naturalWidth) x.drawImage(im, f.x, f.y, f.w, f.h); else { x.fillStyle = "#48bfe3"; x.fillRect(f.x, f.y, f.w, f.h); }
    f.x += f.v; if (f.x > c.width + 40) Object.assign(f, mk(), { x: -f.w }); }
  x.fillStyle = "#E8B923"; x.font = "20px sans-serif";
  x.fillText(G.name + "  |  credits " + credits.toFixed(2) + "  |  session RTP " + (wagered ? (100 * paid / wagered).toFixed(1) : "-") + "%  |  verified RTP " + G.rtp_percent + "%", 20, 36);
  requestAnimationFrame(draw);
}
c.addEventListener("click", e => { const r = c.getBoundingClientRect(), mx = (e.clientX - r.left) * c.width / r.width, my = (e.clientY - r.top) * c.height / r.height;
  play("shot");
  for (let i = fish.length - 1; i >= 0; i--) { const f = fish[i];
    if (mx >= f.x && mx <= f.x + f.w && my >= f.y && my <= f.y + f.h) {
      const win = G.paytable[f.k]; credits += win - 1; wagered += 1; paid += win;
      play(win >= 5 ? "big_win" : "hit"); fish[i] = mk(); fish[i].x = -fish[i].w; break; } } });
draw();
"""


def compose_web(spec: Any, verification: Dict[str, Any], assets: List[Dict[str, Any]], audio: List[Dict[str, Any]], root: Path) -> Dict[str, Any]:
    web = root / "web"
    web.mkdir(parents=True, exist_ok=True)
    manifest = {
        "name": spec.name, "version": "0.1.0", "game_type": spec.game_type, "theme": spec.theme,
        "verification": verification, "assets": assets, "audio": audio,
    }
    (web / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    runtime = {
        "name": spec.name,
        "fish_count": spec.fish_count,
        "paytable": verification["paytable"],
        "probabilities": verification["probabilities"],
        "rtp_percent": verification["theoretical_rtp_percent"],
        "assets": assets,
        "audio": audio,
    }
    runtime_json = json.dumps(runtime).replace("</", "<\\/")
    page = (
        "<!doctype html><html><head><meta charset=\"utf-8\">"
        f"<title>{html.escape(spec.name)}</title>"
        "<style>html,body{margin:0;background:#050505}canvas{display:block;width:100vw;height:100vh;cursor:crosshair}</style>"
        f"</head><body><canvas width=\"{spec.width}\" height=\"{spec.height}\"></canvas>"
        f"<script>window.GENESIS={runtime_json};</script><script>{_JS}</script></body></html>"
    )
    (web / "index.html").write_text(page, encoding="utf-8")
    return {
        "format": "html5", "entrypoint": "web/index.html",
        "files": ["web/index.html", "web/manifest.json"],
        "uses_verified_math": True, "status": "playable",
    }
