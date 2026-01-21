"""WhatsApp Bot API using WAHA and Groq LLM."""

import logging
import json
import os
from typing import Tuple, Dict, Any
from datetime import datetime
from bot.ai_bot import AIBot
from services.waha_client import WAHAClient
from models.message_store import MessageStore
from models.reminder_store import ReminderStore
from models.reminder_scheduler import ReminderScheduler
from flask import Flask, request, jsonify, render_template
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

app = Flask(__name__, template_folder='templates')

# Initialize services
whatsapp_service = WAHAClient()
ai_bot = AIBot()
message_store = MessageStore()
reminder_store = ReminderStore()
reminder_scheduler = ReminderScheduler(reminder_store, whatsapp_service)

logger.info('✓ WhatsApp Bot initialized with WAHA')
logger.info('✓ Message store initialized')
logger.info('✓ Reminder store initialized')

# Start reminder scheduler
reminder_scheduler.start()


@app.teardown_appcontext
def shutdown_reminder_scheduler(error=None):
    """Parar scheduler ao desligar."""
    reminder_scheduler.stop()


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

        # Always return 200 to webhook even for ignored events
        # Filter only chat messages
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

        # Salvar mensagem no banco
        sender_name = payload.get('pushName', 'Unknown')
        try:
            message_store.add_message(
                sender_id=chat_id,
                sender_name=sender_name,
                message=message
            )
            logger.info(f'✓ Message saved to store')
        except Exception as e:
            logger.warning(f'Failed to save message to store: {e}')

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


# Panel routes
@app.route('/', methods=['GET'])
def dashboard() -> str:
    """Render dashboard panel."""
    return render_template('dashboard.html')


@app.route('/messages', methods=['GET'])
def messages_panel() -> str:
    """Render message panel (legacy)."""
    return render_template('panel.html')


@app.route('/api/messages', methods=['GET'])
@log_request
def get_messages() -> Tuple[Dict[str, Any], int]:
    """Get messages with optional filtering."""
    try:
        status = request.args.get('status', '')
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))

        if status == 'pending':
            messages = message_store.get_pending_messages(limit)
        else:
            messages = message_store.get_messages(limit, offset)

        return jsonify({
            'messages': [m.to_dict() for m in messages],
            'total': message_store.get_total_count(),
            'status': 'success'
        }), 200

    except Exception as e:
        logger.error(f'Error getting messages: {e}')
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@app.route('/api/stats', methods=['GET'])
@log_request
def get_stats() -> Tuple[Dict[str, Any], int]:
    """Get message statistics."""
    try:
        stats = message_store.get_stats()
        return jsonify(stats), 200

    except Exception as e:
        logger.error(f'Error getting stats: {e}')
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@app.route('/api/messages/<msg_id>/response', methods=['POST'])
@log_request
def save_response(msg_id: str) -> Tuple[Dict[str, Any], int]:
    """Save response for a message."""
    try:
        data = request.json
        response = data.get('response', '')
        notes = data.get('notes', '')

        # Salvar resposta
        success = message_store.add_response(msg_id, response)

        if not success:
            return jsonify({
                'error': 'Message not found',
                'status': 'error'
            }), 404

        # Atualizar notas
        msg = message_store.get_message(msg_id)
        if msg:
            msg.notes = notes

        return jsonify({
            'message': 'Response saved successfully',
            'status': 'success'
        }), 200

    except Exception as e:
        logger.error(f'Error saving response: {e}')
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


# Reminder routes
@app.route('/api/reminders', methods=['GET'])
@log_request
def get_reminders() -> Tuple[Dict[str, Any], int]:
    """Get reminders."""
    try:
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))

        reminders = reminder_store.get_reminders(limit, offset)

        return jsonify({
            'reminders': [r.to_dict() for r in reminders],
            'total': reminder_store.get_stats()['total'],
            'status': 'success'
        }), 200

    except Exception as e:
        logger.error(f'Error getting reminders: {e}')
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@app.route('/api/reminders', methods=['POST'])
@log_request
def create_reminder() -> Tuple[Dict[str, Any], int]:
    """Create new reminder."""
    try:
        data = request.json

        reminder = reminder_store.add_reminder(
            numero=data.get('numero', ''),
            mensagem=data.get('mensagem', ''),
            data=data.get('data', ''),
            hora=data.get('hora', ''),
            recorrente=data.get('recorrente', False),
            notas=data.get('notas', '')
        )

        return jsonify({
            'reminder': reminder.to_dict(),
            'message': 'Reminder created successfully',
            'status': 'success'
        }), 201

    except Exception as e:
        logger.error(f'Error creating reminder: {e}')
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@app.route('/api/reminders/<int:reminder_id>', methods=['PUT'])
@log_request
def update_reminder(reminder_id: int) -> Tuple[Dict[str, Any], int]:
    """Update reminder."""
    try:
        data = request.json

        success = reminder_store.update_reminder(
            reminder_id,
            **{k: v for k, v in data.items() if k in [
                'numero', 'mensagem', 'data', 'hora', 'recorrente', 'ativo', 'notas'
            ]}
        )

        if not success:
            return jsonify({
                'error': 'Reminder not found',
                'status': 'error'
            }), 404

        reminder = reminder_store.get_reminder(reminder_id)

        return jsonify({
            'reminder': reminder.to_dict(),
            'message': 'Reminder updated successfully',
            'status': 'success'
        }), 200

    except Exception as e:
        logger.error(f'Error updating reminder: {e}')
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@app.route('/api/reminders/<int:reminder_id>', methods=['DELETE'])
@log_request
def delete_reminder(reminder_id: int) -> Tuple[Dict[str, str], int]:
    """Delete reminder."""
    try:
        success = reminder_store.delete_reminder(reminder_id)

        if not success:
            return jsonify({
                'error': 'Reminder not found',
                'status': 'error'
            }), 404

        return jsonify({
            'message': 'Reminder deleted successfully',
            'status': 'success'
        }), 200

    except Exception as e:
        logger.error(f'Error deleting reminder: {e}')
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@app.route('/api/reminders/stats', methods=['GET'])
@log_request
def get_reminders_stats() -> Tuple[Dict[str, Any], int]:
    """Get reminders statistics."""
    try:
        stats = reminder_store.get_stats()
        scheduler_running = reminder_scheduler.is_running()

        return jsonify({
            **stats,
            'scheduler_running': scheduler_running,
            'status': 'success'
        }), 200

    except Exception as e:
        logger.error(f'Error getting reminders stats: {e}')
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
