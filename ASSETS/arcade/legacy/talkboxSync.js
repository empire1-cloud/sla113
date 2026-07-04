// Talkbox Sync Code
// This script analyzes high-frequency Talkbox audio and maps it to visuals

class TalkboxSync {
  constructor(audioAnalyzer, effectManager) {
    this.audioAnalyzer = audioAnalyzer; // Web Audio API AudioAnalyser instance
    this.effectManager = effectManager; // Visual effect manager instance
  }

  update() {
    // Fetch live frequency data
    const frequencyData = this.audioAnalyzer.getFrequencyData();

    // Analyze Talkbox range (high frequencies: 2kHz - 4kHz)
    const talkboxRange = frequencyData.slice(40, 55); // Range indices (example)
    const talkboxAmplitude = talkboxRange.reduce((sum, value) => sum + value, 0) / talkboxRange.length;

    // Map to effects
    this.effectManager.setBloomIntensity(talkboxAmplitude / 255);
    this.effectManager.triggerNeonFlicker(talkboxAmplitude / 255);
    this.effectManager.setGlow(talkboxAmplitude / 255);
  }
}

export default TalkboxSync;
