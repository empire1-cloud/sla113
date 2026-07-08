#!/usr/bin/env python3
"""
CCNA Cultural Engine Direct Test
Tests cultural marker extraction, ethical scoring, and narrative archetypes
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.cultural.ccna_engine import CCNAEngine

def test_ccna():
    """Test CCNA Cultural Engine execution"""
    print("\n" + "="*80)
    print("CCNA CULTURAL ENGINE TEST")
    print("="*80 + "\n")
    
    # Initialize engine
    print("[1/4] Initializing CCNA Cultural Engine...")
    engine = CCNAEngine()
    print("✓ Engine initialized\n")
    
    # Create test context
    print("[2/4] Creating test cultural context...")
    text = "Under the jacaranda tree, where abuela used to sing to me, Xochitl bloom in purple rain. In San Gabriel Valley, where the barrio raised me, memories of familia y culture remain."
    genre = "cumbia-soul"
    print(f"✓ Text: {len(text)} chars")
    print(f"  └─ Genre: {genre}\n")
    
    # Execute cultural analysis
    print("[3/4] Executing CCNA cultural analysis...")
    print("  ├─ Cultural Marker Extraction")
    print("  ├─ Ethical Gradient Scoring")
    print("  └─ Narrative Archetype Detection")
    result = engine.analyze(text, genre=genre)
    print(f"✓ Analysis ID: {result.get('analysis_id', 'N/A')}\n")
    
    # Verify outputs
    print("[4/4] Verifying analysis outputs...")
    
    # Check cultural markers
    if "cultural_markers" in result:
        markers = result["cultural_markers"]
        print(f"✓ Cultural markers detected: {result.get('marker_count', len(markers))}")
        for marker in markers[:5]:  # Show first 5
            print(f"  └─ {marker.get('category', 'unknown')}: {marker.get('marker', 'N/A')}")
    else:
        print("✗ Cultural markers missing")
    
    # Check ethical gradient
    if "ethical_gradient" in result:
        gradient = result["ethical_gradient"]
        score = gradient.get("score", 0.0)
        level = gradient.get("assessment", "unknown")
        print(f"✓ Ethical gradient score: {score:.2f}")
        print(f"  └─ Level: {level}")
    else:
        print("✗ Ethical gradient missing")
    
    # Check narrative archetype
    if "narrative_archetype" in result:
        archetype = result["narrative_archetype"]
        print(f"✓ Narrative archetype: {archetype}")
    else:
        print("✗ Narrative archetype missing")
    
    # Check creative intent trace
    if "creative_intent_trace" in result:
        intent = result["creative_intent_trace"]
        print(f"✓ Creative intent trace generated")
        print(f"  └─ Summary: {intent.get('summary', 'N/A')[:60]}...")
    else:
        print("✗ Creative intent trace missing")
    
    print()
    
    print("="*80)
    if result.get('analysis_id'):
        print("✅ CCNA CULTURAL ENGINE ONLINE")
    else:
        print("❌ ANALYSIS FAILED")
    print("="*80 + "\n")
    
    return bool(result.get('analysis_id'))

if __name__ == "__main__":
    success = test_ccna()
    sys.exit(0 if success else 1)
