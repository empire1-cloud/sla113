/**
 * SLA113 Audio Forge — Web Audio API Synthesizer
 * Generates playable WAV audio from AI-generated DSP parameters
 */

let audioCtx = null;

function getAudioContext() {
  if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  return audioCtx;
}

/**
 * Synthesize a sound from physical modeling + DSP parameters
 * @param {Object} asset - Audio asset from the backend
 * @returns {AudioBuffer}
 */
export function synthesizeFromAsset(asset) {
  const ctx = getAudioContext();
  const sampleRate = asset.sample_rate || 48000;
  const durationSec = (asset.duration_ms || 3000) / 1000;
  const channels = asset.channels || 2;
  const frameCount = Math.floor(sampleRate * durationSec);
  const buffer = ctx.createBuffer(channels, frameCount, sampleRate);

  const phys = asset.physical_modeling_parameters || {};
  const dsp = asset.pda_environmental_dsp || {};
  const aiDsp = asset.ai_dsp_enhancement || {};
  const audioType = asset.sfx_metadata?.audio_type || 'sfx';

  const sharpness = phys.transient_sharpness || 0.5;
  const decayMs = phys.decay_tail_ms || 2000;
  const decayRate = 1 / (decayMs / 1000 * sampleRate);
  const reverbMix = dsp.reverb_wet_mix || 0.3;
  const rumbleHz = dsp.low_frequency_rumble_hz || 40;

  for (let ch = 0; ch < channels; ch++) {
    const data = buffer.getChannelData(ch);
    const stereoOffset = ch === 1 ? 0.02 : 0;

    for (let i = 0; i < frameCount; i++) {
      const t = i / sampleRate;
      let sample = 0;

      if (audioType === 'sfx') {
        // Transient attack + exponential decay
        const envelope = Math.exp(-i * decayRate * 3) * sharpness;
        const noise = (Math.random() * 2 - 1) * envelope;
        const tone = Math.sin(2 * Math.PI * (rumbleHz + 200 * sharpness) * (t + stereoOffset)) * envelope * 0.6;
        const harmonic = Math.sin(2 * Math.PI * rumbleHz * 3 * t) * envelope * 0.2;
        sample = noise * 0.5 + tone + harmonic;
      } else if (audioType === 'ambience') {
        // Layered noise with slow modulation
        const mod = Math.sin(2 * Math.PI * 0.1 * t) * 0.3 + 0.7;
        const wind = (Math.random() * 2 - 1) * 0.15 * mod;
        const drone = Math.sin(2 * Math.PI * rumbleHz * (t + stereoOffset)) * 0.08 * mod;
        const high = Math.sin(2 * Math.PI * 2000 * t) * (Math.random() * 0.02);
        sample = wind + drone + high;
      } else if (audioType === 'foley') {
        // Short impulsive sounds
        const burstLen = 0.15;
        const burstEnv = t < burstLen ? Math.exp(-t / (burstLen * 0.3)) : 0;
        sample = (Math.random() * 2 - 1) * burstEnv * sharpness;
        sample += Math.sin(2 * Math.PI * 800 * t) * burstEnv * 0.3;
      } else if (audioType === 'music_cues') {
        // Musical tones with chord
        const notes = [261.6, 329.6, 392.0, 523.3];
        const env = Math.min(t / 0.1, 1) * Math.exp(-t * 0.5);
        notes.forEach((freq, idx) => {
          sample += Math.sin(2 * Math.PI * freq * (t + stereoOffset * idx)) * env * 0.2;
        });
      } else if (audioType === 'stems') {
        // Rhythmic pattern
        const beatHz = 2;
        const beatPhase = (t * beatHz) % 1;
        const kick = beatPhase < 0.1 ? Math.sin(2 * Math.PI * 60 * t) * (1 - beatPhase / 0.1) : 0;
        const hat = beatPhase > 0.5 && beatPhase < 0.55 ? (Math.random() * 2 - 1) * 0.3 : 0;
        sample = kick * 0.6 + hat;
      } else if (audioType === 'loops') {
        // Seamless loop with modulation
        const loopLen = 1.0;
        const phase = (t % loopLen) / loopLen;
        const baseFreq = rumbleHz * 4;
        sample = Math.sin(2 * Math.PI * baseFreq * t + Math.sin(2 * Math.PI * 0.5 * t) * 2) * 0.3;
        sample += Math.sin(2 * Math.PI * baseFreq * 1.5 * t) * 0.15 * Math.sin(2 * Math.PI * phase * Math.PI);
      } else {
        sample = (Math.random() * 2 - 1) * Math.exp(-i * decayRate);
      }

      // Simple reverb (comb filter)
      if (i > sampleRate * 0.05) {
        const delayed = data[Math.floor(i - sampleRate * 0.05)] || 0;
        sample = sample * (1 - reverbMix) + delayed * reverbMix * 0.6;
      }

      // Soft clip
      sample = Math.tanh(sample * 1.5) * 0.8;
      data[i] = sample;
    }
  }

  return buffer;
}

/**
 * Play an AudioBuffer
 */
export function playBuffer(buffer, onEnd) {
  const ctx = getAudioContext();
  const source = ctx.createBufferSource();
  source.buffer = buffer;
  source.connect(ctx.destination);
  source.start(0);
  if (onEnd) source.onended = onEnd;
  return source;
}

/**
 * Stop a playing source
 */
export function stopSource(source) {
  try { source?.stop(); } catch {}
}

/**
 * Convert AudioBuffer to downloadable WAV blob
 */
export function bufferToWav(buffer) {
  const numChannels = buffer.numberOfChannels;
  const sampleRate = buffer.sampleRate;
  const format = 1; // PCM
  const bitDepth = 16;
  const bytesPerSample = bitDepth / 8;
  const blockAlign = numChannels * bytesPerSample;
  const numFrames = buffer.length;
  const dataSize = numFrames * blockAlign;
  const headerSize = 44;
  const totalSize = headerSize + dataSize;

  const wav = new ArrayBuffer(totalSize);
  const view = new DataView(wav);

  // RIFF header
  writeString(view, 0, 'RIFF');
  view.setUint32(4, totalSize - 8, true);
  writeString(view, 8, 'WAVE');
  writeString(view, 12, 'fmt ');
  view.setUint32(16, 16, true);
  view.setUint16(20, format, true);
  view.setUint16(22, numChannels, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * blockAlign, true);
  view.setUint16(32, blockAlign, true);
  view.setUint16(34, bitDepth, true);
  writeString(view, 36, 'data');
  view.setUint32(40, dataSize, true);

  // Interleave channels
  const channels = [];
  for (let ch = 0; ch < numChannels; ch++) {
    channels.push(buffer.getChannelData(ch));
  }

  let offset = 44;
  for (let i = 0; i < numFrames; i++) {
    for (let ch = 0; ch < numChannels; ch++) {
      const sample = Math.max(-1, Math.min(1, channels[ch][i]));
      const val = sample < 0 ? sample * 0x8000 : sample * 0x7FFF;
      view.setInt16(offset, val, true);
      offset += 2;
    }
  }

  return new Blob([wav], { type: 'audio/wav' });
}

function writeString(view, offset, str) {
  for (let i = 0; i < str.length; i++) {
    view.setUint8(offset + i, str.charCodeAt(i));
  }
}

/**
 * Download a WAV blob
 */
export function downloadWav(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename || 'sla113_audio.wav';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
