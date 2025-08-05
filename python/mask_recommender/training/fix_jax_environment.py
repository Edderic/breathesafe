#!/usr/bin/env python3
"""
Script to fix JAX version issues in the training environment.
This script updates JAX and JAXlib to compatible versions.
"""

import subprocess
import sys
import os

def run_command(command):
    """Run a command and return the result."""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {e.stderr}")
        return None

def fix_jax_environment():
    """Fix JAX version issues."""
    print("Fixing JAX environment...")
    
    # Update JAX and JAXlib to compatible versions
    commands = [
        "conda install -c conda-forge jax>=0.6.0 jaxlib>=0.6.0 -y",
        "pip install --upgrade jax jaxlib",
        "conda list | grep jax"
    ]
    
    for command in commands:
        print(f"Running: {command}")
        output = run_command(command)
        if output:
            print(output)
        else:
            print("Command failed")

if __name__ == "__main__":
    fix_jax_environment() 