#!/usr/bin/env python3
"""
Script to test Groq API connection and bot functionality.
Verifies if the API key is correct and the bot can generate responses.
"""

import os
import sys
import logging
from decouple import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

print("=" * 70)
print("GROQ API CONNECTION TEST")
print("=" * 70)

# 1. Check if API key is loaded
groq_api_key = config('GROQ_API_KEY', default=None)

print("\n[1/4] Checking GROQ_API_KEY...")
if not groq_api_key:
    print("❌ ERROR: GROQ_API_KEY not found in .env")
    print("   Make sure .env file exists and contains:")
    print("   GROQ_API_KEY=gsk_your_key_here")
    sys.exit(1)

key_display = groq_api_key[:10] + "..." + groq_api_key[-10:]
print(f"✓ API Key found: {key_display}")

if not groq_api_key.startswith('gsk_'):
    print(
        f"⚠️  WARNING: Key doesn't start with 'gsk_' (starts with: {groq_api_key[:10]})")

# 2. Initialize ChatGroq
print("\n[2/4] Initializing ChatGroq...")
try:
    from langchain_groq import ChatGroq

    os.environ['GROQ_API_KEY'] = groq_api_key

    chat = ChatGroq(
        model='llama-3.3-70b-versatile',
        temperature=0.7,
        max_tokens=1024,
        api_key=groq_api_key,
    )
    print("✓ ChatGroq initialized successfully")
except Exception as e:
    print(f"❌ ERROR initializing ChatGroq: {e}")
    print(f"   Error type: {type(e).__name__}")
    sys.exit(1)

# 3. Test simple API call
print("\n[3/4] Testing API call...")
try:
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import PromptTemplate

    prompt = PromptTemplate(
        input_variables=['question'],
        template="Answer briefly: {question}"
    )

    chain = prompt | chat | StrOutputParser()

    response = chain.invoke({
        'question': 'What is 2+2?'
    })

    if not response:
        print("❌ ERROR: API returned empty response")
        sys.exit(1)

    print("✓ API call successful!")
    print(f"   Response: {response[:100]}...")

except Exception as e:
    print(f"❌ ERROR during API call: {e}")
    print(f"   Error type: {type(e).__name__}")
    if "401" in str(e) or "Unauthorized" in str(e):
        print("   >> CAUSE: Invalid or expired API key")
        print("   >> FIX: Check your key at https://console.groq.com")
    elif "timeout" in str(e).lower():
        print("   >> CAUSE: Connection timeout")
        print("   >> FIX: Check your internet connection")
    sys.exit(1)

# 4. Test bot module
print("\n[4/4] Testing AIBot module...")
try:
    from bot.ai_bot import AIBot

    ai_bot = AIBot()
    response = ai_bot.invoke("Hello, how are you?")

    if not response:
        print("❌ ERROR: AIBot returned no response")
        sys.exit(1)

    print("✓ AIBot works correctly!")
    print(f"   Response: {response[:100]}...")

except Exception as e:
    print(f"❌ ERROR testing AIBot: {e}")
    print(f"   Error type: {type(e).__name__}")
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ ALL TESTS PASSED!")
print("=" * 70)
print("\nYour Groq API is working correctly.")
print("You can now start the containers:")
print("  $ docker-compose down && docker-compose up --build")
print("=" * 70)
