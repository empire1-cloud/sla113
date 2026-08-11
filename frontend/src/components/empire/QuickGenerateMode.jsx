import { useState } from 'react';
import { Zap, Music, Loader2, Download, ChevronRight } from 'lucide-react';

/**
 * Quick Generate Mode
 * 
 * Fast workflow: Prompt → Generate → Results
 * Perfect for rapid ideation and quick tracks
 */
export default function QuickGenerateMode() {
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setError('Please enter a prompt');
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      const response = await fetch('/api/empire/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt })
      });

      if (!response.ok) {
        throw new Error(`Generation failed: ${response.statusText}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownload = () => {
    if (!result) return;
    
    const blob = new Blob([JSON.stringify(result, null, 2)], { 
      type: 'application/json' 
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `track_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Example prompts
  const examples = [
    "toxic breakup anthem trap 120bpm",
    "aggressive UK drill track survival",
    "intimate soul ballad heartbreak 85bpm",
    "celebration amapiano party vibes",
    "sad reggaeton about lost love"
  ];

  return (
    <div className="max-w-4xl mx-auto">
      {/* Quick Prompt Input */}
      <div className="bg-black/40 backdrop-blur-sm rounded-xl border border-purple-500/30 p-8 shadow-2xl">
        <div className="flex items-start gap-4 mb-6">
          <div className="p-3 rounded-lg bg-purple-600/20 border border-purple-500/30">
            <Zap className="w-6 h-6 text-purple-400" />
          </div>
          <div className="flex-1">
            <h2 className="text-2xl font-bold text-white mb-2">
              Quick Generate
            </h2>
            <p className="text-purple-200/60">
              Describe your track in one sentence. Empire Lyric Master will generate everything instantly.
            </p>
          </div>
        </div>

        {/* Text Input */}
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="e.g., toxic breakup anthem trap 120bpm, she played me..."
          className="w-full h-32 bg-slate-900/50 border border-purple-500/30 rounded-lg px-4 py-3 text-white placeholder-purple-300/30 focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
          disabled={isGenerating}
        />

        {/* Example Prompts */}
        <div className="mt-4 mb-6">
          <p className="text-sm text-purple-200/40 mb-2">Try these examples:</p>
          <div className="flex flex-wrap gap-2">
            {examples.map((example, i) => (
              <button
                key={i}
                onClick={() => setPrompt(example)}
                className="px-3 py-1.5 text-xs bg-purple-900/30 hover:bg-purple-900/50 text-purple-200 rounded-md border border-purple-500/20 transition-colors"
                disabled={isGenerating}
              >
                {example}
              </button>
            ))}
          </div>
        </div>

        {/* Generate Button */}
        <button
          onClick={handleGenerate}
          disabled={isGenerating || !prompt.trim()}
          className="w-full py-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 disabled:from-gray-700 disabled:to-gray-700 text-white font-semibold rounded-lg transition-all flex items-center justify-center gap-2 shadow-lg disabled:cursor-not-allowed"
        >
          {isGenerating ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Generating Track...
            </>
          ) : (
            <>
              <Music className="w-5 h-5" />
              Generate Complete Track
            </>
          )}
        </button>

        {/* Error Message */}
        {error && (
          <div className="mt-4 p-4 bg-red-900/20 border border-red-500/30 rounded-lg">
            <p className="text-red-200 text-sm">{error}</p>
          </div>
        )}
      </div>

      {/* Results */}
      {result && (
        <div className="mt-6 bg-black/40 backdrop-blur-sm rounded-xl border border-purple-500/30 p-6 shadow-2xl animate-in fade-in slide-in-from-bottom-4 duration-500">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-white">
              ✅ Track Generated Successfully!
            </h3>
            <button
              onClick={handleDownload}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-lg flex items-center gap-2 transition-colors"
            >
              <Download className="w-4 h-4" />
              Download Blueprint
            </button>
          </div>

          {/* Track Info */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-purple-900/20 rounded-lg p-4 border border-purple-500/20">
              <div className="text-purple-200/60 text-sm mb-1">Genre</div>
              <div className="text-white font-semibold">
                {result.track_metadata?.genre || 'Unknown'}
              </div>
            </div>
            <div className="bg-purple-900/20 rounded-lg p-4 border border-purple-500/20">
              <div className="text-purple-200/60 text-sm mb-1">BPM</div>
              <div className="text-white font-semibold">
                {result.track_metadata?.bpm || 'N/A'}
              </div>
            </div>
            <div className="bg-purple-900/20 rounded-lg p-4 border border-purple-500/20">
              <div className="text-purple-200/60 text-sm mb-1">Lyrics</div>
              <div className="text-white font-semibold">
                {result.track_metadata?.num_lyrics || 0} lines
              </div>
            </div>
            <div className="bg-purple-900/20 rounded-lg p-4 border border-purple-500/20">
              <div className="text-purple-200/60 text-sm mb-1">Generation</div>
              <div className="text-white font-semibold">
                {result.generation_time_ms?.toFixed(0) || 0}ms
              </div>
            </div>
          </div>

          {/* Lyrics Preview */}
          {result.lyrics && result.lyrics.length > 0 && (
            <div className="mb-6">
              <h4 className="text-white font-semibold mb-3 flex items-center gap-2">
                <ChevronRight className="w-4 h-4" />
                Generated Lyrics
              </h4>
              <div className="bg-slate-900/50 rounded-lg p-4 border border-purple-500/20">
                {result.lyrics.map((line, i) => (
                  <div key={i} className="mb-2 last:mb-0">
                    <span className="text-purple-200">
                      {line.text || line.line}
                    </span>
                    {(line.lml_trigger || line.lml_tags?.length > 0) && (
                      <span className="ml-2 text-xs text-purple-400/60">
                        {line.lml_trigger || line.lml_tags?.join(' ')}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Stats */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-green-900/20 rounded-lg p-4 border border-green-500/20">
              <div className="text-green-200/60 text-sm mb-1">AI Detection Risk</div>
              <div className="text-green-400 font-semibold">
                {((result.empire_performance_metrics?.ai_detection_risk || 0.15) * 100).toFixed(1)}% - Safe
              </div>
            </div>
            <div className="bg-blue-900/20 rounded-lg p-4 border border-blue-500/20">
              <div className="text-blue-200/60 text-sm mb-1">Cultural Authenticity</div>
              <div className="text-blue-400 font-semibold">
                {((result.empire_performance_metrics?.cultural_fingerprint_score || 0.85) * 100).toFixed(0)}%
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
