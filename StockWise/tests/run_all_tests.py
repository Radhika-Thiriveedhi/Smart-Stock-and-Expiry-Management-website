#!/usr/bin/env python3
"""
StockWise Test Suite Runner
Discovers and executes all unit tests across the test directory.
"""
import unittest
import os
import sys

def run_tests():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.abspath(os.path.join(test_dir, ".."))
    sys.path.insert(0, project_dir)

    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=test_dir, pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Errors: {len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print("=" * 50)

    if result.wasSuccessful():
        print("ALL TESTS PASSED SUCCESSFULLY! ✓")
        return 0
    else:
        print("SOME TESTS FAILED! ✗")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())
