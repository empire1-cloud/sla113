'use client';

import React, { useEffect, useRef, useState } from 'react';
import * as PIXI from 'pixi.js';
import { gsap } from 'gsap';

interface CustomSlotGameProps {
  gameId: string;
  themeColor: string;
  symbols: string[];
}

export default function CustomSlotGame({ gameId, themeColor, symbols }: CustomSlotGameProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const initSlot = async () => {
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

      // --- THE JUICE: LIGHT RAYS ---
      const rays = new PIXI.Graphics();
      rays.fill({ color: themeColor, alpha: 0.1 });
      for (let i = 0; i < 20; i++) {
        rays.moveTo(640, 360);
        rays.lineTo(640 + Math.cos(i) * 2000, 360 + Math.sin(i) * 2000);
      }
      rays.stroke({ width: 2, color: themeColor, alpha: 0.05 });
      stage.addChild(rays);
      gsap.to(rays, { rotation: Math.PI * 2, duration: 20, repeat: -1, ease: 'none' });

      // --- SLOT MACHINE UI ---
      const machine = new PIXI.Container();
      machine.x = 640 - 300;
      machine.y = 360 - 200;
      stage.addChild(machine);

      const reels: any[] = [];
      for (let i = 0; i < 5; i++) {
        const reel = new PIXI.Container();
        reel.x = i * 125;
        machine.addChild(reel);

        const reelBg = new PIXI.Graphics();
        reelBg.fill({ color: 0x000000, alpha: 0.8 });
        reelBg.stroke({ color: themeColor, width: 2 });
        reelBg.rect(0, 0, 120, 400);
        reel.addChild(reelBg);

        const strip: any[] = [];
        for (let j = 0; j < 5; j++) {
          const char = symbols[Math.floor(Math.random() * symbols.length)];
          const symbol = new PIXI.Text({ text: char, style: { fontSize: 64, fill: 0xffffff } });
          symbol.anchor.set(0.5);
          symbol.x = 60;
          symbol.y = j * 80 + 40;
          reel.addChild(symbol);
          strip.push(symbol);
        }
        reels.push({ container: reel, symbols: strip });
      }

      // --- SPIN BUTTON ---
      const spinBtn = new PIXI.Graphics();
      spinBtn.fill(themeColor);
      spinBtn.circle(0, 0, 60);
      spinBtn.x = 640;
      spinBtn.y = 620;
      spinBtn.interactive = true;
      spinBtn.cursor = 'pointer';
      stage.addChild(spinBtn);

      const btnText = new PIXI.Text({ text: "SPIN", style: { fontSize: 24, fontWeight: 'bold', fill: 0x000000 } });
      btnText.anchor.set(0.5);
      spinBtn.addChild(btnText);

      spinBtn.on('pointerdown', () => {
        // JUICE: SCREEN SHAKE
        gsap.to(stage, { x: 5, y: 5, duration: 0.05, repeat: 5, yoyo: true });

        reels.forEach((reel, i) => {
          gsap.to(reel.container, {
            y: reel.container.y + 20,
            duration: 0.1,
            yoyo: true,
            repeat: 1,
            onComplete: () => {
              gsap.to(reel.container, {
                y: 0,
                duration: 0.5,
                delay: i * 0.1,
                ease: "elastic.out(1, 0.5)",
                onComplete: () => {
                   reel.symbols.forEach((s: any) => s.text = symbols[Math.floor(Math.random() * symbols.length)]);
                }
              });
            }
          });
        });
      });
    };

    initSlot();
  }, [gameId, themeColor, symbols]);

  return (
    <div className="w-full h-full relative group">
      <div ref={containerRef} className="w-full h-full rounded-2xl overflow-hidden border border-zinc-800" />
    </div>
  );
}
