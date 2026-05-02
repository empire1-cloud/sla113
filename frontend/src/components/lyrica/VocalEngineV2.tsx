import React, { useState, useEffect, useRef } from 'react';
import { GoogleGenAI, Modality } from "@google/genai";
import * as Tone from 'tone';
import { motion } from 'motion/react';
import { 
  Mic2, 
  Play, 
  Pause, 
  Settings2, 
  History,
  Download,
  Activity,
  Layers,
  RefreshCw
} from 'lucide-react';
import { cn, withRetry } from '../lib/utils';
import { db, auth, handleFirestoreError, OperationType } from '../lib/firebase';
import { collection, addDoc, query, where, onSnapshot, orderBy } from 'firebase/firestore';
import { useStudioStore } from '../store/useStudioStore';
import { VocalAsset } from '../types';

interface PerformerDNA {
  vulnerability: number;
  raspiness: number;
  vibrato: number;
  nasality: number;
  brightness: number;
  grit: number;
  warmth: number;
  resonance: number;
  clarity: number;
  breath: number;
}

interface VocalParams {
  prompt: string;
  lyrics: string;
  performerDNA: PerformerDNA;
  vocalRange: string;
  backingTrackId: string;
  isEMSS: boolean;
  emotionalProfile: string;
  harmonyType: string;
  harmonyIntensity: number;
}

interface VocalLayer {
  id: string;
  asset: VocalAsset;
  volume: number;
  pan: number;
  offset: number;
  dryWet: number;
}

const DNA_DESCRIPTIONS: Record<string, string> = {
  vulnerability: "Adds emotional fragility and slight pitch instability for a raw, intimate feel.",
  raspiness: "Introduces vocal cord distortion and grit for a rougher, textured tone.",
  warmth: "Boosts lower-mid frequencies for a fuller, richer, and more comforting sound.",
  breath: "Increases the audible breathiness and airiness in the vocal delivery."
};

