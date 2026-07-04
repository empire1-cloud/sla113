'use client';

import React, { useEffect, useRef } from 'react';
import * as PIXI from 'pixi.js';
import { gsap } from 'gsap';

interface AztecFishGameProps {
  gameId: string;
  themeColor: string;
  godName: string;
}

export default function AztecFishGame({ gameId, themeColor, godName }: AztecFishGameProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const initGame = async () => {
      if (!containerRef.current) return;

      const app = new PIXI.Application();
      await app.init({
        width: 1280,
        height: 720,
        backgroundColor: 0x050505,
        antialias: true,
      });

      containerRef.current.innerHTML = '';
      containerRef.current.appendChild(app.canvas);

      const stage = new PIXI.Container();
      app.stage.addChild(stage);

      // --- THE JUICE: LIGHT MIST ---
      const mist = new PIXI.Graphics();
      mist.fill({ color: themeColor, alpha: 0.05 });
      mist.rect(0, 0, 1280, 720);
      stage.addChild(mist);

      // --- GOD EMBLEM (PREMIUM) ---
      const godText = new PIXI.Text(
        godName.toUpperCase(),
        { fill: themeColor, fontSize: 120, fontWeight: 'bold', fontStyle: 'italic' }
      );
      godText.anchor.set(0.5);
      godText.x = 640;
      godText.y = 360;
      godText.alpha = 0.1;
      stage.addChild(godText);

      // --- FISH SPAWNER (JUICE VERSION) ---
      const spawnFish = () => {
        const fish = new PIXI.Graphics();
        fish.fill({ color: themeColor });
        fish.circle(0, 0, 15);
        fish.x = -50;
        fish.y = Math.random() * 720;
        fish.interactive = true;
        fish.cursor = 'crosshair';
        stage.addChild(fish);

        // Click to Kill (Juice)
        fish.on('pointerdown', () => {
             // EXPLOSION PARTICLES
             for (let i = 0; i < 10; i++) {
                 const p = new PIXI.Graphics();
                 p.fill({ color: 0xFFD700 });
                 p.circle(0, 0, 3);
                 p.x = fish.x;
                 p.y = fish.y;
                 stage.addChild(p);
                 gsap.to(p, { 
                     x: p.x + (Math.random() - 0.5) * 200, 
                     y: p.y + (Math.random() - 0.5) * 200, 
                     alpha: 0, 
                     duration: 0.5, 
                     onComplete: () => p.destroy() 
                 });
             }
             gsap.to(stage, { x: 5, y: 5, duration: 0.05, repeat: 3, yoyo: true });
             fish.destroy();
        });

        gsap.to(fish, {
          x: 1330,
          duration: 4 + Math.random() * 4,
          onComplete: () => fish.destroy()
        });
      };

      const interval = setInterval(spawnFish, 800);
      return () => clearInterval(interval);
    };

    initGame();
  }, [gameId, themeColor, godName]);

  return (
    <div className="w-full h-full relative group">
      <div ref={containerRef} className="w-full h-full rounded-2xl overflow-hidden border border-zinc-800" />
      <div className="absolute top-4 left-4 flex items-center space-x-2 bg-black/80 p-2 rounded-lg border border-zinc-700">
        <div className="w-2 h-2 rounded-full animate-pulse" style={{ backgroundColor: themeColor }} />
        <span className="text-[10px] text-zinc-400 font-bold tracking-widest">
          {gameId.toUpperCase()} {'//'} PREDATOR_MODE
        </span>
      </div>
    </div>
  );
}
