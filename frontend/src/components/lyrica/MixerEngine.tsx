import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'motion/react';
import { 
  Volume2, 
  Play, 
  Pause, 
  Download, 
  Save,
  Sliders,
  Music,
  Mic2,
  Waves,
  Zap
} from 'lucide-react';
import { cn } from '../lib/utils';
import * as Tone from 'tone';
import { useStudioStore } from '../store/useStudioStore';

interface ChannelStrip {
  id: string;
  name: string;
  volume: number;
  pan: number;
  mute: boolean;
  solo: boolean;
  type: 'music' | 'vocal' | 'sfx' | 'ambient';
  assetId: string;
}

const MixerEngine: React.FC = () => {
  const { musicAssets, vocalAssets, sfxAssets, ambientAssets } = useStudioStore();
  const [isPlaying, setIsPlaying] = useState(false);
  const [masterVolume, setMasterVolume] = useState(0);
  const [channelVolumes, setChannelVolumes] = useState<Record<string, number>>({});
  
  const playersRef = useRef<{ [key: string]: Tone.Player }>({});
  const volumesRef = useRef<{ [key: string]: Tone.Volume }>({});
  const analyzerRef = useRef<Tone.Analyser | null>(null);
  const [visualData, setVisualData] = useState<number[]>(new Array(32).fill(0));

  const channels = React.useMemo(() => {
    const newChannels: ChannelStrip[] = [];
    
    musicAssets.forEach(asset => {
      if (asset.urls.drums) newChannels.push({ id: `${asset.id}-drums`, name: 'Drums', volume: channelVolumes[`${asset.id}-drums`] ?? -6, pan: 0, mute: false, solo: false, type: 'music', assetId: asset.id });
      if (asset.urls.bass) newChannels.push({ id: `${asset.id}-bass`, name: 'Bass', volume: channelVolumes[`${asset.id}-bass`] ?? -6, pan: 0, mute: false, solo: false, type: 'music', assetId: asset.id });
      if (asset.urls.melody) newChannels.push({ id: `${asset.id}-melody`, name: 'Melody', volume: channelVolumes[`${asset.id}-melody`] ?? -6, pan: 0, mute: false, solo: false, type: 'music', assetId: asset.id });
      if (asset.urls.atmosphere) newChannels.push({ id: `${asset.id}-atmos`, name: 'Atmos', volume: channelVolumes[`${asset.id}-atmos`] ?? -6, pan: 0, mute: false, solo: false, type: 'music', assetId: asset.id });
    });

    vocalAssets.forEach(asset => {
      newChannels.push({ id: asset.id, name: 'Vocals', volume: channelVolumes[asset.id] ?? 0, pan: 0, mute: false, solo: false, type: 'vocal', assetId: asset.id });
    });

    sfxAssets.forEach(asset => {
      newChannels.push({ id: asset.id, name: 'SFX', volume: channelVolumes[asset.id] ?? 0, pan: 0, mute: false, solo: false, type: 'sfx', assetId: asset.id });
    });

    ambientAssets.forEach(asset => {
      newChannels.push({ id: asset.id, name: 'Ambient', volume: channelVolumes[asset.id] ?? 0, pan: 0, mute: false, solo: false, type: 'ambient', assetId: asset.id });
    });

    return newChannels;
  }, [musicAssets, vocalAssets, sfxAssets, ambientAssets, channelVolumes]);

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

  const handleTogglePlay = async () => {
    if (isPlaying) {
      Tone.Transport.stop();
      setIsPlaying(false);
      return;
    }

    await Tone.start();
    
    // Setup players if not already setup
    channels.forEach(ch => {
      if (!playersRef.current[ch.id]) {
        let url = '';
        if (ch.type === 'music') {
          const asset = musicAssets.find(a => a.id === ch.assetId);
          if (ch.name === 'Drums') url = asset?.urls.drums || '';
          else if (ch.name === 'Bass') url = asset?.urls.bass || '';
          else if (ch.name === 'Melody') url = asset?.urls.melody || '';
          else if (ch.name === 'Atmos') url = asset?.urls.atmosphere || '';
        } else if (ch.type === 'vocal') {
          const asset = vocalAssets.find(a => a.id === ch.assetId);
          url = asset?.urls.processed || asset?.urls.dry || '';
        } else if (ch.type === 'sfx') {
          const asset = sfxAssets.find(a => a.id === ch.assetId);
          url = asset?.urls.main || '';
        } else if (ch.type === 'ambient') {
          const asset = ambientAssets.find(a => a.id === ch.assetId);
          url = asset?.urls.main || '';
        }

        if (url) {
          const vol = new Tone.Volume(ch.volume).toDestination();
          const player = new Tone.Player(url).connect(vol);
          player.loop = true;
          playersRef.current[ch.id] = player;
          volumesRef.current[ch.id] = vol;
        }
      }
    });

    if (!analyzerRef.current) {
      analyzerRef.current = new Tone.Analyser('fft', 64);
      Tone.Destination.connect(analyzerRef.current);
    }

    Object.values(playersRef.current).forEach(p => p.start(0));
    Tone.Transport.start();
    setIsPlaying(true);
  };

  const updateVolume = (id: string, val: number) => {
    setChannelVolumes(prev => ({ ...prev, [id]: val }));
    if (volumesRef.current[id]) {
      volumesRef.current[id].volume.value = val;
    }
  };

  return (
    <div className="p-8 space-y-8">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-accent/20 flex items-center justify-center text-accent">
            <Sliders size={24} />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight">Studio Mixer</h1>
            <p className="text-xs text-white/40 uppercase tracking-widest">Multi-Stem Summing Engine</p>
          </div>
        </div>

        <div className="flex items-center gap-6">
          <div className="flex items-center gap-4 bg-white/5 border border-white/10 rounded-2xl px-6 py-3">
            <Volume2 size={16} className="text-white/40" />
            <input 
              type="range"
              min="-60"
              max="6"
              value={masterVolume}
              onChange={(e) => {
                const val = parseInt(e.target.value);
                setMasterVolume(val);
                Tone.Destination.volume.value = val;
              }}
              className="w-32 accent-accent"
            />
          </div>
          
          <button
            onClick={handleTogglePlay}
            className="w-14 h-14 rounded-full bg-accent text-black flex items-center justify-center shadow-lg shadow-accent/20 hover:scale-110 active:scale-95 transition-all"
          >
            {isPlaying ? <Pause size={28} /> : <Play size={28} className="ml-1" />}
          </button>
        </div>
      </div>

      {/* Visualizer */}
      <section className="bg-white/5 border border-white/10 rounded-3xl p-8 h-48 flex items-end justify-between gap-1">
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
      </section>

      {/* Mixer Console */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-4">
        {channels.map((ch) => (
          <div key={ch.id} className="bg-white/5 border border-white/10 rounded-3xl p-4 flex flex-col items-center gap-6 group">
            <div className="w-full flex justify-between items-center text-[10px] uppercase font-mono text-white/40">
              <span className="truncate max-w-[60px]">{ch.name}</span>
              <span className={cn(ch.volume > 0 ? "text-accent" : "")}>{ch.volume}dB</span>
            </div>

            <div className="flex-1 w-full flex flex-col items-center gap-4 py-4">
              <div className="relative h-48 w-1.5 bg-white/10 rounded-full overflow-hidden">
                <div 
                  className="absolute bottom-0 w-full bg-accent transition-all"
                  style={{ height: `${((ch.volume + 60) / 66) * 100}%` }}
                />
                <input 
                  type="range"
                  min="-60"
                  max="6"
                  step="0.1"
                  value={ch.volume}
                  onChange={(e) => updateVolume(ch.id, parseFloat(e.target.value))}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-ns-resize"
                  style={{ writingMode: 'vertical-lr' } as React.CSSProperties}
                />
              </div>
              
              <div className="flex gap-2">
                <button className={cn(
                  "w-8 h-8 rounded-lg text-[10px] font-bold border transition-all",
                  ch.mute ? "bg-red-500/20 border-red-500 text-red-500" : "bg-white/5 border-white/10 text-white/40"
                )}>M</button>
                <button className={cn(
                  "w-8 h-8 rounded-lg text-[10px] font-bold border transition-all",
                  ch.solo ? "bg-yellow-500/20 border-yellow-500 text-yellow-500" : "bg-white/5 border-white/10 text-white/40"
                )}>S</button>
              </div>
            </div>

            <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center text-accent/40 group-hover:text-accent transition-colors">
              {ch.type === 'music' && <Music size={18} />}
              {ch.type === 'vocal' && <Mic2 size={18} />}
              {ch.type === 'sfx' && <Zap size={18} />}
              {ch.type === 'ambient' && <Waves size={18} />}
            </div>
          </div>
        ))}

        {/* Master Fader */}
        <div className="bg-accent/5 border border-accent/20 rounded-3xl p-4 flex flex-col items-center gap-6">
          <div className="w-full flex justify-between items-center text-[10px] uppercase font-mono text-accent">
            <span>Master</span>
            <span>{masterVolume}dB</span>
          </div>

          <div className="flex-1 w-full flex flex-col items-center gap-4 py-4">
            <div className="relative h-48 w-2 bg-accent/10 rounded-full overflow-hidden">
              <div 
                className="absolute bottom-0 w-full bg-accent transition-all"
                style={{ height: `${((masterVolume + 60) / 66) * 100}%` }}
              />
              <input 
                type="range"
                min="-60"
                max="6"
                step="0.1"
                value={masterVolume}
                onChange={(e) => {
                  const val = parseFloat(e.target.value);
                  setMasterVolume(val);
                  Tone.Destination.volume.value = val;
                }}
                className="absolute inset-0 w-full h-full opacity-0 cursor-ns-resize"
                style={{ writingMode: 'vertical-lr' } as React.CSSProperties}
              />
            </div>
          </div>

          <div className="w-10 h-10 rounded-xl bg-accent text-black flex items-center justify-center">
            <Waves size={18} />
          </div>
        </div>
      </div>

      <div className="flex justify-end gap-4">
        <button className="px-8 py-4 bg-white/5 border border-white/10 rounded-2xl text-xs font-bold uppercase tracking-widest hover:bg-white/10 transition-all flex items-center gap-2">
          <Save size={16} />
          Save Mix State
        </button>
        <button className="px-8 py-4 bg-accent text-black rounded-2xl text-xs font-bold uppercase tracking-widest shadow-lg shadow-accent/20 hover:scale-[1.02] active:scale-[0.98] transition-all flex items-center gap-2">
          <Download size={16} />
          Export Final Mix
        </button>
      </div>
    </div>
  );
};

export default MixerEngine;
