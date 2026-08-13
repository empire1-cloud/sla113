#!/bin/bash
# Aseprite CLI - Export sprite sheets and animations

echo "🎨 Exporting sprites with Aseprite CLI..."

# Create necessary directories
mkdir -p assets/source/{characters,bosses,effects,ui,game-cards}
mkdir -p frontend/public/assets/generated/{sprites,atlases,ui,thumbnails}

# Export character sprites
if [ -d "assets/source/characters" ]; then
  for sprite in assets/source/characters/*.aseprite; do
    if [ -f "$sprite" ]; then
      name=$(basename "$sprite" .aseprite)
      echo "Exporting character: $name"
      aseprite -b "$sprite" \
        --sheet frontend/public/assets/generated/sprites/${name}.png \
        --data frontend/public/assets/generated/sprites/${name}.json \
        --format json-array \
        --list-tags \
        --trim \
        --sheet-pack
    fi
  done
fi

# Export boss sprites
if [ -d "assets/source/bosses" ]; then
  for sprite in assets/source/bosses/*.aseprite; do
    if [ -f "$sprite" ]; then
      name=$(basename "$sprite" .aseprite)
      echo "Exporting boss: $name"
      aseprite -b "$sprite" \
        --sheet frontend/public/assets/generated/sprites/bosses/${name}.png \
        --data frontend/public/assets/generated/sprites/bosses/${name}.json \
        --format json-array \
        --list-tags \
        --trim \
        --sheet-pack
    fi
  done
fi

# Export effects (explosions, muzzle flashes, etc.)
if [ -d "assets/source/effects" ]; then
  for sprite in assets/source/effects/*.aseprite; do
    if [ -f "$sprite" ]; then
      name=$(basename "$sprite" .aseprite)
      echo "Exporting effect: $name"
      aseprite -b "$sprite" \
        --sheet frontend/public/assets/generated/sprites/effects/${name}.png \
        --data frontend/public/assets/generated/sprites/effects/${name}.json \
        --format json-array \
        --list-tags \
        --trim \
        --sheet-pack
    fi
  done
fi

# Export UI buttons and elements
if [ -d "assets/source/ui" ]; then
  for sprite in assets/source/ui/*.aseprite; do
    if [ -f "$sprite" ]; then
      name=$(basename "$sprite" .aseprite)
      echo "Exporting UI element: $name"
      aseprite -b "$sprite" \
        --sheet frontend/public/assets/generated/ui/${name}.png \
        --data frontend/public/assets/generated/ui/${name}.json \
        --format json-array \
        --list-tags \
        --trim \
        --sheet-pack
    fi
  done
fi

echo "✅ Sprite export complete!"
