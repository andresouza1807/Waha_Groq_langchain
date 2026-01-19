"""WhatsApp Bot API using Evolution API and Groq LLM."""

import logging
import json
import os
from typing import Tuple, Dict, Any
from datetime import datetime
from bot.ai_bot import AIBot
from services.evolution_api import EvolutionAPI
from services.waha import Waha
from flask import Flask, request, jsonify
from functools import wraps

# Configure logging with file handler
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Determine which WhatsApp service to use
USE_EVOLUTION = os.getenv('USE_EVOLUTION_API', 'true').lower() == 'true'

# Initialize services globally
if USE_EVOLUTION:
    whatsapp_service = EvolutionAPI()
    logger.info('✓ Using Evolution API for WhatsApp')
else:
    whatsapp_service = Waha()
    logger.info('✓ Using WAHA for WhatsApp')

ai_bot = AIBot()


def log_request(f):
    """Decorator to log all requests."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger.info(
            f'REQUEST: {request.method} {request.path} from {request.remote_addr}')
        try:
            result = f(*args, **kwargs)
            return result
        except Exception as e:
            logger.error(f'REQUEST ERROR: {e}', exc_info=True)
            raise
    return decorated_function


@app.route('/health', methods=['GET'])
@log_request
def health() -> Tuple[Dict[str, str], int]:
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'service': 'WhatsApp Bot API'
    }), 200


@app.route('/wpp-bot-api', methods=['POST'])
@log_request
def webhook() -> Tuple[Dict[str, Any], int]:
    try:
        data = request.json
        logger.info(f'Webhook received: {json.dumps(data, indent=2)}')

        # WAHA sempre deve receber 200, mesmo em eventos ignorados
        if not data or not isinstance(data, dict):
            logger.info('Ignoring invalid data format')
            return jsonify({'ignored': True, 'reason': 'Invalid data'}), 200

        payload = data.get('payload')
        if not isinstance(payload, dict):
            logger.info('Ignoring event without payload')
            return jsonify({'ignored': True, 'reason': 'Missing payload'}), 200

        # Filtra apenas mensagens de chat
        # O tipo da mensagem pode estar em payload.type ou payload._data.type
        message_type = payload.get('type') or (
            payload.get('_data') or {}).get('type')
        if message_type != 'chat':
            logger.info(f'Ignoring non-chat message: type={message_type}')
            return jsonify({
                'ignored': True,
                'reason': f'Non-chat message ({message_type})'
            }), 200

        chat_id = payload.get('from')
        message = payload.get('body')

        # Ignora eventos sem texto (status, mídia, etc.)
        if not chat_id or message is None:
            logger.info(
                f'Ignoring event: chat_id={chat_id}, message={message}')
            return jsonify({
                'ignored': True,
                'reason': 'Missing chat_id or message'
            }), 200

        message = str(message).strip()
        if not message:
            logger.info('Ignoring empty message')
            return jsonify({
                'ignored': True,
                'reason': 'Empty message'
            }), 200

        logger.info(f'Processing message from {chat_id}: "{message[:50]}..."')

        # Inicia "digitando"
        try:
            type_result = whatsapp_service.start_typing(chat_id=chat_id)
            if not type_result:
                logger.warning(
                    f'Failed to start typing indicator for {chat_id}')
        except Exception as e:
            logger.warning(f'Failed to start typing: {e}')

        logger.info(f'Invoking AI bot...')
        response = ai_bot.invoke(question=message)

        if not response:
            logger.error(
                f'❌ AI Bot returned empty/None response for: "{message[:50]}..."')
            return jsonify({
                'ignored': True,
                'reason': 'Empty AI response'
            }), 200

        logger.info(f'✓ AI response generated: "{response[:100]}..."')

        # Envia resposta
        logger.info(f'Sending message to {chat_id}...')
        send_result = whatsapp_service.send_message(
            chat_id=chat_id, message=response)

        if not send_result:
            logger.error(
                f'❌ Failed to send message to {chat_id}. Check WAHA connection and logs.')
            return jsonify({
                'ignored': True,
                'reason': 'Failed to send message'
            }), 200

        logger.info(f'✓ Message sent successfully to {chat_id}')

        # Para "digitando"
        try:
            whatsapp_service.stop_typing(chat_id=chat_id)
        except Exception as e:
            logger.warning(f'Failed to stop typing: {e}')

        return jsonify({
            'status': 'success',
            'chat_id': chat_id
        }), 200

    except Exception as e:
        logger.error(f'Webhook error: {e}', exc_info=True)
        # Mesmo em erro inesperado, retorne 200 para evitar retry do WAHA
        return jsonify({
            'ignored': True,
            'reason': 'Internal error'
        }), 200


@app.route('/test', methods=['POST'])
@log_request
def test() -> Tuple[Dict[str, Any], int]:
    """Test endpoint for testing the bot without WhatsApp."""
    try:
        data = request.json
        message = data.get('message', '').strip() if data else ''

        if not message:
            return jsonify({
                'error': 'Message field is required',
                'status': 'error'
            }), 400

        logger.info(f'Test request: "{message[:50]}..."')
        response = ai_bot.invoke(question=message)

        if not response:
            return jsonify({
                'error': 'Failed to generate response',
                'status': 'error'
            }), 500

        return jsonify({
            'input': message,
            'response': response,
            'status': 'success'
        }), 200

    except Exception as e:
        logger.error(f'Test endpoint error: {e}', exc_info=True)
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@app.errorhandler(404)
def not_found(error) -> Tuple[Dict[str, str], int]:
    """Handle 404 errors."""
    return jsonify({
        'error': 'Endpoint not found',
        'status': 'error'
    }), 404


@app.errorhandler(500)
def internal_error(error) -> Tuple[Dict[str, str], int]:
    """Handle 500 errors."""
    logger.error(f'Internal server error: {error}', exc_info=True)
    return jsonify({
        'error': 'Internal server error',
        'status': 'error'
    }), 500


if __name__ == '__main__':
    logger.info('Starting WhatsApp Bot API...')
    app.run(host='0.0.0.0', port=5000, debug=True)
# http://api:5000/wpp-bot-api
