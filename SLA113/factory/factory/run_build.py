#!/usr/bin/env python3
"""
SLA113 Industrial Foundry - Build Generator
Interactive CLI for generating sovereign game OS builds
"""

import os
import sys
import json
import time
import hashlib
from datetime import datetime
from pathlib import Path

BUILD_TYPES = {
    "1": {"name": "Arcade Classic", "category": "arcade", "desc": "Retro arcade experience with coin-op mechanics"},
    "2": {"name": "Fish Shooting", "category": "arcade", "desc": "Underwater shooter with catch mechanics"},
    "3": {"name": "Slot Machine", "category": "slots", "desc": "Casino slot with bonus rounds"},
    "4": {"name": "Video Poker", "category": "slots", "desc": "Card-based poker slots"},
    "5": {"name": "Open World RPG", "category": "rpg", "desc": "Massive open world adventure"},
    "6": {"name": "Dungeon Crawler", "category": "rpg", "desc": "Roguelike dungeon exploration"},
    "7": {"name": "Battle Royale", "category": "multiplayer", "desc": "100-player competitive shooter"},
    "8": {"name": "MOBA", "category": "multiplayer", "desc": "Team-based arena combat"},
    "9": {"name": "Racing Sim", "category": "simulation", "desc": "Realistic driving simulation"},
    "10": {"name": "Flight Sim", "category": "simulation", "desc": "Aerospace flight experience"},
    "11": {"name": "City Builder", "category": "strategy", "desc": "Urban planning and management"},
    "12": {"name": "4X Strategy", "category": "strategy", "desc": "Empire building turn-based strategy"},
    "13": {"name": "Fighting Game", "category": "action", "desc": "1v1 combat arena"},
    "14": {"name": "Stealth Action", "category": "action", "desc": "Infiltration and espionage"},
    "15": {"name": "Puzzle Adventure", "category": "puzzle", "desc": "Brain-teasing narrative experience"},
    "16": {"name": "Match-3", "category": "puzzle", "desc": "Cascading gem puzzles"},
    "17": {"name": "Survival Horror", "category": "horror", "desc": " atmospheric fear experience"},
    "18": {"name": "Tower Defense", "category": "casual", "desc": "Strategic base protection"},
    "19": {"name": "Idle Clicker", "category": "casual", "desc": "Incremental progression game"},
    "20": {"name": "Visual Novel", "category": "narrative", "desc": "Story-driven dialogue experience"},
    "21": {"name": "Custom Game", "category": "custom", "desc": "User-defined game specifications"},
}

OBSIDIAN_PALETTE = {
    "primary": "#050505",
    "accent": "#D4AF37",
    "highlight": "#00C8FF"
}

