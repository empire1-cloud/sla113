import React, { useState, useEffect, useRef } from 'react';
import { GoogleGenAI, Modality } from "@google/genai";
import * as Tone from 'tone';
import { motion, AnimatePresence } from 'motion/react';
import { 
  Mic2, 
  Play, 
  Square, 
  Music, 
  Settings2, 
  Sparkles, 
  History,
  Download,
  Volume2,
  Waves,
  Zap,
  Trash2,
  Plus,
  X,
  Repeat,
  Gauge,
  Activity
} from 'lucide-react';
import { cn } from '../lib/utils';
import { db, handleFirestoreError, OperationType } from '../lib/firebase';
import { collection, addDoc, query, where, onSnapshot, orderBy, deleteDoc, doc, Timestamp } from 'firebase/firestore';
import { User as FirebaseUser } from 'firebase/auth';

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY || '' });

interface EmotionalSection {
  id: string;
  name: string;
  emotion: string;
  intensity: number;
  delivery: string;
}

interface VocalDNA {
  breathiness: number;
  raspiness: number;
  vibrato: number;
  nasality: number;
  brightness: number;
}

interface GenerationHistory {
  id: string;
  lyrics: string;
  audioUrl: string;
  timestamp: Timestamp | Date;
  params: {
    prompt: string;
    timbre: string;
    ageTone: string;
    vocalRange: string;
    style: string;
    vocalDNA: VocalDNA;
    emotionalSections: EmotionalSection[];
  };
  authorUid: string;
}

interface VocalEngineProps {
  user: FirebaseUser | null;
}

