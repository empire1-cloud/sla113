#!/bin/bash
# ImageMagick - batch cleanup and resizing
# Usage: ./assets/scripts/optimize-assets.sh

echo "Optimizing assets with ImageMagick..."

# Create output directories
mkdir -p public/assets/generated/thumbnails
mkdir -p public/assets/generated/thumbnails-mobile
mkdir -p public/assets/generated/ui/states

# Process game covers - create thumbnails
for file in assets/source/game-covers/*.png assets/source/game-covers/*.jpg; do
  if [ -f "$file" ]; then
    name=$(basename "$file")
    
    # Desktop thumbnail (640x360)
    magick "$file" \
      -resize "640x360^" \
      -gravity center \
      -extent 640x360 \
      "public/assets/generated/thumbnails/$name"
    
    # Mobile thumbnail (320x180)
    magick "$file" \
      -resize "320x180^" \
      -gravity center \
      -extent 320x180 \
      "public/assets/generated/thumbnails-mobile/$name"
  fi
done

# Create disabled button states
for file in assets/source/ui/*-button.png; do
  if [ -f "$file" ]; then
    name=$(basename "$file" -button.png)
    
    # Disabled version
    magick "$file" \
      -colorspace Gray \
      -alpha set \
      -channel A \
      -evaluate multiply 0.55 \
      "public/assets/generated/ui/${name}-button-disabled.png"
    
    # Pressed version (slightly darker)
    magick "$file" \
      -fill black -colorize 15% \
      "public/assets/generated/ui/${name}-button-pressed.png"
    
    # Hover version (slightly brighter)
    magick "$file" \
      -fill white -colorize 10% \
      "public/assets/generated/ui/${name}-button-hover.png"
  fi
done

# Optimize PNG files with pngquant and optipng
find public/assets/generated -name "*.png" -type f | while read img; do
  echo "Optimizing $img"
  pngquant --quality=65-85 --speed 1 --force --output "$img.opt" "$img" && mv "$img.opt" "$img"
  optipng -o2 -quiet "$img"
done

# Create WebP versions for web
find assets/source -name "*.png" -type f | while read img; do
  name=$(basename "$img" .png)
  dir=$(dirname "$img")
  rel_path=${dir#assets/source/}
  
  mkdir -p "public/assets/generated/$rel_path"
  
  magick "$img" -webp 80 "public/assets/generated/$rel_path/$name.webp"
done

# Generate SVG fallbacks for simple icons (where applicable)
# This would be custom logic based on your icon set

echo "Asset optimization complete!"
