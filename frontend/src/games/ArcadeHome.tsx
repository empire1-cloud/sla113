'use client';

import React, { useState, useEffect, useRef } from 'react';
import { AZTEC_GAMES } from '@/lib/aztec_registry';
import { SLOT_GAMES } from '@/lib/slot_registry';
import GShieldWOF from '@/components/games/GShieldWOF';
import CustomSlotGame from '@/components/games/CustomSlotGame';
import AztecFishGame from '@/components/games/AztecFishGame';

/**
 * SOVEREIGN_ARCADE // GOD_TIER_LOBBY // v2.1_ROBUST
 * Built to surpass Juwa and FireKirin
 * Target: arcade.southernlifestyle.org
 */
export default function ArcadeHome() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [activeGame, setActiveGame] = useState<string | null>(null);
  const [gameType, setGameType] = useState<'FISH' | 'SLOT' | 'WOF' | null>(null);
  const [jackpot, setJackpot] = useState(128450.75);
  const [loadingProgress, setLoadingProgress] = useState(0);
  const [gameState, setGameState] = useState<'LOADING' | 'LOBBY' | 'GAME'>('LOADING');

  // --- SOVEREIGN SLAM BRAIN (LOGIC) ---
  const SYMBOLS = [
    { id: 'crown', char: '👑', weight: 4, pays: {3: 100, 4: 500, 5: 5000}, isJackpot: true },
    { id: 'wild', char: '⭐', weight: 6, pays: {3: 50, 4: 200, 5: 1000}, isWild: true },
    { id: 'scatter', char: '🎉', weight: 8, isScatter: true },
    { id: 'seven', char: '7️⃣', weight: 10, pays: {3: 30, 4: 100, 5: 500} },
    { id: 'bar', char: '🍀', weight: 15, pays: {3: 20, 4: 50, 5: 200} },
    { id: 'bell', char: '🔔', weight: 18, pays: {3: 15, 4: 40, 5: 150} },
    { id: 'cherry', char: '🍒', weight: 25, pays: {3: 10, 4: 25, 5: 75} },
    { id: 'grape', char: '🍇', weight: 30, pays: {3: 5, 4: 15, 5: 50} },
  ];

  const getWeightedSymbol = () => {
    const totalWeight = SYMBOLS.reduce((sum, s) => sum + s.weight, 0);
    let rand = Math.random() * totalWeight;
    for (const sym of SYMBOLS) {
      rand -= sym.weight;
      if (rand <= 0) return sym;
    }
    return SYMBOLS[0];
  };

  // Simulate Live Jackpot
  useEffect(() => {
    const interval = setInterval(() => {
      setJackpot(prev => prev + Math.random() * 0.1);
    }, 100);
    return () => clearInterval(interval);
  }, []);

  // --- PIXI LOBBY ENGINE (ONLY RUNS WHEN NO GAME ACTIVE) ---
  useEffect(() => {
    if (activeGame) return;

    const loadScripts = async () => {
      if (window.PIXI && window.gsap) { initEngine(); return; }
      
      const pixiScript = document.createElement('script');
      pixiScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/pixi.js/7.4.2/pixi.min.js';
      document.head.appendChild(pixiScript);

      const gsapScript = document.createElement('script');
      gsapScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js';
      document.head.appendChild(gsapScript);

      await Promise.all([
        new Promise((res) => pixiScript.onload = res),
        new Promise((res) => gsapScript.onload = res)
      ]);

      initEngine();
    };

    const initEngine = () => {
      if (!containerRef.current || !window.PIXI || !window.gsap) return;
      const PIXI = window.PIXI;
      const gsap = window.gsap;

      containerRef.current.innerHTML = '';

      const app = new PIXI.Application({
        width: window.innerWidth,
        height: window.innerHeight,
        backgroundColor: 0x050505,
        antialias: true,
        resolution: window.devicePixelRatio || 1,
      });
      containerRef.current.appendChild(app.view);

      const stage = new PIXI.Container();
      app.stage.addChild(stage);

      const loader = PIXI.Assets;
      loader.add('logo', '/brand/southern-logo.png');
      loader.add('titleBg', '/assets/titleScreen.jpg');
      
      const symbolTextures: Record<string, any> = {};
      
      const startLoading = async () => {
        try {
          const assets = await loader.load(['logo', 'titleBg'], (p: number) => {
            setLoadingProgress(Math.floor(p * 100));
          }).catch(() => ({ logo: null, titleBg: null }));
          
          SYMBOLS.forEach(sym => {
            const text = new PIXI.Text(sym.char, { fontSize: 60, fill: 0xffffff });
            symbolTextures[sym.id] = text; 
          });

          runLoaderSequence(assets || { logo: null, titleBg: null });
        } catch (e) {
          initGame({ logo: null, titleBg: null });
        }
      };

      const runLoaderSequence = (assets: any) => {
        let emblem;
        if (assets.logo) {
            emblem = new PIXI.Sprite(assets.logo);
            emblem.scale.set(0.2);
        } else {
            emblem = new PIXI.Text("S", { fontSize: 120, fill: 0xD4AF37, fontWeight: '900' });
        }
        emblem.anchor.set(0.5);
        emblem.x = app.screen.width / 2;
        emblem.y = app.screen.height / 2;
        emblem.alpha = 0;
        stage.addChild(emblem);

        const bloom = new PIXI.BlurFilter(8);
        emblem.filters = [bloom];

        gsap.to(emblem, { alpha: 1, duration: 1.5, ease: "power2.out" });
        gsap.to(emblem.scale, { x: assets.logo ? 0.22 : 1.1, y: assets.logo ? 0.22 : 1.1, duration: 3, yoyo: true, repeat: -1, ease: "sine.inOut" });

        setTimeout(() => {
          gsap.to(emblem, { 
            alpha: 0, 
            scale: assets.logo ? 0.5 : 2, 
            duration: 0.8, 
            ease: "back.in(1.7)",
            onComplete: () => initGame(assets)
          });
        }, 2000);
      };

      const initGame = (assets: any) => {
        setGameState('LOBBY');
        stage.removeChildren();

        if (assets.titleBg) {
          const bg = new PIXI.Sprite(assets.titleBg);
          bg.anchor.set(0.5);
          bg.x = app.screen.width / 2;
          bg.y = app.screen.height / 2;
          bg.scale.set(Math.max(app.screen.width / bg.width, app.screen.height / bg.height));
          bg.alpha = 0.4;
          stage.addChild(bg);
        } else {
          const rect = new PIXI.Graphics();
          rect.beginFill(0x1a0b2e);
          rect.drawRect(0, 0, app.screen.width, app.screen.height);
          rect.endFill();
          stage.addChild(rect);
        }
      };

      startLoading();
      window.addEventListener('resize', () => app.renderer.resize(window.innerWidth, window.innerHeight));
    };

    loadScripts();
  }, [activeGame]);

  const selectedFish = AZTEC_GAMES.find(g => g.id === activeGame);
  const selectedSlot = SLOT_GAMES.find(g => g.id === activeGame);

  return (
    <div className="bg-[#050505] w-full min-h-screen overflow-x-hidden flex flex-col font-mono text-white selection:bg-[#D4AF37] selection:text-black">
      
      {/* BACKGROUND PIXI LAYER (Visible in Lobby) */}
      {!activeGame && <div ref={containerRef} className="fixed inset-0 z-0 opacity-40 pointer-events-none" />}

      {/* 1. SOVEREIGN HUD */}
      <div className="sticky top-0 z-50 bg-[#050505]/80 backdrop-blur-xl border-b border-zinc-900 p-6 flex justify-between items-center">
        <div className="flex items-center space-x-6">
            <div className="w-10 h-10 bg-[#D4AF37] rounded-lg flex items-center justify-center font-black text-black">S</div>
            <div className="hidden md:block">
                <div className="text-[12px] font-bold tracking-[0.2em] uppercase text-white">SLA113 // SOVEREIGN_SYSTEM</div>
                <div className="text-[10px] text-zinc-500 uppercase tracking-widest">Personal Arcade Interface</div>
            </div>
        </div>

        <div className="flex flex-col items-center">
            <div className="text-[8px] text-[#D4AF37] uppercase tracking-[0.4em] mb-1">GLOBAL SOVEREIGN JACKPOT</div>
            <div className="text-3xl font-black italic tracking-tighter text-white tabular-nums">
                ${jackpot.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
        </div>

        <div className="flex items-center space-x-6">
            <div className="text-right">
                <div className="text-[8px] text-zinc-500 uppercase">Balance</div>
                <div className="text-sm font-bold text-[#D4AF37]">$2,450.00</div>
            </div>
            {activeGame && (
                <button 
                  onClick={() => { setActiveGame(null); setGameType(null); }}
                  className="bg-white/5 border border-white/10 px-6 py-2 text-[10px] text-zinc-400 hover:bg-white hover:text-black transition-all uppercase tracking-widest font-bold rounded-full"
                >
                    EXIT TO LOBBY
                </button>
            )}
        </div>
      </div>

      <div className="p-8 pb-32 z-10">
        {!activeGame ? (
            <div className="space-y-24">
                
                <section className="relative group cursor-pointer" onClick={() => { setActiveGame('gshield_wof'); setGameType('WOF'); }}>
                    <div className="absolute -inset-1 bg-gradient-to-r from-[#D4AF37] to-red-600 rounded-3xl blur opacity-10 group-hover:opacity-30 transition duration-1000 group-hover:duration-200"></div>
                    <div className="relative bg-zinc-900 border border-zinc-800 rounded-3xl p-12 flex items-center overflow-hidden">
                        <div className="flex-1 z-10">
                             <div className="flex items-center space-x-3 mb-6">
                                <div className="px-3 py-1 bg-[#D4AF37]/10 border border-[#D4AF37]/30 text-[10px] text-[#D4AF37] font-bold rounded-full">HIGH VOLATILITY</div>
                                <div className="text-zinc-500 text-[10px] uppercase tracking-widest">Featured Engine</div>
                             </div>
                             <h2 className="text-7xl font-black italic tracking-tighter mb-4">G-SHIELD<br/>WHEEL</h2>
                             <p className="text-zinc-400 max-w-sm text-sm leading-relaxed mb-8">Exclusive high-limit rewards. The ultimate Sovereign test of loyalty and luck.</p>
                             <div className="flex items-center space-x-6">
                                <button className="bg-[#D4AF37] text-black px-10 py-4 text-xs font-black tracking-widest uppercase hover:scale-105 transition-transform">SPIN NOW</button>
                                <div className="text-[10px] text-zinc-600 uppercase tracking-widest">Max Win: 50,000X</div>
                             </div>
                        </div>
                        <div className="absolute right-0 top-0 bottom-0 w-2/5 bg-gradient-to-l from-zinc-950 to-transparent flex items-center justify-center">
                             <div className="w-80 h-80 rounded-full border-[20px] border-zinc-900 shadow-[0_0_100px_rgba(212,175,55,0.1)] flex items-center justify-center">
                                <div className="text-8xl font-black text-zinc-800">WOF</div>
                             </div>
                        </div>
                    </div>
                </section>

                <section>
                    <div className="flex items-center justify-between mb-8">
                        <div className="flex items-center space-x-4">
                            <h2 className="text-2xl font-black tracking-tighter italic">AZTEC MYTH CYCLE</h2>
                            <div className="h-px w-32 bg-zinc-800" />
                            <span className="text-zinc-600 text-[10px] uppercase font-bold">14 Boss Hunt Engines</span>
                        </div>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
                        {AZTEC_GAMES.map((game) => (
                            <div 
                              key={game.id}
                              onClick={() => { setActiveGame(game.id); setGameType('FISH'); }}
                              className="aspect-[3/4] bg-zinc-900 border border-zinc-800 p-6 flex flex-col justify-between hover:border-[#D4AF37] transition-all group cursor-pointer relative overflow-hidden"
                            >
                                <div className="z-10">
                                    <div className="text-[8px] text-zinc-500 uppercase tracking-widest mb-1">{game.element}</div>
                                    <h3 className="font-bold text-sm tracking-tight group-hover:text-[#D4AF37] transition-colors">{game.name.toUpperCase()}</h3>
                                </div>
                                <div className="z-10 space-y-3">
                                    <div className="text-[9px] text-zinc-600 italic leading-tight">Boss: {game.god}</div>
                                    <div className="w-full bg-zinc-950 h-1 rounded-full overflow-hidden">
                                        <div className="h-full bg-[#D4AF37] transition-all duration-500 w-0 group-hover:w-full" />
                                    </div>
                                    <div className="flex justify-between items-center text-[8px] text-zinc-400">
                                        <span>{game.config.bossHp} HP</span>
                                        <span className="font-bold">{game.config.multiplier}X</span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </section>

                <section>
                    <div className="flex items-center justify-between mb-8">
                        <div className="flex items-center space-x-4">
                            <h2 className="text-2xl font-black tracking-tighter italic">SOVEREIGN SLOTS</h2>
                            <div className="h-px w-32 bg-zinc-800" />
                            <span className="text-zinc-600 text-[10px] uppercase font-bold">10 High-Limit Engines</span>
                        </div>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
                        {SLOT_GAMES.map((slot) => (
                            <div 
                              key={slot.id}
                              onClick={() => { setActiveGame(slot.id); setGameType('SLOT'); }}
                              className="bg-zinc-950 border border-zinc-900 rounded-2xl p-8 space-y-6 hover:bg-zinc-900/40 hover:border-zinc-700 transition-all cursor-pointer group"
                            >
                                <div className="w-12 h-12 bg-white/5 rounded-xl flex items-center justify-center text-xl group-hover:scale-110 transition-transform">
                                    {slot.symbols[0]}
                                </div>
                                <div className="space-y-1">
                                    <h3 className="font-bold text-lg group-hover:text-[#D4AF37] transition-colors">{slot.name}</h3>
                                    <div className="text-[10px] text-zinc-600 uppercase tracking-widest">{slot.theme}</div>
                                </div>
                                <div className="flex justify-between items-center pt-4 border-t border-zinc-900">
                                    <div className="text-[10px] text-zinc-500">RTP: {(slot.rtp * 100).toFixed(1)}%</div>
                                    <div className="px-2 py-1 bg-green-500/10 text-green-500 text-[8px] font-bold rounded">LIVE</div>
                                </div>
                            </div>
                        ))}
                    </div>
                </section>

            </div>
        ) : (
            <div className="flex-1 flex flex-col h-[calc(100vh-200px)]">
                {gameType === 'FISH' && selectedFish && (
                    <AztecFishGame
                      gameId={selectedFish.id}
                      themeColor={selectedFish.color}
                      godName={selectedFish.god}
                    />
                )}
                {gameType === 'SLOT' && selectedSlot && (
                    <CustomSlotGame 
                      gameId={activeGame} 
                      symbols={selectedSlot.symbols} 
                      themeColor={selectedSlot.color} 
                    />
                )}
                {gameType === 'WOF' && (
                    <div className="flex-1 flex items-center justify-center">
                        <GShieldWOF />
                    </div>
                )}
            </div>
        )}
      </div>

      <div className="fixed bottom-0 left-0 w-full bg-[#050505] border-t border-zinc-900 p-4 flex justify-between items-center text-[8px] text-zinc-600 uppercase tracking-[0.2em] px-12 z-50">
          <div className="flex space-x-12">
              <div>System Uptime: 99.98%</div>
              <div>Connected Players: 12,450</div>
              <div>Engine: <span className="text-[#D4AF37]">SLA113_V2_PIXI</span></div>
          </div>
          <div className="text-[#D4AF37] font-bold">ARCADE.SOUTHERNLIFESTYLE.ORG // THE GOLD STANDARD</div>
      </div>

      <style jsx global>{`
        body { margin: 0; padding: 0; background: #050505; color: #fff; overflow-x: hidden; }
        canvas { display: block; }
      `}</style>
    </div>
  );
}

declare global {
  interface Window {
    PIXI: any;
    gsap: any;
  }
}
