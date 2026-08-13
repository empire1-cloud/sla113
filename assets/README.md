# SLA113 Asset Production Pipeline

This directory contains the complete asset production pipeline for the SLA113 Southern Arcade, following the recommended CLI stack:

## 🛠️ Toolchain

1. **Aseprite CLI** - Animation and sprite export
2. **TexturePacker CLI** - Phaser atlas creation
3. **ImageMagick** - Batch processing and optimization
4. **Sharp** (Node.js) - Programmatic image processing
5. **Phaser Asset Packs** - Clean asset loading

## 📁 Directory Structure

```
assets/
├── source/                 # Original artist assets (.aseprite, .psd, .ai, etc.)
│   ├── characters/         # Character sprites and animations
│   ├── bosses/             # Boss characters
│   ├── effects/            # Particle effects, explosions, muzzle flashes
│   ├── ui/                 # UI elements (buttons, icons, panels)
│   └── game-covers/        # Game thumbnail artwork
├── raw/                    # Processed PNG/JPG assets ready for packing
│   └── ui/                 # UI elements for atlas packing
├── scripts/                # Automation scripts
│   ├── export-sprites.sh   # Aseprite CLI exports
│   ├── build-atlases.sh    # TexturePacker CLI atlases
│   ├── optimize-assets.sh  # ImageMagick optimization
│   └── validate-assets.mjs # Asset validation with Sharp
└── generated/              # Output assets (copied to frontend/public/assets/generated)
```

## 🚀 Usage

### Available NPM Scripts (in package.json):

```bash
# Export sprites from Aseprite source files
npm run assets:export

# Build texture atlases from exported sprites
npm run assets:pack

# Optimize assets (resize, compress, create variants)
npm run assets:optimize

# Validate all assets meet quality standards
npm run assets:validate

# Full pipeline: export → pack → optimize → validate
npm run assets:build
```

### Individual Scripts:

```bash
# Aseprite sprite export
./assets/scripts/export-sprites.sh

# TexturePacker atlas building
./assets/scripts/build-atlases.sh

# ImageMagick optimization
./assets/scripts/optimize-assets.sh

# Node.js validation with Sharp
node assets/scripts/validate-assets.mjs
```

## 🎮 Integration with Phaser Games

The pipeline generates a Phaser Asset Pack file at:
`frontend/public/assets/arcade-pack.json`

In your Phaser game, load it with:
```javascript
this.load.pack('game-assets', 'assets/arcade-pack.json');
```

This gives you access to all pre-defined assets:
- `this.add.sprite(x, y, 'characters', 'hero-idle-0')`
- `this.add.image(x, y, 'lobby-background')`
- `this.add.sprite(x, y, 'arcade-ui', 'play-button')`
- `this.sound.play('coin-sound')`

## 📦 Generated Assets

After running `npm run assets:build`, you'll find:

```
frontend/public/assets/generated/
├── atlases/
│   ├── characters-atlas.png
│   ├── characters-atlas.json
│   ├── bosses-atlas.png
│   ├── bosses-atlas.json
│   ├── effects-atlas.png
│   ├── effects-atlas.json
│   ├── ui-atlas.png
│   ├── ui-atlas.json
│   ├── arcade-ui.png
│   ├── arcade-ui.json
│   └── game-covers-atlas.png
├── sprites/
│   ├── characters/
│   ├── bosses/
│   └── effects/
├── ui/
│   ├── button-states/
│   └── icons/
└── thumbnails/
    ├── desktop/
    └── mobile/
```

## 🔧 Prerequisites

Install the required tools:

```bash
# Aseprite (from https://www.aseprite.org/)
# TexturePacker (from https://www.codeandweb.com/texturepacker)
# ImageMagick
sudo apt-get install imagemagick

# PNG optimization tools
sudo apt-get install pngquant optipng

# Node.js dependencies (already in package.json)
npm install
```

## 💡 Workflow for Artists

1. Create/edit animations in Aseprite (`assets/source/*/*.aseprite`)
2. Run `npm run assets:export` to generate sprite sheets
3. Place any additional PNG/JPG assets in `assets/raw/`
4. Run `npm run assets:pack` to create texture atlases
5. Run `npm run assets:optimize` to create web-optimized versions
6. Run `npm run assets:validate` to verify quality
7. Commit generated assets to repo
8. Games automatically use the latest assets via the asset pack

## 🎯 Benefits

- **Zero manual tracking**: All assets version-controlled
- **Consistent naming**: Automatic predicate-based naming
- **Optimized delivery**: WebP, compressed PNGs, appropriate sizes
- **Easy updates**: Artists update source → pipeline generates build
- **Game integration**: Single asset pack loads everything
- **Validation**: Automatic size/format checking
