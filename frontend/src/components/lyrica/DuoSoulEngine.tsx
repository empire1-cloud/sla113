import React, { useState } from 'react';
import { motion } from 'motion/react';
import { Users, Play, Loader2, Download, Sparkles, Mic2 } from 'lucide-react';
import { useStudioStore } from '../store/useStudioStore';
import { generateAudioWithAI } from '../services/audioService';
import { GoogleGenAI } from '@google/genai';
import { db, auth, handleFirestoreError, OperationType } from '../lib/firebase';
import { collection, addDoc, serverTimestamp } from 'firebase/firestore';

const VOICE_PROFILES = [
  { id: 'mateo', name: 'Mateo', description: 'Smooth, warm baritone', color: 'bg-blue-500' },
  { id: 'elara', name: 'Elara', description: 'Ethereal, breathy soprano', color: 'bg-purple-500' },
  { id: 'jax', name: 'Jax', description: 'Gritty, rhythmic tenor', color: 'bg-orange-500' },
  { id: 'nova', name: 'Nova', description: 'Crisp, pop-focused alto', color: 'bg-pink-500' },
];

export const DuoSoulEngine: React.FC = () => {
  const { activeProject } = useStudioStore();
  const [voice1, setVoice1] = useState(VOICE_PROFILES[0].id);
  const [voice2, setVoice2] = useState(VOICE_PROFILES[1].id);
  const [lyrics, setLyrics] = useState('[Mateo]: The city lights are fading out...\n[Elara]: But our spark is just igniting.');
  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState('');
  const [generatedAudio, setGeneratedAudio] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!activeProject || !auth.currentUser) return;
    
    setIsGenerating(true);
    setProgress('Initializing Aether-Ensemble-v2...');
    
    try {
      const apiKey = process.env.GEMINI_API_KEY || (window as any).process?.env?.API_KEY || (process.env as any).API_KEY;
      if (!apiKey) throw new Error("API Key not found. Please connect your API key.");
      
      const ai = new GoogleGenAI({ apiKey });
      
      const config = {
        voice1: VOICE_PROFILES.find(v => v.id === voice1)?.name,
        voice2: VOICE_PROFILES.find(v => v.id === voice2)?.name,
        lyrics: lyrics,
        style: 'Duet, conversational, emotional'
      };
      
      const { audioBase64, mimeType } = await generateAudioWithAI(
        ai, 
        'music', 
        config, 
        (status) => setProgress(status)
      );

      const binary = atob(audioBase64);
      const bytes = new Uint8Array(binary.length);
      for (let i = 0; i < binary.length; i++) {
        bytes[i] = binary.charCodeAt(i);
      }
      const blob = new Blob([bytes], { type: mimeType });
      const url = URL.createObjectURL(blob);
      
      setGeneratedAudio(url);
      
      // Save to project
      const assetData = {
        projectId: activeProject.id,
        title: `Duet: ${config.voice1} & ${config.voice2}`,
        type: 'vocal',
        fileUrl: url,
        createdAt: serverTimestamp(),
        authorUid: auth.currentUser.uid,
        metadata: {
          voice1: config.voice1,
          voice2: config.voice2,
          lyrics: lyrics
        }
      };
      
      await addDoc(collection(db, 'vocal_assets'), assetData);
      
    } catch (error: any) {
      console.error('Generation failed:', error);
      alert(`Generation failed: ${error.message}`);
    } finally {
      setIsGenerating(false);
      setProgress('');
    }
  };

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-display uppercase tracking-tighter text-accent flex items-center gap-3">
            <Users className="w-8 h-8" />
            Duo-Soul Engine
          </h1>
          <p className="text-white/40 text-xs font-mono uppercase tracking-widest mt-2">
            Aether-Ensemble-v2 Multi-Voice Synthesis
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          <div className="glass-panel p-6 rounded-3xl border border-white/10 space-y-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-bold uppercase tracking-widest text-white/60">Conversational Lyrics</h3>
              <Sparkles className="w-4 h-4 text-accent" />
            </div>
            
            <textarea
              value={lyrics}
              onChange={(e) => setLyrics(e.target.value)}
              className="w-full h-64 bg-black/50 border border-white/10 rounded-2xl p-6 text-sm font-mono focus:border-accent outline-none resize-none"
              placeholder="Enter lyrics. Use [VoiceName]: to assign lines..."
            />
            
            <div className="flex justify-end">
              <button
                onClick={handleGenerate}
                disabled={isGenerating || !lyrics.trim()}
                className="px-8 py-4 bg-accent text-black font-bold uppercase tracking-widest rounded-xl hover:scale-105 transition-all disabled:opacity-50 disabled:hover:scale-100 flex items-center gap-3"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    {progress || 'Generating...'}
                  </>
                ) : (
                  <>
                    <Mic2 className="w-5 h-5" />
                    Generate Duet
                  </>
                )}
              </button>
            </div>
          </div>

          {generatedAudio && (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass-panel p-6 rounded-3xl border border-accent/30 bg-accent/5"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-bold uppercase tracking-widest text-accent">Generated Duet</h3>
                <div className="flex gap-2">
                  <a 
                    href={generatedAudio} 
                    download="duet.wav"
                    className="p-2 bg-white/5 hover:bg-white/10 rounded-lg transition-colors"
                  >
                    <Download className="w-4 h-4" />
                  </a>
                </div>
              </div>
              <audio controls src={generatedAudio} className="w-full" />
            </motion.div>
          )}
        </div>

        <div className="space-y-6">
          <div className="glass-panel p-6 rounded-3xl border border-white/10">
            <h3 className="text-sm font-bold uppercase tracking-widest text-white/60 mb-6">Voice Profile 1</h3>
            <div className="space-y-3">
              {VOICE_PROFILES.map(voice => (
                <button
                  key={`v1-${voice.id}`}
                  onClick={() => setVoice1(voice.id)}
                  className={`w-full p-4 rounded-xl border text-left transition-all flex items-center gap-4 ${
                    voice1 === voice.id 
                      ? 'bg-white/10 border-white/30' 
                      : 'bg-black/20 border-white/5 hover:border-white/20'
                  }`}
                >
                  <div className={`w-3 h-3 rounded-full ${voice.color} ${voice1 === voice.id ? 'shadow-[0_0_10px_rgba(255,255,255,0.5)]' : ''}`} />
                  <div>
                    <div className="font-bold">{voice.name}</div>
                    <div className="text-[10px] text-white/40 uppercase tracking-widest">{voice.description}</div>
                  </div>
                </button>
              ))}
            </div>
          </div>

          <div className="glass-panel p-6 rounded-3xl border border-white/10">
            <h3 className="text-sm font-bold uppercase tracking-widest text-white/60 mb-6">Voice Profile 2</h3>
            <div className="space-y-3">
              {VOICE_PROFILES.map(voice => (
                <button
                  key={`v2-${voice.id}`}
                  onClick={() => setVoice2(voice.id)}
                  className={`w-full p-4 rounded-xl border text-left transition-all flex items-center gap-4 ${
                    voice2 === voice.id 
                      ? 'bg-white/10 border-white/30' 
                      : 'bg-black/20 border-white/5 hover:border-white/20'
                  }`}
                >
                  <div className={`w-3 h-3 rounded-full ${voice.color} ${voice2 === voice.id ? 'shadow-[0_0_10px_rgba(255,255,255,0.5)]' : ''}`} />
                  <div>
                    <div className="font-bold">{voice.name}</div>
                    <div className="text-[10px] text-white/40 uppercase tracking-widest">{voice.description}</div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
