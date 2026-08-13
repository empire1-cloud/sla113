#!/bin/bash
# TexturePacker CLI - Build Phaser 3 atlases from exported sprites

echo "📦 Building texture atlases with TexturePacker..."

# Create output directories
mkdir -p frontend/public/assets/generated/atlases

# Character Atlas
if [ -d "frontend/public/assets/generated/sprites/characters" ] && [ "$(ls -A frontend/public/assets/generated/sprites/characters/*.png 2>/dev/null)" ]; then
  echo "Building character atlas..."
  TexturePacker \
    --phaser3 \
    --sheet frontend/public/assets/generated/atlases/characters-atlas.png \
    --data frontend/public/assets/generated/atlases/characters-atlas.json \
    frontend/public/assets/generated/sprites/characters/ \
    --max-size 2048 \
    --disable-rotation \
    --enable-auto-alias \
    --scale 1 \
    || echo "⚠️  No character sprites found or TexturePacker not installed"
fi

# Boss Atlas
if [ -d "frontend/public/assets/generated/sprites/bosses" ] && [ "$(ls -A frontend/public/assets/generated/sprites/bosses/*.png 2>/dev/null)" ]; then
  echo "Building boss atlas..."
  TexturePacker \
    --phaser3 \
    --sheet frontend/public/assets/generated/atlases/bosses-atlas.png \
    --data frontend/public/assets/generated/atlases/bosses-atlas.json \
    frontend/public/assets/generated/sprites/bosses/ \
    --max-size 2048 \
    --disable-rotation \
    --enable-auto-alias \
    --scale 1 \
    || echo "⚠️  No boss sprites found or TexturePacker not installed"
fi

# Effects Atlas
if [ -d "frontend/public/assets/generated/sprites/effects" ] && [ "$(ls -A frontend/public/assets/generated/sprites/effects/*.png 2>/dev/null)" ]; then
  echo "Building effects atlas..."
  TexturePacker \
    --phaser3 \
    --sheet frontend/public/assets/generated/atlases/effects-atlas.png \
    --data frontend/public/assets/generated/atlases/effects-atlas.json \
    frontend/public/assets/generated/sprites/effects/ \
    --max-size 2048 \
    --disable-rotation \
    --enable-auto-alias \
    --scale 1 \
    || echo "⚠️  No effect sprites found or TexturePacker not installed"
fi

# UI Atlas - Combine all UI elements
if [ -d "frontend/public/assets/generated/ui" ] && [ "$(ls -A frontend/public/assets/generated/ui/*.png 2>/dev/null)" ]; then
  echo "Building UI atlas..."
  TexturePacker \
    --phaser3 \
    --sheet frontend/public/assets/generated/atlases/ui-atlas.png \
    --data frontend/public/assets/generated/atlases/ui-atlas.json \
    frontend/public/assets/generated/ui/ \
    --max-size 2048 \
    --disable-rotation \
    --enable-auto-alias \
    --scale 1 \
    || echo "⚠️  No UI elements found or TexturePacker not installed"
fi

# Arcade UI Atlas - For lobby buttons, etc.
if [ -d "assets/raw/ui" ] && [ "$(ls -A assets/raw/ui/*.png 2>/dev/null)" ]; then
  echo "Building arcade UI atlas..."
  TexturePacker \
    --phaser3 \
    --sheet frontend/public/assets/generated/atlases/arcade-ui.png \
    --data frontend/public/assets/generated/atlases/arcade-ui.json \
    assets/raw/ui/ \
    --max-size 2048 \
    --disable-rotation \
    --enable-auto-alias \
    --scale 1 \
    || echo "⚠️  No raw UI assets found or TexturePacker not installed"
fi

# Game Covers Atlas
if [ -d "frontend/public/assets/generated/thumbnails" ] && [ "$(ls -A frontend/public/assets/generated/thumbnails/*.png 2>/dev/null)" ]; then
  echo "Building game covers atlas..."
  TexturePacker \
    --phaser3 \
    --sheet frontend/public/assets/generated/atlases/game-covers-atlas.png \
    --data frontend/public/assets/generated/atlases/game-covers-atlas.json \
    frontend/public/assets/generated/thumbnails/ \
    --max-size 2048 \
    --disable-rotation \
    --enable-auto-alias \
    --scale 1 \
    || echo "⚠️  No game thumbnails found or TexturePacker not installed"
fi

echo "✅ Texture packing complete!"
echo "📝 Remember to commit the generated .json and .png atlas files"
