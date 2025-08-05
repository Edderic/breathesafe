#!/usr/bin/env python3
"""
Test runner for the training module.
Run this script to execute all tests for the training module.
"""

import pytest
import sys
import os

# Add the current directory to the path so we can import the training module
sys.path.insert(0, os.path.dirname(__file__))

if __name__ == "__main__":
    # Run all tests in the tests directory
    test_dir = os.path.join(os.path.dirname(__file__), "tests")
    pytest.main([test_dir, "-v"]) 