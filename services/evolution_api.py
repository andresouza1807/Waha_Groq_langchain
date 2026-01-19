"""Evolution API client for WhatsApp integration."""

import logging
import os
from typing import Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from decouple import config

logger = logging.getLogger(__name__)


class EvolutionAPI:
    """Evolution API client for WhatsApp messaging.

    Attributes:
        api_url: Base URL for Evolution API
        api_key: API key for authentication
        timeout: Request timeout in seconds
        retries: Number of retry attempts for failed requests
    """

    def __init__(self, api_url: str | None = None,
                 api_key: str | None = None,
                 timeout: int = 10,
                 retries: int = 3):
        """Initialize Evolution API client.

        Args:
            api_url: The base URL for Evolution API
            api_key: The API key for authentication
            timeout: Request timeout in seconds
            retries: Number of retry attempts
        """
        self.__api_url = api_url or os.getenv(
            'EVOLUTION_API_URL', 'http://localhost:3333')
        self.__api_key = api_key or os.getenv('EVOLUTION_API_KEY', '')
        self.__timeout = timeout
        self.__retries = retries
        self.__instance_name = os.getenv('EVOLUTION_INSTANCE_NAME', 'default')

        # Setup headers with API key
        self.__headers = {
            'Content-Type': 'application/json',
        }

        if self.__api_key:
            self.__headers['apikey'] = self.__api_key
            logger.info(f'Evolution API initialized with API key')
        else:
            logger.warning('Evolution API key not configured')

        self.__session_obj = self._create_session()
        logger.info(
            f'Evolution API client initialized: {self.__api_url} (instance: {self.__instance_name})')

        # Test connection to Evolution API
        try:
            status = self.get_status()
            if status:
                logger.info('✓ Evolution API connection successful')
            else:
                logger.error(
                    f'❌ Evolution API at {self.__api_url} did not respond')
        except Exception as e:
            logger.error(
                f'❌ Failed to connect to Evolution API at {self.__api_url}: {e}')

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

    def send_message(self, chat_id: str, message: str) -> Optional[dict]:
        """Send a text message via WhatsApp.

        Args:
            chat_id: The recipient's WhatsApp number with @c.us or @g.us
            message: The message text to send

        Returns:
            The response JSON or None if an error occurs
        """
        if not chat_id or not message:
            logger.error(
                f'❌ Invalid parameters: chat_id={chat_id}, message={message}')
            return None

        url = f'{self.__api_url}/message/sendText/{self.__instance_name}'
        payload = {
            'number': chat_id.replace('@c.us', '').replace('@g.us', ''),
            'text': message,
        }

        try:
            logger.debug(f'Sending message to {chat_id}: "{message[:50]}..."')
            response = self.__session_obj.post(
                url=url,
                json=payload,
                headers=self.__headers,
                timeout=self.__timeout
            )
            response.raise_for_status()
            logger.info(f'✓ Message sent successfully to {chat_id}')
            return response.json()
        except requests.exceptions.Timeout:
            logger.error(f'❌ Timeout sending message to {chat_id}')
            return None
        except requests.exceptions.ConnectionError:
            logger.error(
                f'❌ Connection error sending message to {chat_id}. Evolution API not reachable at {self.__api_url}')
            return None
        except requests.RequestException as e:
            logger.error(f'❌ Error sending message to {chat_id}: {e}')
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f'   Response status: {e.response.status_code}')
                logger.error(f'   Response body: {e.response.text}')
            return None

    def start_typing(self, chat_id: str) -> Optional[dict]:
        """Start typing indicator in a chat.

        Args:
            chat_id: The chat ID where typing should start

        Returns:
            The response JSON or None if an error occurs
        """
        if not chat_id:
            logger.warning('Invalid chat_id for start_typing')
            return None

        url = f'{self.__api_url}/chat/toggleChatPresence/{self.__instance_name}'
        payload = {
            'number': chat_id.replace('@c.us', '').replace('@g.us', ''),
            'presence': 'typing',
        }

        try:
            response = self.__session_obj.post(
                url=url,
                json=payload,
                headers=self.__headers,
                timeout=self.__timeout
            )
            response.raise_for_status()
            logger.debug(f'✓ Typing started for {chat_id}')
            return response.json()
        except requests.RequestException as e:
            logger.debug(f'Warning: Could not start typing for {chat_id}: {e}')
            return None

    def stop_typing(self, chat_id: str) -> Optional[dict]:
        """Stop typing indicator in a chat.

        Args:
            chat_id: The chat ID where typing should stop

        Returns:
            The response JSON or None if an error occurs
        """
        if not chat_id:
            logger.warning('Invalid chat_id for stop_typing')
            return None

        url = f'{self.__api_url}/chat/toggleChatPresence/{self.__instance_name}'
        payload = {
            'number': chat_id.replace('@c.us', '').replace('@g.us', ''),
            'presence': 'paused',
        }

        try:
            response = self.__session_obj.post(
                url=url,
                json=payload,
                headers=self.__headers,
                timeout=self.__timeout
            )
            response.raise_for_status()
            logger.debug(f'✓ Typing stopped for {chat_id}')
            return response.json()
        except requests.RequestException as e:
            logger.debug(f'Warning: Could not stop typing for {chat_id}: {e}')
            return None

    def get_status(self) -> bool:
        """Get Evolution API status.

        Returns:
            True if API is healthy, False otherwise
        """
        try:
            url = f'{self.__api_url}/instance/fetchInstances'
            response = self.__session_obj.get(
                url=url,
                headers=self.__headers,
                timeout=self.__timeout
            )

            if response.status_code == 200:
                logger.debug('✓ Evolution API is healthy')
                return True
            else:
                logger.warning(
                    f'Evolution API returned {response.status_code}')
                return False
        except requests.exceptions.Timeout:
            logger.warning(
                f'Timeout connecting to Evolution API at {self.__api_url}')
            return False
        except requests.exceptions.ConnectionError:
            logger.warning(
                f'Cannot connect to Evolution API at {self.__api_url}')
            return False
        except Exception as e:
            logger.warning(f'Error checking Evolution API status: {e}')
            return False
