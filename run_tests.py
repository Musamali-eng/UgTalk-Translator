"""
Test runner script for AI-Powered Web Service
"""

import subprocess
import sys

def run_tests():
    """Run all tests with pytest"""
    print("=" * 60)
    print("Running Tests for AI-Powered Web Service")
    print("=" * 60)
    
    # Run pytest with verbose output
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', 'tests/', '-v', '--tb=short'],
        capture_output=False
    )
    
    print("=" * 60)
    if result.returncode == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")
    print("=" * 60)
    
    return result.returncode

if __name__ == '__main__':
    sys.exit(run_tests())