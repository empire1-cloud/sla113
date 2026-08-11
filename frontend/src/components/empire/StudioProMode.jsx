import { useState } from 'react';
import { Music2, Sliders, FileAudio, Settings, Loader2, Play, Download } from 'lucide-react';

/**
 * Studio Pro Mode
 * 
 * Full production interface with manual controls
 * Genre selection, BPM control, vulnerability slider, etc.
 */
export default function StudioProMode() {
  const [prompt, setPrompt] = useState('');
  const [genre, setGenre] = useState('auto');
  const [bpm, setBpm] = useState(120);
  const [vulnerability, setVulnerability] = useState(0.5);
  const [isGenerating, setIsGenerating] = useState(false);
  const [result, setResult] = useState(null);
  const [activeTab, setActiveTab] = useState('lyrics'); // lyrics | midi | dsp | export

  const genres = [
    { value: 'auto', label: 'Auto-Detect' },
    { value: 'trap', label: 'Trap' },
    { value: 'drill', label: 'Drill' },
    { value: 'soul', label: 'Soul' },
    { value: 'corrido', label: 'Corrido' },
    { value: 'afrobeats', label: 'Afrobeats' },
    { value: 'uk_drill', label: 'UK Drill' },
    { value: 'kpop', label: 'K-pop' },
    { value: 'reggaeton', label: 'Reggaeton' },
    { value: 'amapiano', label: 'Amapiano' },
    { value: 'dancehall', label: 'Dancehall' },
  ];

  const handleGenerate = async () => {
    if (!prompt.trim()) return;

    setIsGenerating(true);

    try {
      const payload = {
        prompt,
        genre_override: genre !== 'auto' ? genre : undefined,
        bpm_override: bpm,
        vulnerability_override: vulnerability
      };

      const response = await fetch('/api/empire/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await response.json();
      setResult(data);
    } catch (err) {
      console.error('Generation error:', err);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Left Panel - Controls */}
      <div className="lg:col-span-1 space-y-6">
        {/* Prompt */}
        <div className="bg-black/40 backdrop-blur-sm rounded-xl border border-purple-500/30 p-6">
          <div className="flex items-center gap-2 mb-4">
            <Music2 className="w-5 h-5 text-purple-400" />
            <h3 className="text-white font-semibold">Track Concept</h3>
          </div>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe your track..."
            className="w-full h-32 bg-slate-900/50 border border-purple-500/30 rounded-lg px-3 py-2 text-white placeholder-purple-300/30 focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none text-sm"
          />
        </div>

        {/* Genre Selection */}
        <div className="bg-black/40 backdrop-blur-sm rounded-xl border border-purple-500/30 p-6">
          <div className="flex items-center gap-2 mb-4">
            <FileAudio className="w-5 h-5 text-purple-400" />
            <h3 className="text-white font-semibold">Genre</h3>
          </div>
          <select
            value={genre}
            onChange={(e) => setGenre(e.target.value)}
            className="w-full bg-slate-900/50 border border-purple-500/30 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            {genres.map(g => (
              <option key={g.value} value={g.value}>{g.label}</option>
            ))}
          </select>
        </div>

        {/* BPM Control */}
        <div className="bg-black/40 backdrop-blur-sm rounded-xl border border-purple-500/30 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Sliders className="w-5 h-5 text-purple-400" />
              <h3 className="text-white font-semibold">BPM</h3>
            </div>
            <span className="text-purple-200 font-mono text-lg">{bpm}</span>
          </div>
          <input
            type="range"
            min="60"
            max="180"
            value={bpm}
            onChange={(e) => setBpm(parseInt(e.target.value))}
            className="w-full h-2 bg-slate-900 rounded-lg appearance-none cursor-pointer accent-purple-600"
          />
          <div className="flex justify-between text-xs text-purple-200/40 mt-1">
            <span>60</span>
            <span>120</span>
            <span>180</span>
          </div>
        </div>

        {/* Vulnerability Control */}
        <div className="bg-black/40 backdrop-blur-sm rounded-xl border border-purple-500/30 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Settings className="w-5 h-5 text-purple-400" />
              <h3 className="text-white font-semibold">Vulnerability</h3>
            </div>
            <span className="text-purple-200 font-mono">
              {(vulnerability * 100).toFixed(0)}%
            </span>
          </div>
          <input
            type="range"
            min="0"
            max="1"
            step="0.01"
            value={vulnerability}
            onChange={(e) => setVulnerability(parseFloat(e.target.value))}
            className="w-full h-2 bg-slate-900 rounded-lg appearance-none cursor-pointer accent-purple-600"
          />
          <div className="flex justify-between text-xs text-purple-200/40 mt-1">
            <span>Cold</span>
            <span>Balanced</span>
            <span>Raw</span>
          </div>
        </div>

        {/* Generate Button */}
        <button
          onClick={handleGenerate}
          disabled={isGenerating || !prompt.trim()}
          className="w-full py-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 disabled:from-gray-700 disabled:to-gray-700 text-white font-semibold rounded-lg transition-all flex items-center justify-center gap-2 disabled:cursor-not-allowed"
        >
          {isGenerating ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <Play className="w-5 h-5" />
              Generate Track
            </>
          )}
        </button>
      </div>

      {/* Right Panel - Results */}
      <div className="lg:col-span-2">
        {result ? (
          <div className="bg-black/40 backdrop-blur-sm rounded-xl border border-purple-500/30 p-6">
            {/* Tabs */}
            <div className="flex gap-2 mb-6 border-b border-purple-500/20 pb-4">
              <button
                onClick={() => setActiveTab('lyrics')}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  activeTab === 'lyrics'
                    ? 'bg-purple-600 text-white'
                    : 'text-purple-300 hover:bg-purple-900/30'
                }`}
              >
                Lyrics
              </button>
              <button
                onClick={() => setActiveTab('midi')}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  activeTab === 'midi'
                    ? 'bg-purple-600 text-white'
                    : 'text-purple-300 hover:bg-purple-900/30'
                }`}
              >
                MIDI Pattern
              </button>
              <button
                onClick={() => setActiveTab('dsp')}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  activeTab === 'dsp'
                    ? 'bg-purple-600 text-white'
                    : 'text-purple-300 hover:bg-purple-900/30'
                }`}
              >
                DSP/Mastering
              </button>
              <button
                onClick={() => setActiveTab('export')}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  activeTab === 'export'
                    ? 'bg-purple-600 text-white'
                    : 'text-purple-300 hover:bg-purple-900/30'
                }`}
              >
                Export
              </button>
            </div>

            {/* Tab Content */}
            {activeTab === 'lyrics' && (
              <div className="space-y-4">
                <h3 className="text-xl font-bold text-white mb-4">Generated Lyrics</h3>
                <div className="bg-slate-900/50 rounded-lg p-6 border border-purple-500/20 font-mono">
                  {result.lyrics?.map((line, i) => (
                    <div key={i} className="mb-3 last:mb-0">
                      <div className="text-purple-100">{line.text || line.line}</div>
                      {(line.lml_trigger || line.lml_tags?.length > 0) && (
                        <div className="text-xs text-purple-400/60 mt-1">
                          {line.lml_trigger || line.lml_tags?.join(' ')}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'midi' && (
              <div className="space-y-4">
                <h3 className="text-xl font-bold text-white mb-4">MIDI Pattern</h3>
                <div className="bg-slate-900/50 rounded-lg p-6 border border-purple-500/20">
                  <div className="mb-4">
                    <div className="text-purple-200 text-sm mb-2">BPM: {result.rhythm_blueprint?.bpm}</div>
                    <div className="text-purple-200 text-sm">Style: {result.rhythm_blueprint?.style}</div>
                  </div>
                  {/* MIDI pattern visualization would go here */}
                  <div className="text-purple-300/60 text-sm">
                    16-step pattern with Late-Pocket timing (+10-18ms snare drag)
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'dsp' && (
              <div className="space-y-4">
                <h3 className="text-xl font-bold text-white mb-4">DSP & Mastering</h3>
                <div className="bg-slate-900/50 rounded-lg p-6 border border-purple-500/20">
                  <pre className="text-purple-200 text-xs overflow-auto">
                    {JSON.stringify(result.mastering_blueprint, null, 2)}
                  </pre>
                </div>
              </div>
            )}

            {activeTab === 'export' && (
              <div className="space-y-4">
                <h3 className="text-xl font-bold text-white mb-4">Export Options</h3>
                <div className="grid grid-cols-2 gap-4">
                  <button
                    onClick={() => {
                      const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement('a');
                      a.href = url;
                      a.download = `track_${Date.now()}.json`;
                      a.click();
                    }}
                    className="p-6 bg-purple-900/20 hover:bg-purple-900/40 border border-purple-500/20 rounded-lg transition-colors flex flex-col items-center gap-2"
                  >
                    <Download className="w-8 h-8 text-purple-400" />
                    <span className="text-white font-semibold">Download JSON</span>
                    <span className="text-purple-200/60 text-sm">Complete blueprint</span>
                  </button>
                  <button
                    className="p-6 bg-slate-900/20 hover:bg-slate-900/40 border border-slate-500/20 rounded-lg transition-colors flex flex-col items-center gap-2 cursor-not-allowed opacity-50"
                    disabled
                  >
                    <FileAudio className="w-8 h-8 text-slate-400" />
                    <span className="text-white font-semibold">Render Audio</span>
                    <span className="text-slate-200/60 text-sm">Coming soon</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="bg-black/40 backdrop-blur-sm rounded-xl border border-purple-500/30 p-12 flex items-center justify-center">
            <div className="text-center">
              <Music2 className="w-16 h-16 text-purple-400/30 mx-auto mb-4" />
              <p className="text-purple-200/60">
                Configure your track and hit Generate
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
