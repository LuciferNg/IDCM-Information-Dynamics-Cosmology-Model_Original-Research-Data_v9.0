#!/usr/bin/env python3
"""Explore Bagpipes fitting API from source"""
import bagpipes as pipes
import inspect, warnings
warnings.filterwarnings("ignore")

# Check fit_interface
print("=== fit_interface ===")
for name, obj in inspect.getmembers(pipes.fit_interface):
    if not name.startswith('_'):
        print(f"  {name}: {type(obj).__name__}")

# Check fitting
print("\n=== fitting ===")
if hasattr(pipes, 'fitting'):
    for name, obj in inspect.getmembers(pipes.fitting):
        if not name.startswith('_'):
            print(f"  {name}: {type(obj).__name__}")

# Check galaxy
print("\n=== galaxy ===")
if hasattr(pipes, 'galaxy'):
    for name, obj in inspect.getmembers(pipes.galaxy):
        if not name.startswith('_'):
            print(f"  {name}: {type(obj).__name__}")

# Try to create galaxy
print("\n=== Trying Galaxy ===")
try:
    g = pipes.galaxy.Galaxy(2859, None, 8.106)
    print(f"  Galaxy created: {g}")
except Exception as e:
    print(f"  Error: {e}")

# Check create_galaxy
print("\n=== create_galaxy ===")
if hasattr(pipes, 'create_galaxy'):
    print(f"  create_galaxy: {pipes.create_galaxy}")
    print(inspect.signature(pipes.create_galaxy))

# Check fit_galaxy
print("\n=== fit_galaxy ===")
if hasattr(pipes, 'fit_galaxy'):
    print(f"  fit_galaxy: {pipes.fit_galaxy}")
    print(inspect.signature(pipes.fit_galaxy))