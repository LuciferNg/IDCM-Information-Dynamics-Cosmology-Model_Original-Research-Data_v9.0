#!/usr/bin/env python3
"""Explore Bagpipes API for SED fitting"""
import bagpipes as pipes
import warnings
warnings.filterwarnings("ignore")

# Check the main module
print("=== pipes dir ===")
main_attrs = [a for a in dir(pipes) if not a.startswith('_')]
for a in sorted(main_attrs):
    print(f"  {a}")

# Check pipes.filters more
print("\n=== pipes.filters.filter_set methods ===")
fs = pipes.filters.filter_set
print(f"  get_photometry: {fs.get_photometry}")
print(f"  resample_filter_curves: {fs.resample_filter_curves}")

# Try the actual Bagpipes fitting interface
print("\n=== pipes.fit_interface ===")
if hasattr(pipes, 'fit_interface'):
    print([a for a in dir(pipes.fit_interface) if not a.startswith('_')])
if hasattr(pipes, 'fitting'):
    print([a for a in dir(pipes.fitting) if not a.startswith('_')])

# Check if there's a model module
print("\n=== pipes.models ===")
if hasattr(pipes, 'models'):
    print([a for a in dir(pipes.models) if not a.startswith('_')])

# Check Galaxy class
print("\n=== pipes.galaxy ===")
if hasattr(pipes, 'galaxy'):
    print([a for a in dir(pipes.galaxy) if not a.startswith('_')])

# Check if there's a fit method
print("\n=== pipes.fit ===")
if hasattr(pipes, 'fit'):
    print(f"  fit: {pipes.fit}")
if hasattr(pipes, 'run'):
    print(f"  run: {pipes.run}")

# Try creating a model
print("\n=== Trying to create model ===")
try:
    model = pipes.model_galaxy
    print(f"  model_galaxy: {model}")
except:
    print("  No model_galaxy")