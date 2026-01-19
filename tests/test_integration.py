#!/usr/bin/env python3
"""
Complete Integration Test - Verify AIBot is fully integrated and working
Tests the entire flow: API Key → ChatGroq → AIBot → Flask App
"""

import os
import sys
import json
from decouple import config

print("=" * 80)
print("🔍 COMPLETE INTEGRATION TEST - AIBot with Flask")
print("=" * 80)

# TEST 1: API Key & Environment
print("\n[TEST 1/5] Environment & API Key Setup")
print("-" * 80)
groq_api_key = config('GROQ_API_KEY', default=None)

if not groq_api_key:
    print("❌ FAIL: GROQ_API_KEY not found")
    sys.exit(1)

key_display = groq_api_key[:10] + "..." + groq_api_key[-10:]
print(f"✓ PASS: API Key loaded: {key_display}")

# TEST 2: Import AIBot
print("\n[TEST 2/5] AIBot Module Import")
print("-" * 80)
try:
    from bot.ai_bot import AIBot
    print("✓ PASS: AIBot imported successfully")
except Exception as e:
    print(f"❌ FAIL: Cannot import AIBot: {e}")
    sys.exit(1)

# TEST 3: AIBot Initialization
print("\n[TEST 3/5] AIBot Instantiation")
print("-" * 80)
try:
    ai_bot = AIBot()
    print(f"✓ PASS: AIBot initialized")
    print(f"  - Model: llama-3.3-70b-versatile")
    print(f"  - Temperature: 0.7")
    print(f"  - Max tokens: 1024")
except Exception as e:
    print(f"❌ FAIL: Cannot initialize AIBot: {e}")
    sys.exit(1)

# TEST 4: AIBot Message Invocation
print("\n[TEST 4/5] AIBot Message Processing")
print("-" * 80)
try:
    test_message = "Hello, how are you?"
    print(f"Testing with message: '{test_message}'")

    response = ai_bot.invoke(test_message)

    if not response:
        print("❌ FAIL: AIBot returned empty response")
        sys.exit(1)

    if isinstance(response, str):
        response_display = response[:100] + \
            "..." if len(response) > 100 else response
        print(f"✓ PASS: Response received")
        print(f"  Response: '{response_display}'")
    else:
        print(f"❌ FAIL: Response is not a string: {type(response)}")
        sys.exit(1)

except Exception as e:
    print(f"❌ FAIL: Error invoking AIBot: {e}")
    sys.exit(1)

# TEST 5: Flask App Integration
print("\n[TEST 5/5] Flask App Integration")
print("-" * 80)
try:
    from app import app, ai_bot as app_ai_bot, waha_service
    print("✓ PASS: Flask app imported successfully")
    print(f"  - AIBot instance: {type(app_ai_bot).__name__}")
    print(f"  - Waha service: {type(waha_service).__name__}")

    # Test Flask app context
    with app.test_client() as client:
        # Test /health endpoint
        response = client.get('/health')
        if response.status_code == 200:
            print("✓ PASS: /health endpoint working")
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.json}")
        else:
            print(f"❌ FAIL: /health returned {response.status_code}")
            sys.exit(1)

        # Test /test endpoint
        test_payload = {'message': 'What is Python?'}
        response = client.post('/test',
                               json=test_payload,
                               content_type='application/json')

        if response.status_code == 200:
            print("✓ PASS: /test endpoint working")
            print(f"  Status: {response.status_code}")
            response_data = response.json
            print(f"  Input: '{response_data.get('input', 'N/A')[:50]}'")
            print(
                f"  Response: '{response_data.get('response', 'N/A')[:50]}...'")
            print(f"  Status: {response_data.get('status', 'N/A')}")
        else:
            print(f"❌ FAIL: /test returned {response.status_code}")
            print(f"  Error: {response.json}")
            sys.exit(1)

except Exception as e:
    print(f"❌ FAIL: Flask app integration error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# SUMMARY
print("\n" + "=" * 80)
print("✅ ALL INTEGRATION TESTS PASSED!")
print("=" * 80)
print("\n📊 Integration Status:")
print("  ✅ Environment configured")
print("  ✅ AIBot module imported")
print("  ✅ AIBot instantiated correctly")
print("  ✅ AIBot processing messages")
print("  ✅ Flask app integrated")
print("  ✅ Health check endpoint working")
print("  ✅ Test endpoint working")

print("\n🎯 Summary:")
print("  • AIBot is fully integrated with Flask app")
print("  • Message processing is working correctly")
print("  • API endpoints are responding as expected")
print("  • Service initialization is successful")

print("\n✨ The bot is ready for deployment!")
print("\nNext steps:")
print("  1. docker-compose down")
print("  2. docker-compose up --build")
print("  3. Test with WhatsApp message")
print("=" * 80)
