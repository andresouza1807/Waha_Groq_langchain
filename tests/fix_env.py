#!/usr/bin/env python3
"""
Script to validate and fix .env file.
Removes spaces, quotes and validates key format.
Ensures WAHA_API_KEY is properly configured for Docker.
"""

import os
import sys

ENV_FILE = '.env'

print("=" * 80)
print("🔧 .ENV FILE VALIDATION AND FIX - WAHA Authentication Ready")
print("=" * 80)

# Check if file exists
if not os.path.exists(ENV_FILE):
    print(f"\n❌ File {ENV_FILE} not found!")
    print("   Creating example file...")
    with open(ENV_FILE, 'w') as f:
        f.write("GROQ_API_KEY=your_groq_key_here\n")
        f.write("WAHA_API_KEY=your_waha_api_key_here\n")
        f.write("WAHA_DASHBOARD_USERNAME=admin\n")
        f.write("WAHA_DASHBOARD_PASSWORD=your_password\n")
    print(f"✓ File {ENV_FILE} created!")
    print("   Edit the file and add your API keys")
    sys.exit(0)

# Read file
print(f"\n📄 Reading {ENV_FILE}...")
with open(ENV_FILE, 'r') as f:
    content = f.read()

original_content = content

# Process lines
lines = content.split('\n')
corrected_lines = []
corrections = []

for line in lines:
    # Skip empty lines and comments
    if not line.strip() or line.strip().startswith('#'):
        corrected_lines.append(line)
        continue

    # Process lines with =
    if '=' in line:
        key, value = line.split('=', 1)
        original_value = value

        # Clean value
        value = value.strip()  # Remove spaces
        value = value.strip("'\"")  # Remove quotes

        if key.strip() == 'GROQ_API_KEY':
            # Specific validations for GROQ_API_KEY
            if not value:
                print(f"⚠️  WARNING: GROQ_API_KEY is empty!")
                corrections.append("GROQ_API_KEY was empty")
            elif not value.startswith('gsk_'):
                print(f"⚠️  WARNING: GROQ_API_KEY format issue")
                print(f"             Expected format: gsk_xxx")
                print(f"             Found: {value[:20]}...")
                corrections.append("GROQ_API_KEY format issue detected")

        # Rebuild line
        corrected_line = f"{key.strip()}={value}"

        if original_value != value:
            print(f"✓ Fixed: {key.strip()}=***[fixed]***")
            corrections.append(f"Removed spaces/quotes from {key.strip()}")

        corrected_lines.append(corrected_line)
    else:
        corrected_lines.append(line)

# Join lines
corrected_content = '\n'.join(corrected_lines)

# Save if changes were made
if corrected_content != original_content:
    print("\n⚠️  Changes detected!")
    print("Fixing file...")

    with open(ENV_FILE, 'w') as f:
        f.write(corrected_content)

    print("✓ File updated successfully!")
    print("\nChanges made:")
    for correction in corrections:
        print(f"  • {correction}")
else:
    print("\n✓ File is correct!")

# Final verification
print("\n" + "=" * 70)
print("FINAL VERIFICATION")
print("=" * 70)

with open(ENV_FILE, 'r') as f:
    for line in f:
        if line.strip() and not line.strip().startswith('#'):
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()

                if key == 'GROQ_API_KEY':
                    if value.startswith('gsk_'):
                        display = value[:10] + "..." + value[-10:]
                        print(f"✓ {key}: {display}")
                    else:
                        print(f"❌ {key}: INVALID VALUE")
                else:
                    print(f"ℹ️  {key}: [loaded]")

print("\n" + "=" * 70)
print("Next step: Rebuild containers")
print("$ docker-compose down && docker-compose up --build")
print("=" * 70)
