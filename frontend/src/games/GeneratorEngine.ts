export type RenderMode = 'cloud' | 'local';
export type BuildStatus = 'queued' | 'processing' | 'completed' | 'failed';

export interface BuildRequest {
  build_id: string;
  game_type: string;
  category: string;
  prompt: string;
  palette: {
    primary: string;
    accent: string;
    highlight: string;
  };
  render_mode: RenderMode;
  status: BuildStatus;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  output_path?: string;
  error?: string;
}

export interface FactoryStatus {
  queue_length: number;
  processing: boolean;
  current_build: BuildRequest | null;
  last_heartbeat: string;
  render_modes: {
    cloud: boolean;
    local: boolean;
  };
}

export class GeneratorEngine {
  private apiEndpoint: string;
  private mode: RenderMode;
  private queue: BuildRequest[] = [];
  private processing: boolean = false;

  constructor(endpoint: string = '/api/sla113', mode: RenderMode = 'cloud') {
    this.apiEndpoint = endpoint;
    this.mode = mode;
  }

  setMode(mode: RenderMode): void {
    this.mode = mode;
  }

  getMode(): RenderMode {
    return this.mode;
  }

  async queueBuild(gameType: string, customPrompt?: string): Promise<BuildRequest> {
    const response = await fetch(`${this.apiEndpoint}/queue-prompt`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        game_type: gameType,
        mode: this.mode,
        custom_prompt: customPrompt
      })
    });

    if (!response.ok) {
      throw new Error(`Queue failed: ${response.statusText}`);
    }

    const result = await response.json();
    return result.build;
  }

  async getStatus(): Promise<FactoryStatus> {
    const response = await fetch(`${this.apiEndpoint}/status`);
    
    if (!response.ok) {
      throw new Error(`Status fetch failed: ${response.statusText}`);
    }

    return response.json();
  }

  async getQueue(): Promise<BuildRequest[]> {
    const response = await fetch(`${this.apiEndpoint}/queue`);
    
    if (!response.ok) {
      throw new Error(`Queue fetch failed: ${response.statusText}`);
    }

    return response.json();
  }

  async cancelBuild(buildId: string): Promise<boolean> {
    const response = await fetch(`${this.apiEndpoint}/cancel`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ build_id: buildId })
    });

    return response.ok;
  }

  processQueue(): void {
    if (this.processing) return;
    
    this.processing = true;
    this.processNext();
  }

  private async processNext(): Promise<void> {
    if (this.queue.length === 0) {
      this.processing = false;
      return;
    }

    const build = this.queue.shift();
    if (!build) return;

    try {
      await this.executeBuild(build);
    } catch (error) {
      console.error(`Build ${build.build_id} failed:`, error);
    }

    setTimeout(() => this.processNext(), 1000);
  }

  private async executeBuild(build: BuildRequest): Promise<void> {
    if (this.mode === 'cloud') {
      await this.cloudRender(build);
    } else {
      await this.localRender(build);
    }
  }

  private async cloudRender(build: BuildRequest): Promise<void> {
    console.log(`[Cloud] Rendering ${build.build_id} via Together.ai...`);
    await new Promise(resolve => setTimeout(resolve, 2000));
  }

  private async localRender(build: BuildRequest): Promise<void> {
    console.log(`[Local] Rendering ${build.build_id} on EPYC-Milan CPU...`);
    await new Promise(resolve => setTimeout(resolve, 8000));
  }
}

export const OBSIDIAN_PALETTE = {
  primary: '#050505',
  accent: '#D4AF37',
  highlight: '#00C8FF'
};

export const GAME_CATEGORIES = [
  { id: 'arcade', label: 'Arcade', color: '#FF6B6B' },
  { id: 'slots', label: 'Slots', color: '#D4AF37' },
  { id: 'rpg', label: 'RPG', color: '#9B59B6' },
  { id: 'multiplayer', label: 'Multiplayer', color: '#E74C3C' },
  { id: 'simulation', label: 'Simulation', color: '#3498DB' },
  { id: 'strategy', label: 'Strategy', color: '#2ECC71' },
  { id: 'action', label: 'Action', color: '#F39C12' },
  { id: 'puzzle', label: 'Puzzle', color: '#1ABC9C' },
  { id: 'horror', label: 'Horror', color: '#34495E' },
  { id: 'casual', label: 'Casual', color: '#E91E63' },
  { id: 'narrative', label: 'Narrative', color: '#00BCD4' },
  { id: 'custom', label: 'Custom', color: '#9C27B0' }
];
