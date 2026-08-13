#!/usr/bin/env node
// Asset validation script
// Usage: node assets/scripts/validate-assets.mjs

import { readdir, stat, access } from 'node:fs/promises';
import { join } from 'node:path';

const root = process.cwd();

async function checkFileExists(filepath) {
  try {
    await access(join(root, filepath));
    return true;
  } catch (err) {
    return false;
  }
}

async function getImageInfo(filepath) {
  const { exec } = await import('node:child_process');
  return new Promise((resolve) => {
    exec(`magick identify -format "%w %h %b" "${join(root, filepath)}"`, (error, stdout) => {
      if (error) {
        resolve(null);
        return;
      }
      const [width, height, size] = stdout.trim().split(' ');
      resolve({ width: parseInt(width), height: parseInt(height), size: size });
    });
  });
}

async function validateAssets() {
  console.log('🔍 Validating game assets...\n');

  // Required directories
  const requiredDirs = [
    'assets/source/characters',
    'assets/source/bosses', 
    'assets/source/effects',
    'assets/source/ui',
    'assets/source/game-covers',
    'assets/raw/ui',
    'frontend/public/assets/generated/atlases'
  ];

  // Check directory structure
  for (const dir of requiredDirs) {
    const exists = await checkFileExists(dir);
    console.log(exists ? `✅ ${dir}` : `❌ ${dir} (MISSING)`);
  }

  console.log('\n');

  // Check for generated atlases
  const atlasDir = 'frontend/public/assets/generated/atlases';
  const expectedAtlases = [
    'characters-atlas.png',
    'characters-atlas.json',
    'bosses-atlas.png', 
    'bosses-atlas.json',
    'effects-atlas.png',
    'effects-atlas.json',
    'ui-atlas.png',
    'ui-atlas.json',
    'arcade-ui.png',
    'arcade-ui.json',
    'game-covers-atlas.png',
    'game-covers-atlas.json'
  ];

  let atlasCount = 0;
  for (const atlas of expectedAtlases) {
    const exists = await checkFileExists(`${atlasDir}/${atlas}`);
    if (exists) atlasCount++;
    console.log(`${exists ? '✅' : '❌'} ${atlasDir}/${atlas}`);
  }

  console.log(`\n📊 Atlas Summary: ${atlasCount}/${expectedAtlases.length} atlases generated`);

  // Check arcade pack exists
  const packExists = await checkFileExists('frontend/public/assets/arcade-pack.json');
  console.log(`${packExists ? '✅' : '❌'} frontend/public/assets/arcade-pack.json`);

  // Sample image validation
  console.log('\n🖼️  Sample image validation:');
  const sampleImages = [
    'frontend/public/assets/generated/atlases/characters-atlas.png',
    'frontend/public/assets/generated/atlases/ui-atlas.png'
  ];

  for (const img of sampleImages) {
    const exists = await checkFileExists(img);
    if (exists) {
      const info = await getImageInfo(img);
      if (info) {
        console.log(`✅ ${img} - ${info.width}x${info.height}`);
      } else {
        console.log(`❌ ${img} - Could not read image info`);
      }
    } else {
      console.log(`⚠️  ${img} - File not found`);
    }
  }

  console.log('\n🎯 Asset validation complete!');
  console.log('💡 Run \'npm run assets:build\' to generate missing assets');
}

// Run validation
validateAssets().catch(console.error);
