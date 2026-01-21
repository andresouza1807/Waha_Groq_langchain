#!/usr/bin/env python3
"""
Script para obter e exibir o QR Code da Evolution API
"""
import requests
import time
import sys

API_URL = "http://localhost:8080"
API_KEY = "B6D711FCDE4D4FD5936544120E713976"
INSTANCE_NAME = "bot"

headers = {
    "apikey": API_KEY
}

print(f"Aguardando QR Code para a instância '{INSTANCE_NAME}'...")
print("=" * 60)

for attempt in range(30):
    try:
        # Tenta obter o QR Code
        response = requests.get(
            f"{API_URL}/instance/connect/{INSTANCE_NAME}",
            headers=headers,
            timeout=5
        )

        if response.status_code == 200:
            data = response.json()

            if 'base64' in data or 'qrcode' in data:
                qr_data = data.get('base64') or data.get(
                    'qrcode', {}).get('base64')

                if qr_data:
                    print("\n✅ QR Code encontrado!")
                    print(f"\nAcesse o painel web: {API_URL}/manager/")
                    print(f"\nOu use este link direto:")
                    print(f"{API_URL}/instance/qrcode/{INSTANCE_NAME}")
                    print("\nAbra o WhatsApp no celular e escaneie o QR Code!")
                    sys.exit(0)

            # Verifica se já está conectado
            if data.get('instance', {}).get('state') == 'open':
                print("\n✅ Instância já está conectada!")
                sys.exit(0)

        print(f"Tentativa {attempt + 1}/30 - Aguardando QR Code...", end="\r")
        time.sleep(2)

    except Exception as e:
        print(f"\nErro: {e}")
        time.sleep(2)

print("\n\n❌ Timeout: QR Code não foi gerado.")
print(f"\nTente acessar manualmente: {API_URL}/manager/")
