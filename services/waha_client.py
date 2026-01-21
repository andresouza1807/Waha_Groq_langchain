"""WAHA client for WhatsApp integration."""

import logging
import os
from typing import Optional, Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class WAHAClient:
    """WAHA client for WhatsApp messaging.

    Uses WAHA API to send messages, manage typing indicators, etc.
    """

    def __init__(self, api_url: str | None = None,
                 api_key: str | None = None,
                 session_name: str = 'default',
                 timeout: int = 10,
                 retries: int = 3):
        """Initialize WAHA client.

        Args:
            api_url: The base URL for WAHA API
            api_key: The API key for authentication
            session_name: WAHA session name
            timeout: Request timeout in seconds
            retries: Number of retry attempts
        """
        self.__api_url = api_url or os.getenv(
            'WAHA_API_URL', 'http://localhost:3000')
        self.__api_key = api_key or os.getenv('WHATSAPP_API_KEY', '')
        self.__session_name = session_name
        self.__timeout = timeout
        self.__retries = retries

        # Setup headers with API key
        self.__headers = {
            'Content-Type': 'application/json',
            'X-Api-Key': self.__api_key
        }

        self.__session_obj = self._create_session()
        logger.info(
            f'WAHA client initialized: {self.__api_url} (session: {self.__session_name})')

        # Test connection to WAHA
        try:
            status = self.get_status()
            if status:
                logger.info('✓ WAHA connection successful')
            else:
                logger.error(f'❌ WAHA at {self.__api_url} did not respond')
        except Exception as e:
            logger.error(
                f'❌ Failed to connect to WAHA at {self.__api_url}: {e}')

    def _create_session(self) -> requests.Session:
        """Create a requests session with retry strategy.

        Returns:
            Configured requests.Session object
        """
        session = requests.Session()
        retry_strategy = Retry(
            total=self.__retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=['POST', 'GET'],
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def send_message(self, chat_id: str, message: str) -> bool:
        """Send a text message to a chat.

        Args:
            chat_id: The chat ID (phone number with @c.us or just number)
            message: The message text to send

        Returns:
            True if successful, False otherwise
        """
        try:
            # Remove @c.us suffix if present
            clean_chat_id = chat_id.replace('@c.us', '')

            url = f'{self.__api_url}/api/{self.__session_name}/chats/{clean_chat_id}@c.us/messages/text'
            payload = {
                'text': message
            }

            response = self.__session_obj.post(
                url,
                json=payload,
                headers=self.__headers,
                timeout=self.__timeout
            )

            if response.status_code in [200, 201]:
                logger.info(f'✓ Message sent to {chat_id}')
                return True
            else:
                logger.error(
                    f'❌ Failed to send message: {response.status_code} - {response.text[:200]}')
                return False

        except requests.exceptions.RequestException as e:
            logger.error(
                f'❌ Connection error sending message to {chat_id}: {e}')
            return False
        except Exception as e:
            logger.error(f'❌ Error sending message to {chat_id}: {e}')
            return False

    def start_typing(self, chat_id: str) -> bool:
        """Show typing indicator.

        Args:
            chat_id: The chat ID

        Returns:
            True if successful, False otherwise
        """
        try:
            url = f'{self.__api_url}/api/{self.__session_name}/chats/{chat_id}/typing'

            response = self.__session_obj.post(
                url,
                json={},
                headers=self.__headers,
                timeout=self.__timeout
            )

            if response.status_code in [200, 201]:
                return True
            else:
                logger.warning(
                    f'Failed to start typing: {response.status_code}')
                return False

        except Exception as e:
            logger.warning(f'Error starting typing: {e}')
            return False

    def stop_typing(self, chat_id: str) -> bool:
        """Hide typing indicator.

        Args:
            chat_id: The chat ID

        Returns:
            True if successful, False otherwise
        """
        try:
            url = f'{self.__api_url}/api/{self.__session_name}/chats/{chat_id}/typing'

            response = self.__session_obj.delete(
                url,
                headers=self.__headers,
                timeout=self.__timeout
            )

            if response.status_code in [200, 201, 204]:
                return True
            else:
                logger.warning(
                    f'Failed to stop typing: {response.status_code}')
                return False

        except Exception as e:
            logger.warning(f'Error stopping typing: {e}')
            return False

    def get_status(self) -> Dict[str, Any] | None:
        """Get session status.

        Returns:
            Session info dict or None if failed
        """
        try:
            url = f'{self.__api_url}/api/sessions/{self.__session_name}'

            response = self.__session_obj.get(
                url,
                headers=self.__headers,
                timeout=self.__timeout
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f'Failed to get status: {response.status_code}')
                return None

        except Exception as e:
            logger.error(f'Error getting status: {e}')
            return None
