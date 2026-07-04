'use client';

import React, { useEffect, useRef, useState } from 'react';
import * as PIXI from 'pixi.js';
import { gsap } from 'gsap';

export default function GShieldWOF({ onWin }: { onWin?: (amount: number) => void }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [spinning, setSpinning] = useState(false);

  useEffect(() => {
    const initWOF = async () => {
      if (!containerRef.current) return;

      const app = new PIXI.Application();
      await app.init({
        width: 600,
        height: 600,
        backgroundAlpha: 0,
        antialias: true,
      });

      containerRef.current.innerHTML = '';
      containerRef.current.appendChild(app.canvas);

      const stage = new PIXI.Container();
      app.stage.addChild(stage);
      stage.x = 300;
      stage.y = 300;

      // --- THE WHEEL ---
      const wheel = new PIXI.Container();
      stage.addChild(wheel);

      const segments = 12;
      const radius = 250;
      const colors = [0xD4AF37, 0x050505, 0x8B0000, 0x000000];

      for (let i = 0; i < segments; i++) {
        const sector = new PIXI.Graphics();
        const startAngle = (i * 2 * Math.PI) / segments;
        const endAngle = ((i + 1) * 2 * Math.PI) / segments;
        
        sector.fill({ color: colors[i % colors.length] });
        sector.moveTo(0, 0);
        sector.arc(0, 0, radius, startAngle, endAngle);
        sector.stroke({ width: 2, color: 0xFFD700 });
        
        const text = new PIXI.Text({ 
          text: `$${(i + 1) * 100}`, 
          style: { fill: 0xFFFFFF, fontSize: 24, fontWeight: 'bold' } 
        });
        text.anchor.set(0.5);
        const midAngle = (startAngle + endAngle) / 2;
        text.x = Math.cos(midAngle) * (radius * 0.7);
        text.y = Math.sin(midAngle) * (radius * 0.7);
        text.rotation = midAngle + Math.PI / 2;
        
        sector.addChild(text);
        wheel.addChild(sector);
      }

      // --- THE INDICATOR (G-SHIELD) ---
      const indicator = new PIXI.Graphics();
      indicator.fill(0xFFD700);
      indicator.moveTo(280, -20);
      indicator.lineTo(320, 0);
      indicator.lineTo(280, 20);
      indicator.closePath();
      stage.addChild(indicator);

      // --- SPIN FUNCTION ---
      const spin = () => {
        if (spinning) return;
        setSpinning(true);

        const rotations = 5 + Math.random() * 5;
        const finalRotation = rotations * Math.PI * 2;

        gsap.to(wheel, {
          rotation: finalRotation,
          duration: 4,
          ease: "power4.out",
          onComplete: () => {
            setSpinning(false);
            if (onWin) onWin(1000); // Trigger win logic
          }
        });
      };

      containerRef.current.onclick = spin;
    };

    initWOF();
  }, [onWin, spinning]);

  return (
    <div className="flex flex-col items-center justify-center p-8 bg-zinc-950/50 rounded-3xl border border-zinc-800 backdrop-blur-xl">
      <div className="text-[#D4AF37] font-bold text-xl mb-4 tracking-widest uppercase">G-SHIELD // WHEEL OF FORTUNE</div>
      <div ref={containerRef} className="cursor-pointer hover:scale-105 transition-transform duration-500" />
      <div className="mt-8 text-zinc-500 text-xs uppercase tracking-widest animate-pulse">
        {spinning ? "Spinning..." : "Click to Spin for Sovereign Rewards"}
      </div>
    </div>
  );
}
