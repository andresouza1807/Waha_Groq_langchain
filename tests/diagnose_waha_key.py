#!/usr/bin/env python3
"""
WAHA API Key Diagnostic - Check if WAHA_API_KEY is being loaded correctly
Run inside Docker container to diagnose 401 errors
"""

import os
import sys

print("=" * 80)
print("🔍 WAHA_API_KEY DIAGNOSTIC - Docker Environment Check")
print("=" * 80)

# TEST 1: Check OS environment variable
print("\n[TEST 1/3] OS Environment Variable (os.environ)")
print("-" * 80)

waha_key_os = os.environ.get('WAHA_API_KEY')
if waha_key_os:
    print(f"✅ FOUND in os.environ:")
    print(f"   Value: {waha_key_os[:15]}...{waha_key_os[-5:]}")
else:
    print(f"❌ NOT FOUND in os.environ")

# TEST 2: Check .env file via decouple
print("\n[TEST 2/3] .env File Variable (python-decouple)")
print("-" * 80)

try:
    from decouple import config
    waha_key_decouple = config('WAHA_API_KEY', default=None)
    if waha_key_decouple:
        print(f"✅ FOUND via decouple config:")
        print(f"   Value: {waha_key_decouple[:15]}...{waha_key_decouple[-5:]}")
    else:
        print(f"❌ NOT FOUND via decouple config")
except Exception as e:
    print(f"❌ Error loading via decouple: {e}")
    waha_key_decouple = None

# TEST 3: Check which source is being used
print("\n[TEST 3/3] Which Source Will Be Used (Priority)")
print("-" * 80)

final_key = os.environ.get('WAHA_API_KEY') or (
    config('WAHA_API_KEY', default=None) if 'config' in dir() else None)

if final_key:
    print(f"✅ WAHA_API_KEY IS CONFIGURED:")
    print(
        f"   Source: {'os.environ (Docker)' if os.environ.get('WAHA_API_KEY') else '.env file (decouple)'}")
    print(f"   Value: {final_key[:15]}...{final_key[-5:]}")
    print(f"\n✅ Authorization header will be:")
    print(f"   Authorization: Bearer {final_key[:15]}...")
else:
    print(f"❌ CRITICAL: WAHA_API_KEY NOT FOUND!")
    print(f"   os.environ: {waha_key_os}")
    print(f"   decouple:   {waha_key_decouple}")
    print(f"\n❌ Authorization header will be EMPTY!")
    print(f"   This causes 401 Unauthorized errors!")

# TEST 4: Show environment context
print("\n[CONTEXT] Environment Variables")
print("-" * 80)

print("Docker env file path: /app/.env (if inside container)")
print("Current working directory:", os.getcwd())
print("PYTHONPATH:", os.environ.get('PYTHONPATH', 'Not set'))

# List all WAHA-related env vars
print("\nAll environment variables containing 'WAHA':")
waha_vars = {k: v for k, v in os.environ.items() if 'WAHA' in k}
if waha_vars:
    for key, value in waha_vars.items():
        display_value = f"{value[:15]}...{value[-5:]}" if len(
            value) > 20 else value
        print(f"  {key}={display_value}")
else:
    print("  (None found)")

# SUMMARY
print("\n" + "=" * 80)
if final_key:
    print("✅ WAHA_API_KEY IS CONFIGURED - Should work!")
else:
    print("❌ WAHA_API_KEY IS MISSING - Will get 401 errors!")
print("=" * 80)

print("\nSolution if missing:")
print("1. Make sure WAHA_API_KEY is in .env file")
print("2. Restart Docker: docker-compose down && docker-compose up --build")
print("3. Check container env: docker exec <container> env | grep WAHA_API_KEY")
