import React, { useState, useRef, useEffect } from 'react';
import { Play, Square, Settings2, Loader2, Download, Zap } from 'lucide-react';
import { useStudioStore } from '../store/useStudioStore';
import { SfxAsset } from '../types';
import { cn } from '../lib/utils';
import { GoogleGenAI, Modality } from '@google/genai';
import { db, auth } from '../lib/firebase';
import { collection, addDoc, query, where, orderBy, onSnapshot } from 'firebase/firestore';
import * as Tone from 'tone';

const withRetry = async <T,>(fn: () => Promise<T>, retries = 3, delay = 2000): Promise<T> => {
  try {
    return await fn();
  } catch (error) {
    if (retries === 0) throw error;
    await new Promise(resolve => setTimeout(resolve, delay));
    return withRetry(fn, retries - 1, delay * 1.5);
  }
};

interface SfxParams {
  prompt: string;
  material: string;
  mass: string;
  environment: string;
  frequency: string;
  envelope: string;
}

export const SfxEngine: React.FC = () => {
  const { activeProject, sfxAssets, addSfxAsset, setSfxAssets } = useStudioStore();
  const [params, setParams] = useState<SfxParams>({
    prompt: 'The distinct sound of a 1-ton, rusted steel bank vault door being secured by a large central lever.',
    material: 'Aged Steel',
    mass: '1000kg',
    environment: 'Subterranean Stone Chamber (Long decay/Reverb)',
    frequency: 'Low-mid rumble',
    envelope: 'Slow Attack, Long Sustain'
  });

  const [isGenerating, setIsGenerating] = useState(false);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [currentAsset, setCurrentAsset] = useState<SfxAsset | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  
  const playerRef = useRef<Tone.Player | null>(null);

  useEffect(() => {
    if (!activeProject || !auth.currentUser) return;
    const q = query(
      collection(db, 'sfx_assets'),
      where('projectId', '==', activeProject.id),
      orderBy('createdAt', 'desc')
    );
    const unsubscribe = onSnapshot(q, (snapshot) => {
      const assets = snapshot.docs.map(doc => ({ ...doc.data(), id: doc.id } as SfxAsset));
      setSfxAssets(assets);
    }, (error) => {
      console.error("Firestore Error in SfxEngine:", error);
    });
    return () => unsubscribe();
  }, [activeProject, setSfxAssets]);

  useEffect(() => {
    return () => {
      if (playerRef.current) {
        playerRef.current.dispose();
      }
    };
  }, []);

  const handlePlay = async (asset: SfxAsset) => {
    if (currentAsset?.id === asset.id && isPlaying) {
      playerRef.current?.stop();
      setIsPlaying(false);
      return;
    }

    await Tone.start();
    if (playerRef.current) {
      playerRef.current.stop();
      playerRef.current.dispose();
    }

    const player = new Tone.Player(asset.urls.main).toDestination();
    playerRef.current = player;
    player.onstop = () => setIsPlaying(false);
    
    await Tone.loaded();
    player.start();
    setCurrentAsset(asset);
    setIsPlaying(true);
  };

  const generateSfx = async () => {
    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey || !activeProject || !auth.currentUser) {
      setError("Missing configuration or active project.");
      return;
    }

    setIsGenerating(true);
    setStatus("Synthesizing SFX...");
    setError(null);

    try {
      const ai = new GoogleGenAI({ apiKey });
      const promptText = `ACT AS A MASTER SOUND DESIGNER AND FOLEY ARTIST.
        OBJECTIVE: Synthesize a high-fidelity sound effect based on precise Acoustic Modeling Parameters (AMPs).
        
        ACOUSTIC MODELING PARAMETERS:
        - Material: ${params.material}
        - Mass: ${params.mass}
        - Environment: ${params.environment}
        - Frequency Profile: ${params.frequency}
        - Envelope (ADSR): ${params.envelope}
        
        DESCRIPTION/PROMPT: ${params.prompt}
        
        OUTPUT: Generate a single, highly realistic sound effect matching these physical constraints.`;

      const response = await withRetry(() => ai.models.generateContent({
        model: "gemini-3.1-flash-audio-preview",
        contents: promptText,
        config: {
          responseModalities: [Modality.AUDIO]
        }
      }));

      const base64Audio = response.candidates?.[0]?.content?.parts?.[0]?.inlineData?.data;
      if (!base64Audio) throw new Error("No audio data received.");

      const binary = atob(base64Audio);
      const bytes = new Uint8Array(binary.length);
      for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
      const blob = new Blob([bytes], { type: 'audio/wav' });
      const url = URL.createObjectURL(blob);

      const newAsset: SfxAsset = {
        id: Math.random().toString(36).substring(7),
        projectId: activeProject.id,
        type: "sfx",
        meta: {
          material: params.material,
          mass: params.mass,
          environment: params.environment,
          frequency: params.frequency,
          envelope: params.envelope
        },
        urls: { main: url },
        createdAt: new Date().toISOString(),
        authorUid: auth.currentUser.uid
      };

      await addDoc(collection(db, 'sfx_assets'), newAsset);
      addSfxAsset(newAsset);
      setCurrentAsset(newAsset);
      setStatus("SFX Generated Successfully");
    } catch (err: unknown) {
      console.error(err);
      setError(err instanceof Error ? err.message : "Failed to generate SFX.");
    } finally {
      setIsGenerating(false);
      setTimeout(() => setStatus(null), 3000);
    }
  };

  return (
    <div className="h-full flex flex-col lg:flex-row gap-6 p-6 overflow-hidden">
      <div className="flex-1 flex flex-col gap-6 overflow-y-auto pr-2">
        <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
          <div className="flex items-center gap-3 mb-6">
            <Zap className="w-5 h-5 text-accent" />
            <h2 className="text-xl font-bold text-white tracking-tight">Foley & Acoustic Modeler</h2>
          </div>

          <div className="space-y-6">
            <div className="space-y-2">
              <label className="text-xs font-mono text-white/50 uppercase tracking-wider">SFX Description</label>
              <textarea
                value={params.prompt}
                onChange={(e) => setParams({ ...params, prompt: e.target.value })}
                className="w-full h-24 bg-black/50 border border-white/10 rounded-xl p-4 text-white text-sm focus:outline-none focus:border-accent/50 transition-colors resize-none"
                placeholder="Describe the sound effect..."
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-xs font-mono text-white/50 uppercase tracking-wider">Material</label>
                <input
                  type="text"
                  value={params.material}
                  onChange={(e) => setParams({ ...params, material: e.target.value })}
                  className="w-full bg-black/50 border border-white/10 rounded-lg p-3 text-white text-sm focus:outline-none focus:border-accent/50"
                  placeholder="e.g., Aged Steel, Pure Plasma"
                />
              </div>
              <div className="space-y-2">
                <label className="text-xs font-mono text-white/50 uppercase tracking-wider">Mass</label>
                <input
                  type="text"
                  value={params.mass}
                  onChange={(e) => setParams({ ...params, mass: e.target.value })}
                  className="w-full bg-black/50 border border-white/10 rounded-lg p-3 text-white text-sm focus:outline-none focus:border-accent/50"
                  placeholder="e.g., 1000kg, Weightless"
                />
              </div>
              <div className="space-y-2">
                <label className="text-xs font-mono text-white/50 uppercase tracking-wider">Environment</label>
                <input
                  type="text"
                  value={params.environment}
                  onChange={(e) => setParams({ ...params, environment: e.target.value })}
                  className="w-full bg-black/50 border border-white/10 rounded-lg p-3 text-white text-sm focus:outline-none focus:border-accent/50"
                  placeholder="e.g., Subterranean Stone Chamber"
                />
              </div>
              <div className="space-y-2">
                <label className="text-xs font-mono text-white/50 uppercase tracking-wider">Frequency Profile</label>
                <input
                  type="text"
                  value={params.frequency}
                  onChange={(e) => setParams({ ...params, frequency: e.target.value })}
                  className="w-full bg-black/50 border border-white/10 rounded-lg p-3 text-white text-sm focus:outline-none focus:border-accent/50"
                  placeholder="e.g., 8-12kHz peak"
                />
              </div>
              <div className="space-y-2 md:col-span-2">
                <label className="text-xs font-mono text-white/50 uppercase tracking-wider">Envelope (ADSR)</label>
                <input
                  type="text"
                  value={params.envelope}
                  onChange={(e) => setParams({ ...params, envelope: e.target.value })}
                  className="w-full bg-black/50 border border-white/10 rounded-lg p-3 text-white text-sm focus:outline-none focus:border-accent/50"
                  placeholder="e.g., Fast Attack, 0.2s Decay"
                />
              </div>
            </div>

            {error && (
              <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm">
                {error}
              </div>
            )}

            <button
              onClick={generateSfx}
              disabled={isGenerating || !activeProject}
              className="w-full py-4 bg-white text-black rounded-xl font-bold hover:bg-white/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  {status}
                </>
              ) : (
                <>
                  <Settings2 className="w-5 h-5" />
                  Synthesize SFX
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      <div className="w-full lg:w-80 flex flex-col gap-4">
        <h3 className="text-sm font-bold text-white/80 uppercase tracking-wider">SFX Library</h3>
        <div className="flex-1 overflow-y-auto space-y-2 pr-2">
          {sfxAssets.map((asset) => (
            <div 
              key={asset.id}
              className={cn(
                "p-4 rounded-xl border transition-all cursor-pointer group",
                currentAsset?.id === asset.id 
                  ? "bg-accent/10 border-accent/30" 
                  : "bg-white/5 border-white/5 hover:border-white/20"
              )}
              onClick={() => handlePlay(asset)}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-white truncate pr-4">
                  {asset.meta.material} - {asset.meta.mass}
                </span>
                <button className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center group-hover:bg-white group-hover:text-black transition-colors">
                  {currentAsset?.id === asset.id && isPlaying ? (
                    <Square className="w-4 h-4" />
                  ) : (
                    <Play className="w-4 h-4 ml-0.5" />
                  )}
                </button>
              </div>
              <div className="text-xs text-white/40 flex justify-between items-center">
                <span>{new Date(asset.createdAt).toLocaleTimeString()}</span>
                <a 
                  href={asset.urls.main} 
                  download={`sfx-${asset.id}.wav`}
                  onClick={(e) => e.stopPropagation()}
                  className="p-1 hover:text-white transition-colors"
                >
                  <Download className="w-3 h-3" />
                </a>
              </div>
            </div>
          ))}
          {sfxAssets.length === 0 && (
            <div className="text-center p-8 text-white/30 text-sm border border-dashed border-white/10 rounded-xl">
              No SFX generated yet
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
