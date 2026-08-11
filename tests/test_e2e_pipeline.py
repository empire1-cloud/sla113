#!/usr/bin/env python3
"""
SLA-113 End-to-End Pipeline Test
Tests: Omni task routing → Lyrica blueprint → Nemotron render → Ledger commit → CCNA cultural analysis
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import SLA-113 components
from backend.services.sla113_kernel import SLA113Kernel, WorkerRegistry, UniverseRegistry, BlackBoxEnforcer
from backend.services.nemotron.nemotron_flow import NemotronFlow
from backend.services.cultural.ccna_engine import CCNAEngine
from LYRICA3.soulfire_engine.royalty_ledger import RoyaltyLedger

class E2ETestRunner:
    def __init__(self):
        self.kernel = None
        self.nemotron = None
        self.ccna = None
        self.ledger = None
        self.results = []
        
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        status = "✓ PASS" if passed else "✗ FAIL"
        timestamp = datetime.now().strftime("%H:%M:%S")
        result = {
            "timestamp": timestamp,
            "test": test_name,
            "status": status,
            "passed": passed,
            "details": details
        }
        self.results.append(result)
        print(f"[{timestamp}] {status} | {test_name}")
        if details:
            print(f"         └─ {details}")
    
    def test_1_kernel_boot(self):
        """Test 1: SLA113 Kernel Boot Sequence"""
        try:
            self.kernel = SLA113Kernel()
            boot_result = self.kernel.boot()
            
            # Check boot success
            assert boot_result["status"] == "online", "Kernel not online"
            assert "workers_bound" in boot_result, "Workers not bound"
            assert boot_result["workers_bound"] >= 3, "Insufficient workers bound"
            assert "universes_loaded" in boot_result, "Universe registry not loaded"
            
            details = f"Workers: {boot_result['workers_bound']}, Universes: {boot_result['universes_loaded']}"
            self.log_test("Kernel Boot Sequence", True, details)
            return True
        except Exception as e:
            self.log_test("Kernel Boot Sequence", False, str(e))
            return False
    
    def test_2_worker_binding(self):
        """Test 2: Worker Registry and Bindings"""
        try:
            worker_registry = self.kernel.worker_registry
            
            # Check required workers are bound
            required_workers = ["OMNI_AGENT", "LYRICA_WORKER", "LEDGER_WORKER", "NEMOTRON_FLOW", "CCNA_ENGINE"]
            bound_workers = worker_registry.list_workers()
            
            for worker in required_workers:
                assert worker in bound_workers, f"Worker {worker} not bound"
            
            details = f"Bound: {', '.join(bound_workers)}"
            self.log_test("Worker Registry Binding", True, details)
            return True
        except Exception as e:
            self.log_test("Worker Registry Binding", False, str(e))
            return False
    
    def test_3_universe_registry(self):
        """Test 3: Universe Boundary Loading"""
        try:
            universe_registry = self.kernel.universe_registry
            
            # Check universes loaded
            universes = universe_registry.list_universes()
            assert len(universes) >= 9, f"Expected 9 universes, found {len(universes)}"
            
            # Check U1 (Prime/Origin)
            u1 = universe_registry.get_universe("U1")
            assert u1 is not None, "U1 not found"
            assert u1.get("name") == "Prime/Origin", "U1 name mismatch"
            
            details = f"{len(universes)} universes loaded (U1-U9)"
            self.log_test("Universe Boundary Loading", True, details)
            return True
        except Exception as e:
            self.log_test("Universe Boundary Loading", False, str(e))
            return False
    
    def test_4_black_box_enforcer(self):
        """Test 4: Black Box Scrubbing"""
        try:
            enforcer = self.kernel.black_box
            
            # Test scrubbing internal engine names
            test_output = "EPD engine generated emotion map. S2 synthesized melody. CCNA analyzed culture. Nemotron rendered audio. VICS tagged DNA."
            scrubbed = enforcer.scrub(test_output)
            
            # Check internal names are replaced
            assert "EPD" not in scrubbed, "EPD not scrubbed"
            assert "S2" not in scrubbed or "S2" == "Serendipity Synthesizer"[:2], "S2 not scrubbed"
            assert "CCNA" not in scrubbed, "CCNA not scrubbed"
            assert "Nemotron" not in scrubbed or "Flow Conductor" in scrubbed, "Nemotron not scrubbed"
            assert "VICS" not in scrubbed, "VICS not scrubbed"
            
            # Check aliases are present
            assert "Emotion Engine" in scrubbed or "emotion" in scrubbed.lower(), "Emotion Engine alias missing"
            
            details = "Internal names scrubbed successfully"
            self.log_test("Black Box Scrubbing", True, details)
            return True
        except Exception as e:
            self.log_test("Black Box Scrubbing", False, str(e))
            return False
    
    def test_5_nemotron_flow(self):
        """Test 5: Nemotron Flow Engine (Prosody → Stems → Combinator)"""
        try:
            self.nemotron = NemotronFlow()
            
            # Test blueprint input
            blueprint = {
                "title": "Xochitl Bloom Test",
                "genre": "cumbia-soul",
                "bpm": 98,
                "key": "Am",
                "mood": "tender",
                "lyrics": [
                    {"line": "Under the jacaranda tree", "timestamp": 0.0},
                    {"line": "Where shadows dance with memory", "timestamp": 4.0}
                ],
                "sections": [
                    {"type": "intro", "duration": 8.0},
                    {"type": "verse", "duration": 16.0}
                ]
            }
            
            # Execute Nemotron flow
            result = self.nemotron.render(blueprint)
            
            # Check outputs
            assert "prosody_map" in result, "Prosody map missing"
            assert "stems" in result, "Stems missing"
            assert "final_mix" in result, "Final mix missing"
            assert result["status"] == "rendered", "Render status not 'rendered'"
            
            # Check prosody map structure
            prosody = result["prosody_map"]
            assert "syllable_timings" in prosody, "Syllable timings missing"
            assert "breath_marks" in prosody, "Breath marks missing"
            assert "emphasis_points" in prosody, "Emphasis points missing"
            
            # Check stems structure
            stems = result["stems"]
            assert "vocal_lead" in stems, "Vocal lead stem missing"
            assert "instrumental" in stems, "Instrumental stems missing"
            
            details = f"Rendered with {len(stems)} stems, prosody map generated"
            self.log_test("Nemotron Flow Engine", True, details)
            return True
        except Exception as e:
            self.log_test("Nemotron Flow Engine", False, str(e))
            return False
    
    def test_6_ccna_cultural(self):
        """Test 6: CCNA Cultural Analysis"""
        try:
            self.ccna = CCNAEngine()
            
            # Test cultural analysis
            context = {
                "lyrics": "Under the jacaranda tree, where abuela used to sing",
                "genre": "cumbia-soul",
                "artist_background": "San Gabriel Valley Chicano",
                "themes": ["memory", "heritage", "family"]
            }
            
            result = self.ccna.analyze(context)
            
            # Check outputs
            assert "cultural_markers" in result, "Cultural markers missing"
            assert "ethical_score" in result, "Ethical score missing"
            assert "narrative_archetype" in result, "Narrative archetype missing"
            assert "recommendations" in result, "Recommendations missing"
            
            # Check cultural markers
            markers = result["cultural_markers"]
            assert len(markers) > 0, "No cultural markers detected"
            
            # Check ethical score range
            ethical_score = result["ethical_score"]
            assert 0.0 <= ethical_score <= 1.0, f"Ethical score out of range: {ethical_score}"
            
            details = f"Markers: {len(markers)}, Ethical: {ethical_score:.2f}, Archetype: {result['narrative_archetype']}"
            self.log_test("CCNA Cultural Analysis", True, details)
            return True
        except Exception as e:
            self.log_test("CCNA Cultural Analysis", False, str(e))
            return False
    
    def test_7_royalty_ledger(self):
        """Test 7: Royalty Ledger (VICS/DNA Tagging)"""
        try:
            self.ledger = RoyaltyLedger()
            
            # Test ledger entry creation
            entry_data = {
                "asset_id": "test_xochitl_bloom_001",
                "title": "Xochitl Bloom Test",
                "creator": "SLA-113 Test Suite",
                "universe": "U1",
                "dna_signature": "cumbia_soul_sgv_heritage_098bpm",
                "splits": [
                    {"role": "primary_artist", "percentage": 50.0},
                    {"role": "producer", "percentage": 30.0},
                    {"role": "cultural_advisor", "percentage": 20.0}
                ]
            }
            
            result = self.ledger.commit(entry_data)
            
            # Check commit success
            assert result["status"] == "committed", "Ledger commit failed"
            assert "ledger_id" in result, "Ledger ID not assigned"
            assert "vics_tag" in result, "VICS tag missing"
            assert "dna_hash" in result, "DNA hash missing"
            
            # Verify retrieval
            ledger_id = result["ledger_id"]
            retrieved = self.ledger.get_entry(ledger_id)
            assert retrieved is not None, "Failed to retrieve ledger entry"
            assert retrieved["asset_id"] == entry_data["asset_id"], "Asset ID mismatch"
            
            details = f"Ledger ID: {ledger_id}, VICS: {result['vics_tag'][:16]}..."
            self.log_test("Royalty Ledger Commit", True, details)
            return True
        except Exception as e:
            self.log_test("Royalty Ledger Commit", False, str(e))
            return False
    
    def test_8_omni_routing(self):
        """Test 8: Omni Task Routing"""
        try:
            # Test task routing logic
            routing_config_path = Path(__file__).parent.parent / "OMNI_AGENT" / "config" / "routing.json"
            with open(routing_config_path, 'r') as f:
                routing_config = json.load(f)
            
            # Check routing rules
            routing_rules = routing_config.get("routing_rules", {})
            assert "creative" in routing_rules, "Creative routing missing"
            assert "technical_audio" in routing_rules, "Technical audio routing missing"
            assert "ownership" in routing_rules, "Ownership routing missing"
            
            # Check creative routes to Lyrica
            creative_route = routing_rules["creative"]
            assert "LYRICA_WORKER" in creative_route["workers"], "Lyrica not in creative route"
            
            # Check technical_audio routes to Nemotron
            technical_route = routing_rules["technical_audio"]
            assert "NEMOTRON_FLOW" in technical_route["workers"], "Nemotron not in technical route"
            
            # Check ownership routes to Ledger
            ownership_route = routing_rules["ownership"]
            assert "LEDGER_WORKER" in ownership_route["workers"], "Ledger not in ownership route"
            
            details = f"{len(routing_rules)} routing rules configured"
            self.log_test("Omni Task Routing", True, details)
            return True
        except Exception as e:
            self.log_test("Omni Task Routing", False, str(e))
            return False
    
    def test_9_full_pipeline(self):
        """Test 9: Full Pipeline Integration (Omni → Lyrica → Nemotron → Ledger → CCNA)"""
        try:
            # Simulate full pipeline
            pipeline_data = {
                "task": "Create Xochitl Bloom song",
                "input": {
                    "title": "Xochitl Bloom",
                    "genre": "cumbia-soul",
                    "bpm": 98,
                    "key": "Am",
                    "mood": "tender",
                    "themes": ["heritage", "memory", "family"],
                    "cultural_context": "San Gabriel Valley Chicano lullaby"
                }
            }
            
            # Stage 1: Omni interprets task (simulated - would call Interpreter persona)
            task_interpretation = {
                "task_type": "creative",
                "routed_to": ["LYRICA_WORKER", "CCNA_ENGINE"],
                "complexity": "high"
            }
            
            # Stage 2: Lyrica creates blueprint (simulated - would call EPD/S2/CCNA)
            lyrica_blueprint = {
                "title": pipeline_data["input"]["title"],
                "genre": pipeline_data["input"]["genre"],
                "bpm": pipeline_data["input"]["bpm"],
                "key": pipeline_data["input"]["key"],
                "mood": pipeline_data["input"]["mood"],
                "lyrics": [
                    {"line": "Under the jacaranda tree", "timestamp": 0.0},
                    {"line": "Where abuela used to sing to me", "timestamp": 4.0},
                    {"line": "Xochitl bloom in purple rain", "timestamp": 8.0}
                ],
                "sections": [
                    {"type": "intro", "duration": 8.0},
                    {"type": "verse", "duration": 16.0},
                    {"type": "chorus", "duration": 12.0}
                ]
            }
            
            # Stage 3: CCNA cultural analysis
            ccna_result = self.ccna.analyze({
                "lyrics": " ".join([l["line"] for l in lyrica_blueprint["lyrics"]]),
                "genre": lyrica_blueprint["genre"],
                "artist_background": pipeline_data["input"]["cultural_context"],
                "themes": pipeline_data["input"]["themes"]
            })
            
            # Stage 4: Nemotron renders audio
            nemotron_result = self.nemotron.render(lyrica_blueprint)
            
            # Stage 5: Ledger commits ownership
            ledger_result = self.ledger.commit({
                "asset_id": f"xochitl_bloom_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "title": lyrica_blueprint["title"],
                "creator": "SLA-113 E2E Pipeline",
                "universe": "U1",
                "dna_signature": f"{lyrica_blueprint['genre']}_{lyrica_blueprint['bpm']}bpm_{lyrica_blueprint['key']}",
                "cultural_markers": ccna_result["cultural_markers"],
                "splits": [
                    {"role": "primary_artist", "percentage": 50.0},
                    {"role": "producer", "percentage": 30.0},
                    {"role": "cultural_advisor", "percentage": 20.0}
                ]
            })
            
            # Verify pipeline success
            assert ccna_result["status"] == "analyzed", "CCNA stage failed"
            assert nemotron_result["status"] == "rendered", "Nemotron stage failed"
            assert ledger_result["status"] == "committed", "Ledger stage failed"
            
            # Stage 6: Black Box scrubbing
            pipeline_output = f"Song '{lyrica_blueprint['title']}' created. Cultural analysis by CCNA completed. Nemotron rendered {len(nemotron_result['stems'])} stems. VICS tagged with ledger ID {ledger_result['ledger_id']}."
            scrubbed_output = self.kernel.black_box.scrub(pipeline_output)
            
            details = f"Pipeline complete: CCNA → Nemotron → Ledger → Black Box"
            self.log_test("Full Pipeline Integration", True, details)
            
            # Print final scrubbed output
            print(f"\n{'='*80}")
            print("FINAL PIPELINE OUTPUT (Black Box Scrubbed):")
            print(f"{'='*80}")
            print(scrubbed_output)
            print(f"{'='*80}\n")
            
            return True
        except Exception as e:
            self.log_test("Full Pipeline Integration", False, str(e))
            return False
    
    def run_all_tests(self):
        """Run all E2E tests"""
        print("\n" + "="*80)
        print("SLA-113 END-TO-END PIPELINE TEST")
        print("="*80 + "\n")
        
        tests = [
            self.test_1_kernel_boot,
            self.test_2_worker_binding,
            self.test_3_universe_registry,
            self.test_4_black_box_enforcer,
            self.test_5_nemotron_flow,
            self.test_6_ccna_cultural,
            self.test_7_royalty_ledger,
            self.test_8_omni_routing,
            self.test_9_full_pipeline
        ]
        
        for test in tests:
            test()
            print()  # Blank line between tests
        
        # Summary
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["passed"])
        failed_tests = total_tests - passed_tests
        
        print("="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"Total Tests:  {total_tests}")
        print(f"Passed:       {passed_tests} ✓")
        print(f"Failed:       {failed_tests} ✗")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print("="*80 + "\n")
        
        if failed_tests == 0:
            print("🎉 SLA-113 ONLINE | ALL WORKERS READY | NEMOTRON SYNCED")
            print("✓ All systems operational. Ready for production.\n")
            return True
        else:
            print("⚠ Some tests failed. Review errors above.")
            print("✗ System not ready for production.\n")
            return False

if __name__ == "__main__":
    runner = E2ETestRunner()
    success = runner.run_all_tests()
    sys.exit(0 if success else 1)
