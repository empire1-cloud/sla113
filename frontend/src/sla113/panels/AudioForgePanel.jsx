import React, { useState } from 'react';
import axios from 'axios';
import { Music, XCircle, Archive, Play } from 'lucide-react';
import { synthesizeFromAsset, playBuffer, stopSource, bufferToWav, downloadWav } from '../audioSynth';

const AudioForgePanel = ({ API, audioAssets, setAudioAssets, fetchData }) => {
  const [audioType, setAudioType] = useState('sfx');
  const [audioTitle, setAudioTitle] = useState('');
  const [audioEngine, setAudioEngine] = useState('FMOD');
  const [audioGameType] = useState('fish_shooting');
  const [audioGenerating, setAudioGenerating] = useState(false);
  const [selectedAudioAsset, setSelectedAudioAsset] = useState(null);
  const [dspReverbMix, setDspReverbMix] = useState(65);
  const [dspRumbleHz, setDspRumbleHz] = useState(35);
  const [dspTransientSharpness, setDspTransientSharpness] = useState(95);
  const [dspDecayMs, setDspDecayMs] = useState(4500);
  const [audioPlaying, setAudioPlaying] = useState(false);
  const [audioSourceRef, setAudioSourceRef] = useState(null);

  const handleGenerate = async () => {
    if (!audioTitle) return;
    setAudioGenerating(true);
    try {
      const res = await axios.post(`${API}/audio/generate`, {
        audio_type: audioType, title: audioTitle, game_type: audioGameType,
        engine: audioEngine,
        custom_params: {
          physical_modeling_parameters: { transient_sharpness: dspTransientSharpness / 100, decay_tail_ms: dspDecayMs },
          pda_environmental_dsp: { reverb_wet_mix: dspReverbMix / 100, low_frequency_rumble_hz: dspRumbleHz },
        },
      });
      setAudioAssets(prev => [res.data, ...prev]);
      setSelectedAudioAsset(res.data);
    } catch (e) { console.error("Audio gen failed:", e); }
    setAudioGenerating(false);
  };

  return (
    <div className="grid grid-cols-12 gap-6 h-full animate-in fade-in max-w-7xl mx-auto w-full" data-testid="audio-forge-panel">
      <div className="col-span-4 space-y-6">
        <div className="glass-panel border-[#D4AF37]/20 p-8 space-y-6">
          <h3 className="text-[#D4AF37] text-xs font-bold uppercase tracking-widest border-b border-[#D4AF37]/20 pb-4 flex items-center gap-2"><Music size={14}/> Audio Forge Engine</h3>
          <div className="space-y-4">
            <div>
              <label className="text-[9px] text-zinc-500 uppercase tracking-widest block mb-2">Sound Title</label>
              <input value={audioTitle} onChange={e => setAudioTitle(e.target.value)} placeholder="The Vault Lock (Subterranean)" className="input-dark focus:border-[#D4AF37] uppercase" data-testid="audio-title-input" />
            </div>
            <div>
              <label className="text-[9px] text-zinc-500 uppercase tracking-widest block mb-2">Audio Type</label>
              <div className="grid grid-cols-3 gap-1.5">
                {['sfx','ambience','foley','music_cues','stems','loops'].map(t => (
                  <button key={t} onClick={() => setAudioType(t)} className={`py-1.5 text-[8px] uppercase tracking-widest border transition-all ${audioType === t ? 'border-[#D4AF37] bg-[#D4AF37]/10 text-[#D4AF37]' : 'border-zinc-800 text-zinc-600 hover:text-zinc-300'}`} data-testid={`audio-type-${t}`}>
                    {t.replace('_',' ')}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="text-[9px] text-zinc-500 uppercase tracking-widest block mb-2">Engine</label>
              <div className="grid grid-cols-4 gap-1.5">
                {['FMOD','SonicForge','AudioKing','VoiceKing'].map(e => (
                  <button key={e} onClick={() => setAudioEngine(e)} className={`py-1.5 text-[7px] uppercase tracking-widest border transition-all ${audioEngine === e ? 'border-[#D4AF37] bg-[#D4AF37]/10 text-[#D4AF37]' : 'border-zinc-800 text-zinc-600 hover:text-zinc-300'}`}>
                    {e}
                  </button>
                ))}
              </div>
            </div>
            <div className="space-y-3 pt-2 border-t border-zinc-800">
              <span className="text-[8px] text-zinc-500 uppercase tracking-widest">PDA Environmental DSP</span>
              <div>
                <div className="flex justify-between text-[9px] text-zinc-400 mb-1"><span>Reverb Wet Mix</span><span className="text-[#D4AF37]">{dspReverbMix}%</span></div>
                <input type="range" min="0" max="100" value={dspReverbMix} onChange={e => setDspReverbMix(+e.target.value)} className="text-[#D4AF37]" />
              </div>
              <div>
                <div className="flex justify-between text-[9px] text-zinc-400 mb-1"><span>LF Rumble</span><span className="text-[#D4AF37]">{dspRumbleHz} Hz</span></div>
                <input type="range" min="10" max="120" value={dspRumbleHz} onChange={e => setDspRumbleHz(+e.target.value)} className="text-[#D4AF37]" />
              </div>
              <div>
                <div className="flex justify-between text-[9px] text-zinc-400 mb-1"><span>Transient Sharpness</span><span className="text-[#D4AF37]">{dspTransientSharpness / 100}</span></div>
                <input type="range" min="0" max="100" value={dspTransientSharpness} onChange={e => setDspTransientSharpness(+e.target.value)} className="text-[#D4AF37]" />
              </div>
              <div>
                <div className="flex justify-between text-[9px] text-zinc-400 mb-1"><span>Decay Tail</span><span className="text-[#D4AF37]">{dspDecayMs} ms</span></div>
                <input type="range" min="100" max="15000" step="100" value={dspDecayMs} onChange={e => setDspDecayMs(+e.target.value)} className="text-[#D4AF37]" />
              </div>
            </div>
          </div>
          <button onClick={handleGenerate} disabled={audioGenerating || !audioTitle}
            className="w-full py-4 bg-[#D4AF37]/10 border border-[#D4AF37] text-[#D4AF37] font-bold uppercase text-[10px] tracking-[2px] hover:bg-[#D4AF37] hover:text-black transition-all disabled:opacity-30"
            data-testid="generate-audio-btn"
          >
            {audioGenerating ? 'Forging Sound...' : 'Forge Audio Asset'}
          </button>
        </div>
      </div>

      <div className="col-span-8 space-y-4">
        {selectedAudioAsset && (
          <div className="glass-panel border-[#D4AF37]/20 p-6 space-y-4" data-testid="audio-detail-panel">
            <div className="flex justify-between items-start">
              <div>
                <h4 className="text-zinc-200 text-sm font-bold">{selectedAudioAsset.sfx_metadata?.title}</h4>
                <span className="text-[8px] text-zinc-500 uppercase tracking-widest">{selectedAudioAsset.sfx_metadata?.dna_tag_preview} / {selectedAudioAsset.sfx_metadata?.engine}</span>
              </div>
              <span className="px-2 py-0.5 text-[8px] border border-[#D4AF37]/30 bg-[#D4AF37]/10 text-[#D4AF37] uppercase tracking-widest font-bold">
                {selectedAudioAsset.sfx_metadata?.audio_type?.replace('_',' ')}
              </span>
            </div>
            <div className="bg-black/80 border border-zinc-800 p-4 h-32 flex items-end gap-px">
              {(selectedAudioAsset.waveform_preview || []).map((v, i) => (
                <div key={i} className="flex-1 bg-[#D4AF37]/70 transition-all hover:bg-[#D4AF37]" style={{ height: `${v * 100}%` }} />
              ))}
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => {
                  if (audioPlaying && audioSourceRef) {
                    stopSource(audioSourceRef); setAudioPlaying(false); setAudioSourceRef(null);
                  } else {
                    const buf = synthesizeFromAsset(selectedAudioAsset);
                    const src = playBuffer(buf, () => { setAudioPlaying(false); setAudioSourceRef(null); });
                    setAudioPlaying(true); setAudioSourceRef(src);
                  }
                }}
                className={`flex-1 py-3 font-bold uppercase text-[10px] tracking-[2px] border transition-all flex items-center justify-center gap-2 ${
                  audioPlaying ? 'border-red-500 bg-red-500/10 text-red-400 hover:bg-red-500 hover:text-black' : 'border-[#D4AF37] bg-[#D4AF37]/10 text-[#D4AF37] hover:bg-[#D4AF37] hover:text-black'
                }`}
                data-testid="audio-play-btn"
              >
                <Play size={14}/> {audioPlaying ? 'Stop' : 'Preview Sound'}
              </button>
              <button
                onClick={() => {
                  const buf = synthesizeFromAsset(selectedAudioAsset);
                  const blob = bufferToWav(buf);
                  const title = selectedAudioAsset.sfx_metadata?.title || 'audio';
                  downloadWav(blob, `sla113_${title.replace(/\s+/g, '_').toLowerCase()}.wav`);
                }}
                className="px-6 py-3 font-bold uppercase text-[10px] tracking-[2px] border border-[#D4AF37]/50 bg-black text-[#D4AF37] hover:bg-[#D4AF37]/10 transition-all flex items-center gap-2"
                data-testid="audio-download-btn"
              >
                <Archive size={14}/> Export WAV
              </button>
            </div>
            <div className="grid grid-cols-4 gap-2">
              {[
                { label: 'Duration', value: `${(selectedAudioAsset.duration_ms / 1000).toFixed(1)}s` },
                { label: 'Sample Rate', value: `${selectedAudioAsset.sample_rate / 1000}kHz` },
                { label: 'Bit Depth', value: `${selectedAudioAsset.bit_depth}-bit` },
                { label: 'Channels', value: selectedAudioAsset.channels === 2 ? 'Stereo' : 'Mono' },
              ].map(s => (
                <div key={s.label} className="bg-black/50 border border-zinc-800 p-3 text-center">
                  <div className="text-[7px] text-zinc-600 uppercase tracking-widest">{s.label}</div>
                  <div className="text-zinc-200 text-xs font-bold mt-0.5">{s.value}</div>
                </div>
              ))}
            </div>
            {selectedAudioAsset.ai_dsp_enhancement && (
              <div className="space-y-2">
                <span className="text-[8px] text-[#D4AF37] uppercase tracking-widest font-bold">AI-Enhanced DSP</span>
                <div className="grid grid-cols-2 gap-2">
                  {selectedAudioAsset.ai_dsp_enhancement.eq_bands && (
                    <div className="bg-black/50 border border-zinc-800 p-3">
                      <div className="text-[7px] text-zinc-600 uppercase tracking-widest mb-2">EQ Bands</div>
                      {selectedAudioAsset.ai_dsp_enhancement.eq_bands.map((band, i) => (
                        <div key={i} className="flex justify-between text-[9px] text-zinc-400">
                          <span>{band.freq_hz}Hz</span>
                          <span className={band.gain_db >= 0 ? 'text-[#D4AF37]' : 'text-red-400'}>{band.gain_db > 0 ? '+' : ''}{band.gain_db}dB</span>
                        </div>
                      ))}
                    </div>
                  )}
                  {selectedAudioAsset.ai_dsp_enhancement.compression && (
                    <div className="bg-black/50 border border-zinc-800 p-3">
                      <div className="text-[7px] text-zinc-600 uppercase tracking-widest mb-2">Compression</div>
                      {Object.entries(selectedAudioAsset.ai_dsp_enhancement.compression).map(([k, v]) => (
                        <div key={k} className="flex justify-between text-[9px] text-zinc-400">
                          <span>{k.replace(/_/g,' ')}</span>
                          <span className="text-zinc-200">{v}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
                {selectedAudioAsset.ai_dsp_enhancement.fmod_event_path && (
                  <div className="bg-black/50 border border-zinc-800 p-2">
                    <span className="text-[8px] text-zinc-600 uppercase tracking-widest">FMOD Event: </span>
                    <code className="text-[#D4AF37] text-[10px]">{selectedAudioAsset.ai_dsp_enhancement.fmod_event_path}</code>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        <span className="text-[#D4AF37] text-[10px] font-bold uppercase tracking-[3px]">Generated Assets ({audioAssets.length})</span>
        <div className="space-y-2 max-h-[300px] overflow-y-auto custom-scrollbar">
          {audioAssets.length === 0 && <div className="glass-panel border-[#D4AF37]/10 p-8 text-center text-zinc-600 text-[10px] uppercase tracking-widest">No audio assets. Forge your first sound above.</div>}
          {audioAssets.map(a => (
            <button key={a.id} onClick={() => setSelectedAudioAsset(a)} className={`w-full text-left p-4 border transition-all ${selectedAudioAsset?.id === a.id ? 'border-[#D4AF37]/50 bg-[#D4AF37]/5' : 'border-zinc-800 bg-black/50 hover:border-zinc-700'}`} data-testid={`audio-asset-${a.id}`}>
              <div className="flex justify-between items-center">
                <div>
                  <span className="text-zinc-200 text-xs font-bold">{a.sfx_metadata?.title}</span>
                  <span className="text-zinc-500 text-[9px] ml-2">{a.sfx_metadata?.audio_type?.replace('_',' ')} / {a.sfx_metadata?.engine}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[8px] text-zinc-500">{(a.duration_ms / 1000).toFixed(1)}s</span>
                  <span role="button" tabIndex={0} onClick={async (e) => { e.stopPropagation(); await axios.delete(`${API}/audio/assets/${a.id}`); setAudioAssets(prev => prev.filter(x => x.id !== a.id)); if (selectedAudioAsset?.id === a.id) setSelectedAudioAsset(null); }} className="text-zinc-600 hover:text-red-500 cursor-pointer"><XCircle size={12}/></span>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AudioForgePanel;
