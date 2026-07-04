// Active Frenzy Controller
// This script synchronizes effects for the arcade's "Active Frenzy" state

class ActiveFrenzyController {
  constructor(audioAnalyzer, sceneController) {
    this.audioAnalyzer = audioAnalyzer; // Web Audio API instance
    this.sceneController = sceneController; // Scene assets + animations
    this.frenzyActive = false; // Frenzy State Flag
  }

  // Activate Frenzy State
  activateFrenzy() {
    this.frenzyActive = true;
    this.sceneController.triggerNeonFlicker();
    this.sceneController.activateHydraulics();
    console.log('Active Frenzy Activated!');
  }

  // Deactivate Frenzy State
  deactivateFrenzy() {
    this.frenzyActive = false;
    this.sceneController.resetEffects();
    console.log('Frenzy State Deactivated.');
  }

  // Frame-by-frame Update Loop
  update() {
    if (!this.frenzyActive) return;

    const audioData = this.audioAnalyzer.getFrequencyData();

    // Map Bass (0-200Hz) to Hydraulic Jump
    const bass = audioData.slice(0, 15).reduce((a, b) => a + b, 0) / 15;
    this.sceneController.setHydraulicBounce(bass / 255);

    // Map High Frequencies (2-4kHz) to Neon Flicker
    const highFreq = audioData.slice(40, 55).reduce((a, b) => a + b, 0) / 15;
    this.sceneController.setNeonIntensity(highFreq / 255);
  }
}

export default ActiveFrenzyController;
