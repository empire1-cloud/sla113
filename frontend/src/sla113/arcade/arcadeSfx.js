/** Tiny Web Audio blips for the arcade cabinets — no audio files to ship. */

let ctx = null;
let muted = false;

function audio() {
  if (!ctx) {
    const AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return null;
    ctx = new AC();
  }
  if (ctx.state === 'suspended') ctx.resume();
  return ctx;
}

export const setMuted = (m) => { muted = m; };
export const isMuted = () => muted;

export function tone(freq, duration = 0.08, type = 'square', gain = 0.05, delay = 0) {
  if (muted) return;
  const a = audio();
  if (!a) return;
  const t = a.currentTime + delay;
  const osc = a.createOscillator();
  const g = a.createGain();
  osc.type = type;
  osc.frequency.setValueAtTime(freq, t);
  g.gain.setValueAtTime(gain, t);
  g.gain.exponentialRampToValueAtTime(0.0001, t + duration);
  osc.connect(g).connect(a.destination);
  osc.start(t);
  osc.stop(t + duration + 0.02);
}

export const sfx = {
  click: () => tone(660, 0.04, 'square', 0.03),
  reelStop: (i = 0) => tone(220 + i * 40, 0.06, 'triangle', 0.06),
  win: (big = false) => {
    const notes = big ? [523, 659, 784, 1047, 1319] : [523, 659, 784];
    notes.forEach((f, i) => tone(f, 0.14, 'square', 0.04, i * 0.09));
  },
  coin: () => { tone(988, 0.05, 'square', 0.035); tone(1319, 0.08, 'square', 0.035, 0.05); },
  bump: () => tone(90, 0.15, 'sawtooth', 0.07),
  hop: () => { tone(180, 0.08, 'sine', 0.08); tone(320, 0.12, 'sine', 0.06, 0.06); },
  countdown: (go = false) => tone(go ? 880 : 440, go ? 0.35 : 0.15, 'square', 0.05),
};