export const VocalEngine: React.FC<VocalEngineProps> = ({ user }) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [lyrics, setLyrics] = useState('');
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [playbackState, setPlaybackState] = useState<'stopped' | 'playing'>('stopped');
  const [history, setHistory] = useState<GenerationHistory[]>([]);
  const [activeTab, setActiveTab] = useState<'generate' | 'history'>('generate');
  
  const playerRef = useRef<Tone.Player | null>(null);

  // Default params from user request
  const [params, setParams] = useState({
    prompt: "A Corrido about the heartache of leaving your family behind to find work in a new city, capturing the feeling of seeing their faces in the crowded streets.",
    timbre: "Gritty",
    ageTone: "Mature & Warm",
    vocalRange: "Baritone",
    style: "Corrido Vocal Technique",
    vocalDNA: {
      breathiness: 30,
      raspiness: 60,
      vibrato: 40,
      nasality: 20,
      brightness: 50,
      referenceAudio: undefined as string | undefined
    } as VocalDNA & { referenceAudio?: string },
    emotionalSections: [
      { id: '1', name: 'Verse 1', emotion: 'Melancholic', intensity: 40, delivery: 'Intimate' },
      { id: '2', name: 'Chorus', emotion: 'Passionate', intensity: 90, delivery: 'Powerful' },
      { id: '3', name: 'Verse 2', emotion: 'Nostalgic', intensity: 50, delivery: 'Storytelling' }
    ] as EmotionalSection[]
  });

  const [playbackSettings, setPlaybackSettings] = useState({
    loop: false,
    tempo: 1.0
  });

  const [visualizerData, setVisualizerData] = useState<number[]>(new Array(32).fill(0));
  const analyserRef = useRef<Tone.Analyser | null>(null);
  const animationFrameRef = useRef<number | null>(null);

  useEffect(() => {
    if (playbackState === 'playing') {
      const updateVisualizer = () => {
        if (analyserRef.current) {
          const values = analyserRef.current.getValue() as Float32Array;
          // Map values to 0-100 range for visualization
          const normalized = Array.from(values).map(v => Math.max(0, (v + 100) / 100 * 100));
          setVisualizerData(normalized.slice(0, 32));
        }
        animationFrameRef.current = requestAnimationFrame(updateVisualizer);
      };
      updateVisualizer();
    } else {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      setVisualizerData(new Array(32).fill(0));
    }
    return () => {
      if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
    };
  }, [playbackState]);

  // Fetch history from Firestore
  useEffect(() => {
    if (!user) {
      setHistory([]);
      return;
    }

    const q = query(
      collection(db, 'vocal_performances'),
      where('authorUid', '==', user.uid),
      orderBy('timestamp', 'desc')
    );

    const unsubscribe = onSnapshot(q, (snapshot) => {
      const docs = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      })) as GenerationHistory[];
      setHistory(docs);
    }, (error) => {
      handleFirestoreError(error, OperationType.LIST, 'vocal_performances');
    });

    return () => unsubscribe();
  }, [user]);

  const generateVocalPerformance = async () => {
    if (!process.env.GEMINI_API_KEY) {
      alert("Gemini API Key is missing. Please check your environment.");
      return;
    }

    if (!user) {
      alert("Please login to generate and save performances.");
      return;
    }

    setIsGenerating(true);
    setAudioUrl(null);
    setLyrics('');

    try {
      // 1. Generate Lyrics
      const emotionalContext = params.emotionalSections.map(s => 
        `${s.name}: ${s.emotion} (${s.intensity}% intensity, ${s.delivery} delivery)`
      ).join(', ');

      const lyricsResponse = await ai.models.generateContent({
        model: "gemini-3-flash-preview",
        contents: `Generate lyrics for a ${params.style} song. 
        Prompt: ${params.prompt}
        Thematic Core: heartache, struggle.
        Genre Vernacular: Corrido.
        Poetic Devices: metaphor, alliteration.
        Structure: ${params.emotionalSections.map(s => s.name).join(', ')}.
        Emotional Context per section: ${emotionalContext}`,
        config: {
          systemInstruction: "You are a professional songwriter specializing in Corridos and traditional Latin music. Write evocative, soulful lyrics."
        }
      });

      const generatedLyrics = lyricsResponse.text || "No lyrics generated.";
      setLyrics(generatedLyrics);

      // 2. Generate Vocal Performance (TTS)
      const dnaContext = `Breathiness: ${params.vocalDNA.breathiness}%, Raspiness: ${params.vocalDNA.raspiness}%, Vibrato: ${params.vocalDNA.vibrato}%, Nasality: ${params.vocalDNA.nasality}%, Brightness: ${params.vocalDNA.brightness}%`;

      const ttsResponse = await ai.models.generateContent({
        model: "gemini-2.5-flash-preview-tts",
        contents: [{ parts: [{ text: `Perform these lyrics with a ${params.timbre}, ${params.ageTone} ${params.vocalRange} voice in a ${params.style} style. 
        Vocal DNA Profile: ${dnaContext}.
        Emotional Performance Map: ${emotionalContext}.
        
        Lyrics: \n\n ${generatedLyrics}` }] }],
        config: {
          responseModalities: [Modality.AUDIO],
          speechConfig: {
            voiceConfig: {
              prebuiltVoiceConfig: { voiceName: params.vocalRange === 'Baritone' ? 'Fenrir' : 'Kore' },
            },
          },
        },
      });

      const base64Audio = ttsResponse.candidates?.[0]?.content?.parts?.[0]?.inlineData?.data;
      
      if (base64Audio) {
        const binary = atob(base64Audio);
        const bytes = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) {
          bytes[i] = binary.charCodeAt(i);
        }
        const blob = new Blob([bytes], { type: 'audio/wav' });
        const url = URL.createObjectURL(blob);
        setAudioUrl(url);

        // Save to Firestore
        try {
          await addDoc(collection(db, 'vocal_performances'), {
            id: Math.random().toString(36).substring(7), // client-side ID for reference
            lyrics: generatedLyrics,
            audioUrl: url, // Note: In a real app, you'd upload this to Storage first
            timestamp: Timestamp.now(),
            params: { ...params },
            authorUid: user.uid
          });
        } catch (error) {
          handleFirestoreError(error, OperationType.CREATE, 'vocal_performances');
        }

        // Setup Tone.js Player
        if (playerRef.current) {
          playerRef.current.dispose();
        }
        if (analyserRef.current) {
          analyserRef.current.dispose();
        }
        
        analyserRef.current = new Tone.Analyser("fft", 64);
        playerRef.current = new Tone.Player(url).connect(analyserRef.current).toDestination();
        playerRef.current.loop = playbackSettings.loop;
        playerRef.current.playbackRate = playbackSettings.tempo;
      }

    } catch (error) {
      console.error("Error generating vocal performance:", error);
    } finally {
      setIsGenerating(false);
    }
  };

  const deletePerformance = async (id: string) => {
    try {
      await deleteDoc(doc(db, 'vocal_performances', id));
    } catch (error) {
      handleFirestoreError(error, OperationType.DELETE, `vocal_performances/${id}`);
    }
  };

  const handlePlayback = async () => {
    if (!playerRef.current) return;

    if (playbackState === 'playing') {
      playerRef.current.stop();
      setPlaybackState('stopped');
    } else {
      await Tone.start();
      playerRef.current.loop = playbackSettings.loop;
      playerRef.current.playbackRate = playbackSettings.tempo;
      playerRef.current.start();
      setPlaybackState('playing');
      
      playerRef.current.onstop = () => {
        setPlaybackState('stopped');
      };
    }
  };

  const addEmotionalSection = () => {
    const newSection: EmotionalSection = {
      id: Math.random().toString(36).substring(7),
      name: `Section ${params.emotionalSections.length + 1}`,
      emotion: 'Neutral',
      intensity: 50,
      delivery: 'Natural'
    };
    setParams(p => ({ ...p, emotionalSections: [...p.emotionalSections, newSection] }));
  };

  const removeEmotionalSection = (id: string) => {
    setParams(p => ({ ...p, emotionalSections: p.emotionalSections.filter(s => s.id !== id) }));
  };

  const updateEmotionalSection = (id: string, updates: Partial<EmotionalSection>) => {
    setParams(p => ({
      ...p,
      emotionalSections: p.emotionalSections.map(s => s.id === id ? { ...s, ...updates } : s)
    }));
  };

  const updateVocalDNA = (key: keyof VocalDNA | 'referenceAudio', value: number | string | undefined) => {
    setParams(p => ({
      ...p,
      vocalDNA: { ...p.vocalDNA, [key]: value }
    }));
  };

  const handleReferenceUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const base64 = event.target?.result as string;
      updateVocalDNA('referenceAudio', base64);
    };
    reader.readAsDataURL(file);
  };

  const analyzeReferenceAudio = async () => {
    if (!params.vocalDNA.referenceAudio) return;
    
    setIsGenerating(true);
    try {
      const base64Data = params.vocalDNA.referenceAudio.split(',')[1];
      const response = await ai.models.generateContent({
        model: "gemini-3-flash-preview",
        contents: [
          {
            inlineData: {
              data: base64Data,
              mimeType: "audio/mpeg"
            }
          },
          {
            text: "Analyze this vocal reference and provide a JSON object with the following characteristics (0-100): breathiness, raspiness, vibrato, nasality, brightness. Also suggest a timbre, ageTone, and vocalRange."
          }
        ],
        config: {
          responseMimeType: "application/json"
        }
      });

      const result = JSON.parse(response.text || '{}');
      setParams(p => ({
        ...p,
        timbre: result.timbre || p.timbre,
        ageTone: result.ageTone || p.ageTone,
        vocalRange: result.vocalRange || p.vocalRange,
        vocalDNA: {
          ...p.vocalDNA,
          breathiness: result.breathiness ?? p.vocalDNA.breathiness,
          raspiness: result.raspiness ?? p.vocalDNA.raspiness,
          vibrato: result.vibrato ?? p.vocalDNA.vibrato,
          nasality: result.nasality ?? p.vocalDNA.nasality,
          brightness: result.brightness ?? p.vocalDNA.brightness,
        }
      }));
    } catch (error) {
      console.error("Error analyzing reference audio:", error);
    } finally {
      setIsGenerating(false);
    }
  };

  useEffect(() => {
    if (playerRef.current) {
      playerRef.current.loop = playbackSettings.loop;
      playerRef.current.playbackRate = playbackSettings.tempo;
    }
  }, [playbackSettings]);

  return (
    <div className="flex flex-col gap-6 max-w-5xl mx-auto p-4 md:p-8">
      {/* Header Section */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-4xl font-display uppercase tracking-tighter text-accent">
            Vocal-Lyrical Engine
          </h2>
          <p className="text-text-secondary text-sm font-mono uppercase tracking-widest mt-1">
            Soulfire Update v2.4 // Neural Performance Synthesis
          </p>
        </div>
        
        <div className="flex gap-2 bg-card p-1 rounded-lg border border-white/5">
          <button 
            onClick={() => setActiveTab('generate')}
            className={cn(
              "px-4 py-2 rounded-md text-xs font-bold uppercase transition-all",
              activeTab === 'generate' ? "bg-accent text-white" : "text-text-secondary hover:text-white"
            )}
          >
            Generate
          </button>
          <button 
            onClick={() => setActiveTab('history')}
            className={cn(
              "px-4 py-2 rounded-md text-xs font-bold uppercase transition-all",
              activeTab === 'history' ? "bg-accent text-white" : "text-text-secondary hover:text-white"
            )}
          >
            History ({history.length})
          </button>
        </div>
      </div>

      <AnimatePresence mode="wait">
        {activeTab === 'generate' ? (
          <motion.div 
            key="generate"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="grid grid-cols-1 lg:grid-cols-3 gap-6"
          >
            {/* Controls Panel */}
            <div className="lg:col-span-1 flex flex-col gap-4">
              <div className="widget-container p-6 rounded-2xl flex flex-col gap-6">
                <div className="flex items-center justify-between text-accent">
                  <div className="flex items-center gap-2">
                    <Settings2 size={18} />
                    <span className="text-xs font-bold uppercase tracking-widest">Parameters</span>
                  </div>
                </div>

                <div className="space-y-6">
                  <div className="space-y-2">
                    <label className="status-label">Lyrical Prompt</label>
                    <textarea 
                      value={params.prompt}
                      onChange={(e) => setParams(p => ({ ...p, prompt: e.target.value }))}
                      className="w-full bg-black/40 border border-white/10 rounded-xl p-3 text-sm text-text-primary focus:border-accent outline-none transition-all h-24 resize-none"
                      placeholder="Describe the story or theme..."
                    />
                  </div>

                  {/* Vocal DNA Kit */}
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 text-text-secondary">
                        <Zap size={14} className="text-accent" />
                        <span className="text-[10px] font-bold uppercase tracking-widest">Vocal DNA Kit</span>
                      </div>
                      <label className="cursor-pointer p-1 hover:bg-white/5 rounded text-accent transition-colors">
                        <Mic2 size={14} />
                        <input type="file" accept="audio/*" className="hidden" onChange={handleReferenceUpload} />
                      </label>
                    </div>

                    {params.vocalDNA.referenceAudio && (
                      <div className="p-2 bg-accent/10 border border-accent/20 rounded-lg flex items-center justify-between">
                        <span className="text-[9px] font-mono text-accent uppercase">Reference Loaded</span>
                        <button 
                          onClick={analyzeReferenceAudio}
                          className="text-[9px] font-bold text-white bg-accent px-2 py-1 rounded hover:bg-accent/80 transition-colors"
                        >
                          Analyze
                        </button>
                      </div>
                    )}

                    <div className="grid grid-cols-1 gap-3">
                      {Object.entries(params.vocalDNA).map(([key, value]) => {
                        if (key === 'referenceAudio') return null;
                        return (
                          <div key={key} className="space-y-1">
                            <div className="flex justify-between text-[9px] uppercase font-mono text-text-secondary">
                              <span>{key}</span>
                              <span>{value}%</span>
                            </div>
                            <input 
                              type="range" 
                              min="0" 
                              max="100" 
                              value={value as number}
                              onChange={(e) => updateVocalDNA(key as keyof VocalDNA, parseInt(e.target.value))}
                              className="w-full h-1 bg-white/10 rounded-full appearance-none cursor-pointer accent-accent"
                            />
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Emotional Performance Director */}
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 text-text-secondary">
                        <Activity size={14} className="text-accent" />
                        <span className="text-[10px] font-bold uppercase tracking-widest">Emotional Director</span>
                      </div>
                      <button 
                        onClick={addEmotionalSection}
                        className="p-1 hover:bg-white/5 rounded text-accent transition-colors"
                      >
                        <Plus size={14} />
                      </button>
                    </div>
                    <div className="space-y-3 max-h-48 overflow-y-auto custom-scrollbar pr-2">
                      {params.emotionalSections.map((section) => (
                        <div key={section.id} className="p-3 bg-white/5 rounded-xl border border-white/5 space-y-2 relative group">
                          <button 
                            onClick={() => removeEmotionalSection(section.id)}
                            className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 text-text-secondary hover:text-red-500 transition-all"
                          >
                            <X size={12} />
                          </button>
                          <input 
                            type="text"
                            value={section.name}
                            onChange={(e) => updateEmotionalSection(section.id, { name: e.target.value })}
                            className="bg-transparent text-[10px] font-bold uppercase outline-none w-full border-b border-white/10 pb-1"
                          />
                          <div className="grid grid-cols-2 gap-2">
                            <select 
                              value={section.emotion}
                              onChange={(e) => updateEmotionalSection(section.id, { emotion: e.target.value })}
                              className="bg-black/40 border border-white/10 rounded-md p-1 text-[9px] outline-none"
                            >
                              <option>Neutral</option>
                              <option>Melancholic</option>
                              <option>Passionate</option>
                              <option>Aggressive</option>
                              <option>Joyful</option>
                              <option>Nostalgic</option>
                              <option>Desperate</option>
                              <option>Hopeful</option>
                              <option>Sarcastic</option>
                              <option>Ethereal</option>
                              <option>Haunting</option>
                            </select>
                            <select 
                              value={section.delivery}
                              onChange={(e) => updateEmotionalSection(section.id, { delivery: e.target.value })}
                              className="bg-black/40 border border-white/10 rounded-md p-1 text-[9px] outline-none"
                            >
                              <option>Natural</option>
                              <option>Intimate</option>
                              <option>Powerful</option>
                              <option>Storytelling</option>
                              <option>Whispered</option>
                              <option>Shouted</option>
                              <option>Staccato</option>
                              <option>Legato</option>
                              <option>Theatrical</option>
                            </select>
                          </div>
                          <div className="space-y-1">
                            <div className="flex justify-between text-[8px] uppercase font-mono text-text-secondary">
                              <span>Intensity</span>
                              <span>{section.intensity}%</span>
                            </div>
                            <input 
                              type="range" 
                              min="0" 
                              max="100" 
                              value={section.intensity}
                              onChange={(e) => updateEmotionalSection(section.id, { intensity: parseInt(e.target.value) })}
                              className="w-full h-1 bg-white/10 rounded-full appearance-none cursor-pointer accent-accent"
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label className="status-label">Timbre</label>
                      <select 
                        value={params.timbre}
                        onChange={(e) => setParams(p => ({ ...p, timbre: e.target.value }))}
                        className="w-full bg-black/40 border border-white/10 rounded-xl p-2 text-xs text-text-primary outline-none"
                      >
                        <option>Gritty</option>
                        <option>Smooth</option>
                        <option>Breathy</option>
                        <option>Piercing</option>
                      </select>
                    </div>
                    <div className="space-y-2">
                      <label className="status-label">Vocal Range</label>
                      <select 
                        value={params.vocalRange}
                        onChange={(e) => setParams(p => ({ ...p, vocalRange: e.target.value }))}
                        className="w-full bg-black/40 border border-white/10 rounded-xl p-2 text-xs text-text-primary outline-none"
                      >
                        <option>Baritone</option>
                        <option>Tenor</option>
                        <option>Soprano</option>
                        <option>Alto</option>
                      </select>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label className="status-label">Performance Style</label>
                    <input 
                      type="text"
                      value={params.style}
                      onChange={(e) => setParams(p => ({ ...p, style: e.target.value }))}
                      className="w-full bg-black/40 border border-white/10 rounded-xl p-2 text-xs text-text-primary outline-none"
                    />
                  </div>
                </div>

                <button 
                  onClick={generateVocalPerformance}
                  disabled={isGenerating}
                  className={cn(
                    "w-full py-4 rounded-xl flex items-center justify-center gap-3 transition-all font-bold uppercase tracking-widest text-sm",
                    isGenerating 
                      ? "bg-white/5 text-text-secondary cursor-not-allowed" 
                      : "bg-accent text-white hover:scale-[1.02] active:scale-[0.98] shadow-lg shadow-accent/20"
                  )}
                >
                  {isGenerating ? (
                    <>
                      <Sparkles className="animate-spin" size={18} />
                      Synthesizing...
                    </>
                  ) : (
                    <>
                      <Zap size={18} />
                      Generate Performance
                    </>
                  )}
                </button>
              </div>

              {/* Status Widget */}
              <div className="widget-container p-4 rounded-2xl border-dashed border-white/10">
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-3">
                    <div className={cn(
                      "w-2 h-2 rounded-full",
                      isGenerating ? "bg-accent animate-pulse" : "bg-green-500"
                    )} />
                    <span className="status-label">Engine Status: {isGenerating ? 'Active' : 'Ready'}</span>
                  </div>
                  <span className="timer-display">00:00:00</span>
                </div>
              </div>
            </div>

            {/* Output Panel */}
            <div className="lg:col-span-2 flex flex-col gap-4">
              <div className="widget-container rounded-2xl flex-1 flex flex-col overflow-hidden">
                <div className="p-4 border-b border-white/5 flex justify-between items-center bg-white/2">
                  <div className="flex items-center gap-2">
                    <Waves size={16} className="text-accent" />
                    <span className="text-xs font-bold uppercase tracking-widest">Neural Output</span>
                  </div>
                  {audioUrl && (
                    <div className="flex gap-2">
                      <button className="p-2 hover:bg-white/5 rounded-lg text-text-secondary transition-colors">
                        <Download size={16} />
                      </button>
                    </div>
                  )}
                </div>

                <div className="flex-1 p-6 overflow-y-auto custom-scrollbar">
                  {isGenerating ? (
                    <div className="h-full flex flex-col items-center justify-center gap-4 text-text-secondary">
                      <div className="flex gap-1 items-end h-8">
                        {[...Array(5)].map((_, i) => (
                          <motion.div 
                            key={i}
                            animate={{ height: [8, 32, 8] }}
                            transition={{ duration: 0.6, repeat: Infinity, delay: i * 0.1 }}
                            className="w-1 bg-accent rounded-full"
                          />
                        ))}
                      </div>
                      <p className="text-xs font-mono uppercase tracking-widest">Analyzing Lyrical Structures...</p>
                    </div>
                  ) : lyrics ? (
                    <motion.div 
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="space-y-6"
                    >
                      <div className="prose prose-invert max-w-none">
                        <pre className="font-sans text-lg leading-relaxed text-white/90 whitespace-pre-wrap italic">
                          {lyrics}
                        </pre>
                      </div>
                    </motion.div>
                  ) : (
                    <div className="h-full flex flex-col items-center justify-center gap-4 text-text-secondary opacity-30">
                      <Mic2 size={48} strokeWidth={1} />
                      <p className="text-xs font-mono uppercase tracking-widest">Awaiting Generation Signal</p>
                    </div>
                  )}
                </div>

                {/* Player Bar */}
                <div className="p-6 bg-black/40 border-t border-white/5">
                  <div className="flex flex-col gap-6">
                    {/* Visualizer */}
                    <div className="flex items-center justify-center h-16 gap-[2px] px-2 bg-black/20 rounded-xl border border-white/5 overflow-hidden">
                      {visualizerData.map((v, i) => (
                        <motion.div 
                          key={i}
                          animate={{ 
                            height: `${Math.max(10, v)}%`,
                            backgroundColor: playbackState === 'playing' 
                              ? `rgba(242, 125, 38, ${0.3 + (v/100) * 0.7})` 
                              : "rgba(255, 255, 255, 0.05)"
                          }}
                          className="w-full rounded-full"
                        />
                      ))}
                    </div>

                    <div className="flex items-center gap-6">
                      <button 
                        onClick={handlePlayback}
                        disabled={!audioUrl}
                        className={cn(
                          "w-14 h-14 rounded-full flex items-center justify-center transition-all shrink-0",
                          !audioUrl 
                            ? "bg-white/5 text-text-secondary cursor-not-allowed" 
                            : "bg-white text-black hover:scale-110 active:scale-95 shadow-xl shadow-white/10"
                        )}
                      >
                        {playbackState === 'playing' ? <Square fill="currentColor" size={24} /> : <Play fill="currentColor" size={24} className="ml-1" />}
                      </button>

                      <div className="flex-1 space-y-3">
                        <div className="flex justify-between text-[10px] font-mono text-text-secondary uppercase tracking-widest">
                          <div className="flex gap-4">
                            <span className={cn(playbackState === 'playing' && "text-accent")}>
                              {playbackState === 'playing' ? 'Synthesizing Audio' : 'Idle'}
                            </span>
                            <span>48kHz / 24-bit</span>
                          </div>
                          <div className="flex gap-4 items-center">
                            <button 
                              onClick={() => setPlaybackSettings(s => ({ ...s, loop: !s.loop }))}
                              className={cn(
                                "flex items-center gap-1 transition-colors",
                                playbackSettings.loop ? "text-accent" : "hover:text-white"
                              )}
                            >
                              <Repeat size={12} />
                              <span>Loop</span>
                            </button>
                            <div className="flex items-center gap-2">
                              <Gauge size={12} />
                              <select 
                                value={playbackSettings.tempo}
                                onChange={(e) => setPlaybackSettings(s => ({ ...s, tempo: parseFloat(e.target.value) }))}
                                className="bg-transparent outline-none cursor-pointer hover:text-white"
                              >
                                <option value="0.5">0.5x</option>
                                <option value="0.75">0.75x</option>
                                <option value="1.0">1.0x</option>
                                <option value="1.25">1.25x</option>
                                <option value="1.5">1.5x</option>
                                <option value="2.0">2.0x</option>
                              </select>
                            </div>
                          </div>
                        </div>
                        <div className="h-1 bg-white/10 rounded-full overflow-hidden">
                          <motion.div 
                            className="h-full bg-accent"
                            initial={{ width: 0 }}
                            animate={{ width: playbackState === 'playing' ? '100%' : '0%' }}
                            transition={{ duration: 30, ease: "linear" }}
                          />
                        </div>
                      </div>

                      <div className="flex items-center gap-2 text-text-secondary shrink-0">
                        <Volume2 size={18} />
                        <div className="w-20 h-1 bg-white/10 rounded-full">
                          <div className="w-2/3 h-full bg-white/40 rounded-full" />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        ) : (
          <motion.div 
            key="history"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
          >
            {history.length === 0 ? (
              <div className="col-span-full h-64 flex flex-col items-center justify-center gap-4 text-text-secondary opacity-30">
                <History size={48} strokeWidth={1} />
                <p className="text-xs font-mono uppercase tracking-widest">No previous sessions found</p>
              </div>
            ) : (
              history.map((item) => (
                <div key={item.id} className="widget-container p-5 rounded-2xl hover:border-accent/30 transition-all group">
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 rounded-lg bg-accent/10 flex items-center justify-center text-accent">
                        <Music size={16} />
                      </div>
                      <div>
                        <h4 className="text-xs font-bold uppercase tracking-tight">Performance #{item.id.substring(0, 6)}</h4>
                        <p className="text-[10px] text-text-secondary font-mono">
                          {item.timestamp instanceof Timestamp ? item.timestamp.toDate().toLocaleTimeString() : new Date(item.timestamp).toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button 
                        onClick={() => {
                          setLyrics(item.lyrics);
                          setAudioUrl(item.audioUrl);
                          setParams(item.params);
                          setActiveTab('generate');
                          // Re-setup player
                          if (playerRef.current) playerRef.current.dispose();
                          playerRef.current = new Tone.Player(item.audioUrl).toDestination();
                        }}
                        className="text-[10px] font-bold uppercase text-accent hover:underline"
                      >
                        Load
                      </button>
                      <button 
                        onClick={() => deletePerformance(item.id)}
                        className="text-text-secondary hover:text-red-500 transition-colors"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </div>
                  <p className="text-xs text-text-secondary line-clamp-3 italic mb-4">
                    "{item.lyrics.substring(0, 100)}..."
                  </p>
                  <div className="flex gap-2">
                    <span className="px-2 py-1 bg-white/5 rounded text-[9px] font-mono text-text-secondary uppercase">{item.params.timbre}</span>
                    <span className="px-2 py-1 bg-white/5 rounded text-[9px] font-mono text-text-secondary uppercase">{item.params.vocalRange}</span>
                  </div>
                </div>
              ))
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