export const VocalEngine: React.FC = () => {
  const { activeProject, musicAssets, addVocalAsset } = useStudioStore();
  const [params, setParams] = useState<VocalParams>({
    prompt: 'Smooth, male baritone voice singing with theatrical flair.',
    lyrics: 'The velvet cage is now unlocked.',
    performerDNA: {
      vulnerability: 40,
      raspiness: 30,
      vibrato: 60,
      nasality: 10,
      brightness: 70,
      grit: 20,
      warmth: 80,
      resonance: 85,
      clarity: 90,
      breath: 40
    },
    vocalRange: 'Baritone',
    backingTrackId: '',
    isEMSS: false,
    emotionalProfile: 'Theatrical and Confident',
    harmonyType: 'none',
    harmonyIntensity: 50
  });

  const [isGenerating, setIsGenerating] = useState(false);
  const [, setStatus] = useState<string | null>(null);
  const [, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<VocalAsset[]>([]);
  const [currentAsset, setCurrentAsset] = useState<VocalAsset | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [layers, setLayers] = useState<VocalLayer[]>([]);
  
  const playersRef = useRef<Map<string, { player: Tone.Player, panner: Tone.Panner }>>(new Map());
  const backingPlayerRef = useRef<Tone.Player | null>(null);
  const analyzerRef = useRef<Tone.Analyser | null>(null);
  const [visualData, setVisualData] = useState<number[]>(new Array(32).fill(0));

  useEffect(() => {
    if (!activeProject || !auth.currentUser) return;
    const q = query(
      collection(db, 'vocal_assets'),
      where('projectId', '==', activeProject.id),
      orderBy('createdAt', 'desc')
    );
    const unsubscribe = onSnapshot(q, (snapshot) => {
      const assets = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() } as VocalAsset));
      setHistory(assets);
    }, (error) => {
      handleFirestoreError(error, OperationType.GET, 'vocal_assets');
    });
    return () => unsubscribe();
  }, [activeProject]);

  useEffect(() => {
    const timer = setInterval(() => {
      if (analyzerRef.current && isPlaying) {
        const data = analyzerRef.current.getValue() as Float32Array;
        const normalizedData = Array.from(data).map(v => Math.max(0, (v + 140) / 140) * 100);
        setVisualData(normalizedData.slice(0, 32));
      } else {
        setVisualData(prev => prev.map(v => v * 0.9));
      }
    }, 50);
    return () => clearInterval(timer);
  }, [isPlaying]);

  const handlePlay = async (asset?: VocalAsset) => {
    if (isPlaying) {
      stopAll();
      setIsPlaying(false);
      return;
    }

    await Tone.start();
    stopAll();

    const analyzer = new Tone.Analyser('fft', 64);
    analyzerRef.current = analyzer;

    if (asset) {
      if (asset.urls.processed || asset.urls.dry) {
        const player = new Tone.Player(asset.urls.processed || asset.urls.dry).connect(analyzer).toDestination();
        playersRef.current.set('main', { player, panner: new Tone.Panner(0) });
        player.start();
      }
      setCurrentAsset(asset);
    } else if (layers.length > 0) {
      // Play all layers
      layers.forEach(layer => {
        const url = layer.dryWet > 0.5 ? (layer.asset.urls.processed || layer.asset.urls.dry) : layer.asset.urls.dry;
        if (url) {
          const panner = new Tone.Panner(layer.pan).connect(analyzer).toDestination();
          const player = new Tone.Player(url).connect(panner);
          player.volume.value = Tone.gainToDb(layer.volume);
          playersRef.current.set(layer.id, { player, panner });
          player.autostart = true;
        }
      });
    }

    setIsPlaying(true);
  };

  const stopAll = () => {
    playersRef.current.forEach(({ player, panner }) => {
      player.stop();
      player.dispose();
      panner.dispose();
    });
    playersRef.current.clear();
    backingPlayerRef.current?.stop();
    backingPlayerRef.current?.dispose();
    backingPlayerRef.current = null;
  };

  const addLayer = (asset: VocalAsset) => {
    setLayers(prev => [...prev, {
      id: Math.random().toString(36).substring(7),
      asset,
      volume: 0.8,
      pan: 0,
      offset: 0,
      dryWet: 0.5
    }]);
  };

  const updateLayer = (id: string, updates: Partial<VocalLayer>) => {
    setLayers(prev => prev.map(l => l.id === id ? { ...l, ...updates } : l));
  };

  const removeLayer = (id: string) => {
    setLayers(prev => prev.filter(l => l.id !== id));
  };

  const generateVocals = async () => {
    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey || !activeProject || !auth.currentUser) {
      setError("Missing configuration or active project.");
      return;
    }

    setIsGenerating(true);
    setStatus("Synthesizing Vocal Performance...");
    setError(null);

    try {
      const ai = new GoogleGenAI({ apiKey });
      
      const promptText = `ACT AS A MASTER VOCAL PRODUCER AND DIRECTOR.
        OBJECTIVE: Synthesize a highly authentic, nuanced vocal performance.
        CRITICAL INSTRUCTION: Avoid generic vocal tropes, caricatures, and stereotyping. Focus on authentic emotional delivery, natural phrasing, and the specific performer DNA provided. Do not rely on genre clichés.
        
        PERFORMER DNA:
        - Vulnerability: ${params.performerDNA.vulnerability}%
        - Raspiness: ${params.performerDNA.raspiness}%
        - Vibrato: ${params.performerDNA.vibrato}%
        - Warmth: ${params.performerDNA.warmth}%
        - Breath: ${params.performerDNA.breath}%
        - Range: ${params.vocalRange}

        EMOTIONAL PROFILE: ${params.emotionalProfile}
        HARMONY: ${params.harmonyType !== 'none' ? `Generate a ${params.harmonyType} harmony with ${params.harmonyIntensity}% intensity.` : 'None'}
        LYRICS: ${params.lyrics}
        PROMPT: ${params.prompt}`;

      const response = await withRetry(() => ai.models.generateContent({
        model: "gemini-2.5-flash-preview-tts",
        contents: promptText,
        config: {
          responseModalities: [Modality.AUDIO],
          speechConfig: {
            voiceConfig: {
              prebuiltVoiceConfig: { voiceName: 'Kore' }
            }
          }
        }
      }));

      const base64Audio = response.candidates?.[0]?.content?.parts?.[0]?.inlineData?.data;
      if (!base64Audio) throw new Error("No audio data received.");

      const binary = atob(base64Audio);
      const bytes = new Uint8Array(binary.length);
      for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
      const blob = new Blob([bytes], { type: 'audio/wav' });
      const url = URL.createObjectURL(blob);

      const newAsset: VocalAsset = {
        id: Math.random().toString(36).substring(7),
        projectId: activeProject.id,
        type: "vocal",
        meta: {
          performerDNA: params.performerDNA as unknown as Record<string, number>,
          language: "English/Spanish Slang",
          sections: [],
          emotionProfile: params.emotionalProfile
        },
        urls: {
          dry: url,
          processed: url
        },
        createdAt: new Date().toISOString(),
        authorUid: auth.currentUser.uid
      };

      await addDoc(collection(db, 'vocal_assets'), newAsset);
      addVocalAsset(newAsset);
      setStatus("Synthesis Complete!");
      setTimeout(() => setStatus(null), 2000);
    } catch (err: unknown) {
      handleFirestoreError(err, OperationType.WRITE, 'vocal_assets');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="p-8 space-y-8">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Parameters */}
        <div className="lg:col-span-4 space-y-6">
          <section className="bg-white/5 border border-white/10 rounded-3xl p-6 space-y-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-accent">
                <Settings2 size={16} />
                <h2 className="text-xs font-bold uppercase tracking-widest">Vocal Engine</h2>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] uppercase font-mono text-white/40">EMSS Mode</span>
                <button 
                  onClick={() => setParams(p => ({ ...p, isEMSS: !p.isEMSS }))}
                  className={cn(
                    "w-8 h-4 rounded-full relative transition-colors",
                    params.isEMSS ? "bg-accent" : "bg-white/10"
                  )}
                >
                  <div className={cn(
                    "absolute top-0.5 w-3 h-3 bg-white rounded-full transition-all",
                    params.isEMSS ? "left-4.5" : "left-0.5"
                  )} />
                </button>
              </div>
            </div>

            <div className="space-y-4">
              <div className="space-y-2">
                <label className="text-[10px] uppercase font-mono text-white/40">Lyrics / Text</label>
                <textarea 
                  value={params.lyrics}
                  onChange={(e) => setParams(p => ({ ...p, lyrics: e.target.value }))}
                  className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-sm focus:border-accent outline-none transition-all min-h-[120px]"
                />
              </div>

              <div className="space-y-2">
                <label className="text-[10px] uppercase font-mono text-white/40">Backing Track</label>
                <select 
                  value={params.backingTrackId}
                  onChange={(e) => setParams(p => ({ ...p, backingTrackId: e.target.value }))}
                  className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-sm focus:border-accent outline-none appearance-none"
                >
                  <option value="">No Backing Track</option>
                  {musicAssets.map(asset => (
                    <option key={asset.id} value={asset.id}>{asset.meta.genre} ({asset.meta.bpm} BPM)</option>
                  ))}
                </select>
              </div>

              <div className="pt-4 border-t border-white/10 space-y-4">
                <div className="flex items-center gap-2 text-accent/80">
                  <Layers size={14} />
                  <span className="text-[10px] font-bold uppercase tracking-widest">Harmony Generation</span>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-[10px] uppercase font-mono text-white/40">Harmony Type</label>
                    <select 
                      value={params.harmonyType}
                      onChange={(e) => setParams(p => ({ ...p, harmonyType: e.target.value }))}
                      className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-sm focus:border-accent outline-none appearance-none"
                    >
                      <option value="none">None</option>
                      <option value="3rd above">3rd Above</option>
                      <option value="3rd below">3rd Below</option>
                      <option value="5th above">5th Above</option>
                      <option value="5th below">5th Below</option>
                      <option value="octave above">Octave Above</option>
                      <option value="octave below">Octave Below</option>
                    </select>
                  </div>
                  <div className="space-y-2">
                    <label className="text-[10px] uppercase font-mono text-white/40">Intensity ({params.harmonyIntensity}%)</label>
                    <input 
                      type="range"
                      min="0"
                      max="100"
                      value={params.harmonyIntensity}
                      onChange={(e) => setParams(p => ({ ...p, harmonyIntensity: parseInt(e.target.value) }))}
                      className="w-full accent-accent mt-3"
                      disabled={params.harmonyType === 'none'}
                    />
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t border-white/10 space-y-4">
                <div className="flex items-center gap-2 text-accent/80">
                  <Layers size={14} />
                  <span className="text-[10px] font-bold uppercase tracking-widest">Performer DNA</span>
                </div>
                <div className="space-y-3">
                  {[
                    { label: 'Vulnerability', key: 'vulnerability' },
                    { label: 'Raspiness', key: 'raspiness' },
                    { label: 'Warmth', key: 'warmth' },
                    { label: 'Breath', key: 'breath' }
                  ].map((dna) => (
                    <div key={dna.key} className="space-y-1 group relative">
                      <div className="flex justify-between text-[8px] uppercase font-mono text-white/40 cursor-help">
                        <span className="border-b border-dashed border-white/20">{dna.label}</span>
                        <span>{(params.performerDNA as unknown as Record<string, number>)[dna.key]}%</span>
                      </div>
                      <div className="absolute bottom-full left-0 mb-2 w-48 p-2 bg-black border border-white/10 rounded-lg text-[10px] text-white/80 opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity z-50">
                        {DNA_DESCRIPTIONS[dna.key]}
                      </div>
                      <input 
                        type="range"
                        min="0"
                        max="100"
                        value={(params.performerDNA as unknown as Record<string, number>)[dna.key]}
                        onChange={(e) => setParams(p => ({ 
                          ...p, 
                          performerDNA: { ...p.performerDNA, [dna.key]: parseInt(e.target.value) } 
                        }))}
                        className="w-full accent-accent"
                      />
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <button
              onClick={generateVocals}
              disabled={isGenerating}
              className="w-full py-4 bg-accent text-black rounded-xl font-bold uppercase tracking-widest shadow-lg shadow-accent/20 hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {isGenerating ? <RefreshCw size={18} className="animate-spin" /> : <Mic2 size={18} />}
              {isGenerating ? 'Synthesizing...' : 'Generate Vocals'}
            </button>
          </section>
        </div>

        {/* Visualizer & History */}
        <div className="lg:col-span-8 space-y-8">
          <section className="bg-white/5 border border-white/10 rounded-3xl p-8 relative overflow-hidden">
            <div className="relative z-10 space-y-8">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-accent/20 flex items-center justify-center text-accent">
                    <Activity size={18} />
                  </div>
                  <h2 className="text-xs font-bold uppercase tracking-widest">Vocal Spectrum</h2>
                </div>
                {currentAsset && (
                  <button 
                    onClick={() => handlePlay(currentAsset)}
                    className="w-12 h-12 rounded-full bg-accent text-black flex items-center justify-center shadow-lg shadow-accent/20 hover:scale-110 transition-all"
                  >
                    {isPlaying ? <Pause size={24} /> : <Play size={24} className="ml-1" />}
                  </button>
                )}
              </div>

              <div className="h-48 flex items-end justify-between gap-1">
                {visualData.map((val, i) => (
                  <motion.div 
                    key={i}
                    animate={{ height: `${Math.max(4, val)}%` }}
                    className={cn(
                      "flex-1 rounded-t-full transition-colors",
                      val > 70 ? "bg-accent" : val > 40 ? "bg-accent/60" : "bg-accent/20"
                    )}
                  />
                ))}
              </div>

              {currentAsset && layers.length === 0 && (
                <div className="flex items-center justify-between pt-4 border-t border-white/10">
                  <div className="text-[10px] uppercase font-mono text-white/40">
                    {currentAsset.meta.emotionProfile} // {currentAsset.type}
                  </div>
                  <div className="flex gap-4">
                    <button className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest text-accent hover:text-white transition-colors">
                      <Download size={14} />
                      Export Stem
                    </button>
                  </div>
                </div>
              )}
            </div>
          </section>

          {/* Vocal Layers */}
          <section className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-white/40">
                <Layers size={16} />
                <h2 className="text-[10px] font-bold uppercase tracking-widest">Vocal Layers</h2>
              </div>
              {layers.length > 0 && (
                <button 
                  onClick={() => handlePlay()}
                  className="flex items-center gap-2 px-3 py-1.5 bg-accent/20 text-accent rounded-lg text-[10px] font-bold uppercase tracking-widest hover:bg-accent hover:text-black transition-all"
                >
                  {isPlaying ? <Pause size={14} /> : <Play size={14} />}
                  Play Layers
                </button>
              )}
            </div>
            
            {layers.length === 0 ? (
              <div className="p-6 rounded-2xl border border-dashed border-white/10 text-center">
                <p className="text-xs text-white/40 uppercase tracking-widest">No layers added. Add from history below.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {layers.map(layer => (
                  <div key={layer.id} className="p-4 rounded-2xl bg-white/5 border border-white/10 space-y-4">
                    <div className="flex items-center justify-between">
                      <h4 className="text-xs font-bold truncate">{layer.asset.meta.emotionProfile}</h4>
                      <button onClick={() => removeLayer(layer.id)} className="text-white/40 hover:text-red-500">
                        <RefreshCw size={14} className="rotate-45" />
                      </button>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="space-y-1">
                        <label className="text-[8px] uppercase font-mono text-white/40">Volume</label>
                        <input type="range" min="0" max="1" step="0.01" value={layer.volume} onChange={(e) => updateLayer(layer.id, { volume: parseFloat(e.target.value) })} className="w-full accent-accent" />
                      </div>
                      <div className="space-y-1">
                        <label className="text-[8px] uppercase font-mono text-white/40">Pan</label>
                        <input type="range" min="-1" max="1" step="0.01" value={layer.pan} onChange={(e) => updateLayer(layer.id, { pan: parseFloat(e.target.value) })} className="w-full accent-accent" />
                      </div>
                      <div className="space-y-1">
                        <label className="text-[8px] uppercase font-mono text-white/40">Timing Offset (ms)</label>
                        <input type="number" value={layer.offset} onChange={(e) => updateLayer(layer.id, { offset: parseInt(e.target.value) })} className="w-full bg-black/50 border border-white/10 rounded p-1 text-xs text-white outline-none" />
                      </div>
                      <div className="space-y-1">
                        <label className="text-[8px] uppercase font-mono text-white/40">Dry / Wet</label>
                        <input type="range" min="0" max="1" step="0.01" value={layer.dryWet} onChange={(e) => updateLayer(layer.id, { dryWet: parseFloat(e.target.value) })} className="w-full accent-accent" />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>

          <section className="space-y-4">
            <div className="flex items-center gap-2 text-white/40">
              <History size={16} />
              <h2 className="text-[10px] font-bold uppercase tracking-widest">Vocal Assets</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {history.map((asset) => (
                <div 
                  key={asset.id}
                  className={cn(
                    "p-4 rounded-2xl border transition-all flex items-center gap-4 group cursor-pointer",
                    currentAsset?.id === asset.id ? "bg-accent/10 border-accent" : "bg-white/5 border-white/10 hover:border-white/20"
                  )}
                  onClick={() => handlePlay(asset)}
                >
                  <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center text-accent group-hover:bg-accent group-hover:text-black transition-all">
                    {currentAsset?.id === asset.id && isPlaying ? <Pause size={18} /> : <Play size={18} />}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-bold truncate">{asset.meta.emotionProfile}</h4>
                    <p className="text-[10px] text-white/40 uppercase tracking-widest">{asset.type} // {new Date(asset.createdAt).toLocaleDateString()}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <button 
                      onClick={(e) => {
                        e.stopPropagation();
                        addLayer(asset);
                      }}
                      className="p-2 rounded-lg bg-white/5 hover:bg-accent hover:text-black transition-all text-white/40"
                      title="Add to Layers"
                    >
                      <Layers size={14} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
};

export default VocalEngine;
