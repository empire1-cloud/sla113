#!/usr/bin/env python3
"""
SLA-113 Master Test Suite
Runs all SLA-113 component tests in sequence
"""

import sys
import subprocess
from pathlib import Path

def run_test(test_name: str, test_script: str) -> bool:
    """Run a test script and return success status"""
    print(f"\n{'='*80}")
    print(f"Running: {test_name}")
    print(f"{'='*80}")
    
    result = subprocess.run(
        ["python3", test_script],
        cwd=Path(__file__).parent.parent,
        capture_output=False
    )
    
    return result.returncode == 0

def main():
    """Run all SLA-113 tests"""
    print("\n" + "="*80)
    print("SLA-113 MASTER TEST SUITE")
    print("="*80)
    
    tests = [
        ("Kernel Boot Test", "tests/test_kernel_boot.py"),
        ("Nemotron Flow Engine Test", "tests/test_nemotron_direct.py"),
        ("CCNA Cultural Engine Test", "tests/test_ccna_direct.py"),
        ("Full End-to-End Pipeline Test", "tests/test_full_pipeline.py"),
    ]
    
    results = []
    for test_name, test_script in tests:
        success = run_test(test_name, test_script)
        results.append((test_name, success))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUITE SUMMARY")
    print("="*80)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {test_name}")
    
    total = len(results)
    passed = sum(1 for _, success in results if success)
    failed = total - passed
    
    print("="*80)
    print(f"Total:  {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Rate:   {(passed/total)*100:.1f}%")
    print("="*80 + "\n")
    
    if failed == 0:
        print("🎉 SLA-113 ONLINE | ALL WORKERS READY | NEMOTRON SYNCED")
        print("✅ All tests passed. System ready for production.\n")
        return True
    else:
        print("⚠ Some tests failed. Review errors above.\n")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
