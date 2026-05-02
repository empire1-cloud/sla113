#!/usr/bin/env python3
"""
Engine Migration Script
Migrates all engines from emergentintegrations to local integrations.

Usage:
    python migrate_engines.py

This script will:
1. Backup original engine files
2. Update imports from emergentintegrations to integrations.llm
3. Update API key retrieval to use LLMConfig
4. Update LLM calls to use ChatLLM
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime

# Engines to migrate
ENGINE_FILES = [
    "strategy_engine.py",
    "plan_builder.py",
    "analysis_engine.py",
    "opportunity_mapper.py",
    "evaluator_engine.py",
    "pricing_engine.py",
    "blueprint_engine.py",
    "persona_engine.py",
    "money_pipeline_engine.py",
    "pipeline_composer.py",
    "anime_character_engine.py",
    "anime_lore_engine.py",
    "anime_story_engine.py",
    "art_direction_engine.py",
    "hybrid_core.py",
    "router.py",
]

SERVICES_DIR = Path(__file__).parent / "services"
BACKUP_DIR = Path(__file__).parent / "services_backup"


def backup_file(filepath: Path):
    """Create backup of original file."""
    backup_path = BACKUP_DIR / filepath.name
    shutil.copy(filepath, backup_path)
    print(f"  Backed up: {filepath.name}")


def migrate_imports(content: str) -> str:
    """Update import statements."""
    
    # Replace emergentintegrations imports
    patterns = [
        (
            r"from emergentintegrations\.llm\.chat import.*?\n",
            "from integrations.llm import ChatLLM, LLMConfig, ModelProvider\n"
        ),
        (
            r"from emergentintegrations\.llm import.*?\n",
            "from integrations.llm import ChatLLM, LLMConfig, ModelProvider\n"
        ),
        (
            r"import emergentintegrations.*?\n",
            "from integrations.llm import ChatLLM, LLMConfig, ModelProvider\n"
        ),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    return content


def migrate_api_key(content: str) -> str:
    """Update API key retrieval."""
    
    # Replace EMERGENT_LLM_KEY direct access
    content = re.sub(
        r'os\.environ\.get\(["\']EMERGENT_LLM_KEY["\']\)',
        'LLMConfig.get_api_key(ModelProvider.OPENAI)',
        content
    )
    
    return content


def add_docstring(content: str, filename: str) -> str:
    """Add migration note to docstring."""
    
    engine_name = filename.replace("_", " ").replace(".py", "").title()
    note = f'''"""
{engine_name}
Migrated to use local integrations (standalone deployment).

Supports: OpenAI (GPT-4o), Anthropic (Claude), Google (Gemini)
"""

'''
    
    # If file starts with docstring, append to it
    if content.startswith('"""'):
        end = content.find('"""', 3)
        if end > 0:
            existing = content[3:end].strip()
            content = f'"""\n{existing}\n\nMigrated to local integrations.\n"""\n' + content[end+3:]
    else:
        content = note + content
    
    return content


def migrate_file(filepath: Path):
    """Migrate a single engine file."""
    
    print(f"\nMigrating: {filepath.name}")
    
    # Read content
    with open(filepath, "r") as f:
        content = f.read()
    
    # Check if already migrated
    if "from integrations.llm import" in content:
        print(f"  Already migrated, skipping")
        return
    
    # Check if uses emergentintegrations
    if "emergentintegrations" not in content:
        print(f"  No emergentintegrations imports, skipping")
        return
    
    # Backup
    backup_file(filepath)
    
    # Apply migrations
    content = migrate_imports(content)
    content = migrate_api_key(content)
    
    # Write updated content
    with open(filepath, "w") as f:
        f.write(content)
    
    print(f"  Migrated successfully")


def main():
    print("=" * 60)
    print("Engine Migration Script")
    print("Migrating from emergentintegrations to local integrations")
    print("=" * 60)
    
    # Create backup directory
    BACKUP_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"\nBackups will be saved to: {BACKUP_DIR}")
    
    # Migrate each engine
    migrated = 0
    for filename in ENGINE_FILES:
        filepath = SERVICES_DIR / filename
        if filepath.exists():
            migrate_file(filepath)
            migrated += 1
        else:
            print(f"\nSkipped (not found): {filename}")
    
    print("\n" + "=" * 60)
    print(f"Migration complete! {migrated} files processed")
    print(f"Backups saved to: {BACKUP_DIR}")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Test the migrated engines")
    print("2. Set environment variables:")
    print("   - OPENAI_API_KEY (for GPT models)")
    print("   - ANTHROPIC_API_KEY (for Claude models)")
    print("   - GOOGLE_API_KEY (for Gemini models)")
    print("   - Or EMERGENT_LLM_KEY (universal fallback)")


if __name__ == "__main__":
    main()