class SLA113Foundry:
    def __init__(self):
        self.base_path = Path("/root/SLA113")
        self.archive_path = self.base_path / "archive" / "builds"
        self.queue_path = self.base_path / "factory" / "queue.json"
        self.archive_path.mkdir(parents=True, exist_ok=True)
        
    def generate_build_id(self, game_type: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        raw = f"{game_type}-{timestamp}"
        return f"SLA113-{hashlib.md5(raw.encode()).hexdigest()[:8].upper()}"
    
    def architect_prompt(self, game_type: str, custom_spec: str | None = None) -> dict:
        game_info = BUILD_TYPES.get(game_type, BUILD_TYPES["21"])
        
        base_prompt = f"""Create a sovereign game OS build for: {game_info['name']}
Category: {game_info['category']}
Description: {game_info['desc']}

Design Requirements:
- Obsidian Blue palette: Primary #050505, Accent #D4AF37, Highlight #00C8FF
- Industrial foundry aesthetic
- Cloud GPU and local CPU rendering support
- Modular game architecture
- Multi-tenant capable"""

        if custom_spec:
            base_prompt += f"\n\nCustom Specifications:\n{custom_spec}"
            
        return {
            "game_type": game_info["name"],
            "category": game_info["category"],
            "prompt": base_prompt,
            "palette": OBSIDIAN_PALETTE,
            "render_modes": ["cloud_gpu", "local_cpu"]
        }
    
    def queue_build(self, game_type: str, mode: str = "fast", custom_spec: str = ""):
        prompt_data = self.architect_prompt(game_type, custom_spec)
        build_id = self.generate_build_id(game_type)
        
        build_request = {
            "build_id": build_id,
            "game_type": prompt_data["game_type"],
            "category": prompt_data["category"],
            "prompt": prompt_data["prompt"],
            "palette": prompt_data["palette"],
            "render_mode": mode,
            "status": "queued",
            "created_at": datetime.now().isoformat()
        }
        
        queue = []
        if self.queue_path.exists():
            with open(self.queue_path) as f:
                queue = json.load(f)
        
        queue.append(build_request)
        
        with open(self.queue_path, 'w') as f:
            json.dump(queue, f, indent=2)
        
        return build_request
    
    def process_build(self, build_request: dict) -> dict:
        build_id = build_request["build_id"]
        mode = build_request["render_mode"]
        
        print(f"[SLA113] Processing build {build_id} in {mode} mode...")
        
        build_request["status"] = "processing"
        build_request["started_at"] = datetime.now().isoformat()
        
        if mode == "fast":
            time.sleep(2)
        else:
            time.sleep(8)
        
        output_dir = self.archive_path / build_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        manifest = {
            "build_id": build_id,
            "game_type": build_request["game_type"],
            "category": build_request["category"],
            "render_mode": mode,
            "palette": OBSIDIAN_PALETTE,
            "created_at": build_request["created_at"],
            "completed_at": datetime.now().isoformat(),
            "files": ["boot.bin", "kernel.os", "assets.pkg", "manifest.json"]
        }
        
        with open(output_dir / "manifest.json", 'w') as f:
            json.dump(manifest, f, indent=2)
        
        for filename in ["boot.bin", "kernel.os", "assets.pkg"]:
            (output_dir / filename).write_text(f"# {filename} - {build_id}")
        
        build_request["status"] = "completed"
        build_request["output_path"] = str(output_dir)
        
        return build_request

def main():
    foundry = SLA113Foundry()
    
    print("\n" + "="*60)
    print("   SLA113 INDUSTRIAL FOUNDRY")
    print("   Sovereign Game OS Factory")
    print("="*60)
    print()
    
    print("Available Game Types:")
    print("-" * 40)
    for num, info in BUILD_TYPES.items():
        print(f"  {num}. {info['name']:<20} [{info['category']}]")
    print()
    
    choice = input("Select game type (1-21): ").strip()
    
    if choice not in BUILD_TYPES:
        print("Invalid selection.")
        sys.exit(1)
    
    print(f"\nSelected: {BUILD_TYPES[choice]['name']}")
    print(f"Description: {BUILD_TYPES[choice]['desc']}")
    print()
    
    print("Render Modes:")
    print("  1. Fast (Cloud GPU)  - Quick generation via Together.ai")
    print("  2. Night-Shift (Local CPU)  - Slow but free EPYC-Milan")
    
    mode_choice = input("Select mode (1-2) [1]: ").strip() or "1"
    mode = "fast" if mode_choice == "1" else "night-shift"
    
    custom_spec = ""
    if choice == "21":
        custom_spec = input("\nEnter custom game specifications: ").strip()
    
    print(f"\n[+] Queuing build for {BUILD_TYPES[choice]['name']} in {mode} mode...")
    
    result = foundry.queue_build(choice, mode, custom_spec)
    print(f"[✓] Build queued: {result['build_id']}")
    print(f"[>] Status: {result['status']}")
    
    process = input("\nProcess now? (y/n) [y]: ").strip() or "y"
    if process.lower() == 'y':
        print(f"\n[*] Processing build {result['build_id']}...")
        completed = foundry.process_build(result)
        print(f"[✓] Build completed: {completed['output_path']}")
        print(f"[>] Files: {', '.join(completed.get('files', []))}")

if __name__ == "__main__":
    main()
