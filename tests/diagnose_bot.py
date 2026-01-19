#!/usr/bin/env python3
"""Comprehensive bot diagnostics script."""

import os
import sys
import requests
import logging
from decouple import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_env_vars():
    """Check if all required environment variables are set."""
    print("\n" + "="*60)
    print("🔍 CHECKING ENVIRONMENT VARIABLES")
    print("="*60)

    required_vars = {
        'GROQ_API_KEY': 'Groq API Key',
        'WAHA_API_KEY': 'Waha API Key',
        'WAHA_URL': 'Waha URL (optional)',
        'WAHA_SESSION_NAME': 'Waha Session Name (optional)',
    }

    all_ok = True
    for var, description in required_vars.items():
        value = os.environ.get(var) or config(var, default=None)
        if value:
            masked = value[:10] + '...' if len(value) > 10 else value
            print(f"✓ {var}: {masked}")
        else:
            print(f"✗ {var}: NOT SET - {description}")
            all_ok = False

    return all_ok


def check_waha_connection():
    """Test connection to WAHA API."""
    print("\n" + "="*60)
    print("🔍 CHECKING WAHA CONNECTION")
    print("="*60)

    waha_url = os.environ.get('WAHA_URL') or config(
        'WAHA_URL', default='http://wpp_bot_waha:3000')
    waha_api_key = os.environ.get('WAHA_API_KEY') or config(
        'WAHA_API_KEY', default=None)

    print(f"WAHA URL: {waha_url}")
    print(f"WAHA API Key: {'SET' if waha_api_key else 'NOT SET'}")

    headers = {'Content-Type': 'application/json'}
    if waha_api_key:
        headers['Authorization'] = f'Bearer {waha_api_key}'

    try:
        url = f'{waha_url}/api/status'
        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code == 200:
            print(f"✓ WAHA connection successful")
            print(f"  Response: {response.json()}")
            return True
        else:
            print(f"✗ WAHA returned {response.status_code}")
            print(f"  Body: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to WAHA at {waha_url}")
        print(f"  Make sure WAHA container is running and accessible")
        return False
    except requests.exceptions.Timeout:
        print(f"✗ WAHA connection timeout at {waha_url}")
        return False
    except Exception as e:
        print(f"✗ Error connecting to WAHA: {e}")
        return False


def check_groq_connection():
    """Test connection to Groq API."""
    print("\n" + "="*60)
    print("🔍 CHECKING GROQ CONNECTION")
    print("="*60)

    groq_api_key = os.environ.get('GROQ_API_KEY') or config(
        'GROQ_API_KEY', default=None)

    if not groq_api_key:
        print("✗ GROQ_API_KEY not set")
        return False

    if not groq_api_key.startswith('gsk_'):
        print(
            f"⚠ GROQ_API_KEY has unusual format (starts with: {groq_api_key[:10]})")

    try:
        from langchain_groq import ChatGroq
        chat = ChatGroq(
            model='llama-3.3-70b-versatile',
            api_key=groq_api_key,
            temperature=0.7,
            max_tokens=100
        )

        # Test with a simple message
        response = chat.invoke(
            'Olá, como você está? Responda em uma frase curta.')
        if response and response.content:
            print(f"✓ Groq connection successful")
            print(f"  Test response: {response.content[:100]}...")
            return True
        else:
            print(f"✗ Groq returned empty response")
            return False
    except Exception as e:
        print(f"✗ Error connecting to Groq: {e}")
        return False


def check_bot_initialization():
    """Test if bot can be initialized."""
    print("\n" + "="*60)
    print("🔍 CHECKING BOT INITIALIZATION")
    print("="*60)

    try:
        from bot.ai_bot import AIBot
        bot = AIBot()
        print("✓ AIBot initialized successfully")

        # Test with a simple message
        response = bot.invoke("Teste")
        if response:
            print(f"✓ AIBot can generate responses")
            print(f"  Test response: {response[:100]}...")
            return True
        else:
            print(f"✗ AIBot generated empty response")
            return False
    except Exception as e:
        print(f"✗ Error initializing AIBot: {e}")
        return False


def check_waha_initialization():
    """Test if Waha client can be initialized."""
    print("\n" + "="*60)
    print("🔍 CHECKING WAHA CLIENT INITIALIZATION")
    print("="*60)

    try:
        from services.waha import Waha
        waha = Waha()
        print("✓ Waha client initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Error initializing Waha client: {e}")
        return False


def check_logs():
    """Check if bot.log file exists and show recent entries."""
    print("\n" + "="*60)
    print("🔍 CHECKING BOT LOGS")
    print("="*60)

    log_file = 'bot.log'
    if not os.path.exists(log_file):
        print(f"✗ Log file not found: {log_file}")
        return

    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()

        print(f"✓ Log file found with {len(lines)} entries")
        print("\nLast 20 log entries:")
        print("-" * 60)
        for line in lines[-20:]:
            print(line.rstrip())
    except Exception as e:
        print(f"✗ Error reading log file: {e}")


def main():
    """Run all diagnostics."""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "🤖 BOT DIAGNOSTICS 🤖" + " "*20 + "║")
    print("╚" + "="*58 + "╝")

    results = {
        'Environment Variables': check_env_vars(),
        'WAHA Connection': check_waha_connection(),
        'Groq Connection': check_groq_connection(),
        'Waha Client Init': check_waha_initialization(),
        'AIBot Init': check_bot_initialization(),
    }

    check_logs()

    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)

    for test, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test}")

    all_passed = all(results.values())

    print("\n" + "="*60)
    if all_passed:
        print("✓ All checks passed! Bot should be working.")
    else:
        print("✗ Some checks failed. Fix the issues above.")
    print("="*60 + "\n")

    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
