import { useState } from 'react';
import { Music2, Zap, Sparkles } from 'lucide-react';
import QuickGenerateMode from '../components/empire/QuickGenerateMode';
import StudioProMode from '../components/empire/StudioProMode';
import DuoSoulMode from '../components/empire/DuoSoulMode';

/**
 * Empire Lyric Master - Main Page
 * 
 * Three modes for different workflows:
 * 1. Quick Generate - Fast prompt → track
 * 2. Studio Pro - Full production interface
 * 3. DuoSoul - Adapted from prototype with Empire backend
 */
export default function EmpireLyricMasterPage() {
  const [activeMode, setActiveMode] = useState('quick'); // 'quick' | 'studio' | 'duo'

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-slate-900 to-black">
      {/* Header */}
      <div className="border-b border-purple-500/20 bg-black/40 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                <Music2 className="w-8 h-8 text-purple-400" />
                Empire Lyric Master
              </h1>
              <p className="text-purple-200/60 mt-1">
                Zero-API Music Production • 100% Local • &lt;5ms Generation
              </p>
            </div>
            
            {/* Mode Selector */}
            <div className="flex gap-2 bg-black/60 backdrop-blur-sm rounded-lg p-1 border border-purple-500/30">
              <button
                onClick={() => setActiveMode('quick')}
                className={`px-4 py-2 rounded-md transition-all flex items-center gap-2 ${
                  activeMode === 'quick'
                    ? 'bg-purple-600 text-white shadow-lg shadow-purple-500/50'
                    : 'text-purple-300 hover:bg-purple-900/50'
                }`}
              >
                <Zap className="w-4 h-4" />
                Quick
              </button>
              <button
                onClick={() => setActiveMode('studio')}
                className={`px-4 py-2 rounded-md transition-all flex items-center gap-2 ${
                  activeMode === 'studio'
                    ? 'bg-purple-600 text-white shadow-lg shadow-purple-500/50'
                    : 'text-purple-300 hover:bg-purple-900/50'
                }`}
              >
                <Music2 className="w-4 h-4" />
                Studio Pro
              </button>
              <button
                onClick={() => setActiveMode('duo')}
                className={`px-4 py-2 rounded-md transition-all flex items-center gap-2 ${
                  activeMode === 'duo'
                    ? 'bg-purple-600 text-white shadow-lg shadow-purple-500/50'
                    : 'text-purple-300 hover:bg-purple-900/50'
                }`}
              >
                <Sparkles className="w-4 h-4" />
                DuoSoul
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Mode Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeMode === 'quick' && <QuickGenerateMode />}
        {activeMode === 'studio' && <StudioProMode />}
        {activeMode === 'duo' && <DuoSoulMode />}
      </div>

      {/* Footer Stats */}
      <div className="fixed bottom-0 left-0 right-0 bg-black/60 backdrop-blur-sm border-t border-purple-500/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <div className="flex items-center justify-between text-sm">
            <div className="flex gap-6 text-purple-200/60">
              <span>💰 API Cost: $0</span>
              <span>⚡ Local Processing</span>
              <span>🌍 20+ Genres</span>
            </div>
            <div className="text-purple-200/40">
              Built by a solo mama builder • This is YOUR lane
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
