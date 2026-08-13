# SLA113 Game Asset Pipeline Configuration
# Using NVIDIA Omniverse Tools for Sprite, Texture, and 3D Asset Creation

## Asset Pipeline Overview
This document outlines the asset creation and optimization workflow for the Firekirin fish shooting/juwa slots arcade game using NVIDIA Omniverse tools.

## Directory Structure
```
/assets
  /sprites       # 2D sprites (fish, weapons, UI elements)
  /textures      # Texture atlases and materials
  /models        # 3D models (boss characters, avatars)
  /animations    # Animation sequences
  /ui            # User interface assets
```

## NVIDIA Omniverse Tools to Install

### 1. omniverse-usd-performance-tuning
**Purpose**: Optimize 3D models, textures, and animations for real-time performance
**Usage**: 
- Generate Level of Detail (LOD) models for distant objects
- Optimize texture atlases for sprite sheets
- Bake lighting and ambient occlusion
- Create collision meshes for hit detection
- Optimize animation skeletons and keyframes

### 2. omniverse-cad-to-simready  
**Purpose**: Convert CAD/models to game-ready assets with proper LODs, materials, and physics
**Usage**:
- Convert fish models from Blender/Maya to USD format
- Create physics-ready collision meshes
- Generate material variants for different fish types
- Prepare assets for real-time rendering

### 3. physicsnemo-discover
**Purpose**: Realistic physics simulation for game elements
**Usage**:
- Simulate fish schooling patterns and swimming behaviors
- Create realistic lure physics and water effects
- Generate particle systems for explosions, splashes, and effects
- Model buoyancy and fluid dynamics for underwater scenes

## Asset Creation Workflow

### 1. Fish Sprites & Animations
**Source Creation**:
- Create base fish models in Blender/Maya
- Design sprite sheets with multiple angles (8-directional recommended)
- Create animation cycles: idle, swim, attack, death

**Optimization Process**:
1. Import models into Omniverse Create
2. Use `omniverse-usd-performance-tuning` to:
   - Generate LODs (full, medium, low detail)
   - Optimize texture atlases (combine multiple fish into sheets)
   - Bake ambient occlusion for better lighting
   - Create collision meshes (simplified shapes for hit detection)
3. Export optimized USD assets
4. Convert to sprite sheets using texture packing tools
5. Validate with `qc_check.py` for animation consistency

### 2. Weapon Effects & UI Elements
**Source Creation**:
- Design weapon muzzle flashes, trails, and impact effects
- Create UI buttons, panels, and icons
- Design avatar cosmetic items (hats, outfits, accessories)

**Optimization Process**:
1. Create vector art in Illustrator or Photoshop
2. Import to Omniverse for effect simulation
3. Use `omniverse-usd-performance-tuning` for:
   - Particle system optimization
   - Shader complexity reduction
   - Texture compression without quality loss
4. Generate sprite sheets for animated effects
5. Create atlas textures for UI elements

### 3. Boss Characters & 3D Models
**Source Creation**:
- Model boss characters in high detail
- Create animation rigs for complex movements
- Design multiple phases/transformations

**Optimization Process**:
1. Use `omniverse-cad-to-simready` to:
   - Generate automatic LODs based on screen size
   - Create optimized collision meshes
   - Bake normal and displacement maps
   - Optimize material complexity
2. Apply physics simulations with `physicsnemo-discover` for:
   - Realistic movement patterns
   - Environmental interactions
   - Destruction/death animations
3. Test performance targets (60 FPS minimum)
4. Validate animation consistency with `qc_check.py`

### 4. Backgrounds & Environmental Assets
**Source Creation**:
- Create parallax background layers
- Design environmental props (corals, rocks, plants)
- Develop animated water surfaces

**Optimization Process**:
1. Use texture atlasing for background elements
2. Create seamless tiling textures
3. Implement level-of-detail for distant scenery
4. Use billboard sprites for distant objects
5. Optimize with `omniverse-usd-performance-tuning`

## Quality Control Integration

### Using qc_check.py for Animation Validation
The existing `qc_check.py` script can be integrated into the asset pipeline to validate:

1. **Bounding Box Consistency**: Detect scale drift between animation frames
2. **Palette Consistency**: Ensure color schemes remain uniform
3. **Transparency Check**: Prevent stray opaque backgrounds in PNG sprites
4. **Frame Count Validation**: Verify all requested animation states are generated

**Usage Example**:
```bash
# Validate fish swimming animation
python3 qc_check.py --frame-dir ./assets/sprites/fish/golden_shark/swim --manifest ./assets/sprites/fish/golden_shark/swim/generation_manifest.json

# Validate weapon effect animations  
python3 qc_check.py --frame-dir ./assets/effects/laser/blast --manifest ./assets/effects/laser/blast/generation_manifest.json
```

### Automated Validation Pipeline
1. Artist creates animation frames
2. System generates manifest file listing expected frames
3. `qc_check.py` runs automatically to detect issues
4. Report generated for artist review
5. Assets only promoted to main branch after passing QC

## Performance Targets
- **Target FPS**: 60 FPS minimum on target devices
- **Texture Atlas Size**: ≤ 2048x2048 for mobile compatibility
- **Draw Calls**: < 100 per frame for optimal performance
- **Memory Usage**: < 150MB for asset runtime usage
- **Load Time**: < 3 seconds for initial asset loading

## NVIDIA Skill Installation Commands

To install the recommended NVIDIA skills for this asset pipeline:

```bash
# Install Omniverse USD Performance Tuning
npx skills add nvidia/skills --skill omniverse-usd-performance-tuning --global --yes

# Install Omniverse CAD to SimReady  
npx skills add nvidia/skills --skill omniverse-cad-to-simready --global --yes

# Install PhysicsNeMo Discover
npx skills add nvidia/skills --skill physicsnemo-discover --global --yes

# Optional: For AI-enhanced asset creation
npx skills add nvidia/skills --skill tao-toolkit --global --yes
npx skills add nvidia/skills --skill nemo --global --yes
```

## Asset Naming Convention
```
[asset_type]_[entity]_[variation]_[state].[ext]
Examples:
  sprite_fish_clownfish_idle_01.png
  sprite_weapon_laser_blast_01.png  
  model_boss_jagwarrior_high.usd
  texture_ui_button_play_normal.png
  animation_fish_shark_swim_cycle.usda
```

## Version Control Guidelines
- Store source assets (PSD, AI, BLEND, MA files) in LFS
- Store optimized/runtime assets in regular Git
- Use tags for asset pipeline versions
- Maintain separation between artistic source and optimized runtime assets

## Integration with Game Systems
- **Player Progression**: Unlock higher quality sprite variants as rewards
- **Dynamic Events**: Special event-themed assets (holiday skins, tournament items)
- **Daily/Login Rewards**: Exclusive cosmetic assets as rewards
- **Limited-Time Events**: Seasonal asset packs with unique visual themes

## Next Steps for Implementation
1. Install recommended NVIDIA skills using commands above
2. Create asset creation templates and guidelines for artists
3. Set up automated QC validation in build pipeline
4. Create sample asset packs for testing integration
5. Establish artist-to-developer handoff process
6. Performance test optimized assets in actual game scenes