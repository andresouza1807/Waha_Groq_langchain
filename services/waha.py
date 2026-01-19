"""Waha API client for WhatsApp integration."""

import logging
import os
from typing import Optional
import requests
from requests.auth import HTTPBasicAuth
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from decouple import config

logger = logging.getLogger(__name__)


class Waha:
    """Waha API client for WhatsApp messaging.

    Attributes:
        api_url: Base URL for Waha API
        session: WhatsApp session name
        timeout: Request timeout in seconds
        retries: Number of retry attempts for failed requests
    """

    def __init__(self, api_url: str | None = None,
                 session: str | None = None,
                 timeout: int = 10,
                 retries: int = 3):
        """Initialize Waha client.

        Args:
            api_url: The base URL for Waha API
            session: The WhatsApp session name
            timeout: Request timeout in seconds
            retries: Number of retry attempts
        """
        self.__api_url = api_url or os.getenv(
            'WAHA_URL', 'http://wpp_bot_waha:3000')
        self.__session = session or os.getenv('WAHA_SESSION_NAME', 'default')
        self.__timeout = timeout
        self.__retries = retries

        # Load Dashboard credentials for WAHA API authentication
        # WAHA Community version uses Basic Auth with dashboard credentials
        self.__dashboard_username = os.environ.get('WAHA_DASHBOARD_USERNAME') or config(
            'WAHA_DASHBOARD_USERNAME', default='admin')
        self.__dashboard_password = os.environ.get('WAHA_DASHBOARD_PASSWORD') or config(
            'WAHA_DASHBOARD_PASSWORD', default='')

        # Setup headers with Basic Auth
        self.__headers = {
            'Content-Type': 'application/json',
        }

        # Create Basic Auth object for requests
        self.__auth = HTTPBasicAuth(
            self.__dashboard_username,
            self.__dashboard_password
        ) if (self.__dashboard_username and self.__dashboard_password) else None

        if self.__auth:
            logger.info(
                f'WAHA Dashboard authentication configured (user: {self.__dashboard_username})')
        else:
            logger.warning(
                'WAHA Dashboard credentials not configured - API requests may fail with 401')

        self.__session_obj = self._create_session()
        logger.info(
            f'Waha client initialized: {self.__api_url} (session: {self.__session})')

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

    def send_message(self, chat_id: str, message: str) -> Optional[dict]:
        """Send a text message via WhatsApp.

        Args:
            chat_id: The recipient's chat ID
            message: The message to send

        Returns:
            The response JSON or None if an error occurs
        """
        if not chat_id or not message:
            logger.error(
                f'❌ Invalid parameters: chat_id={chat_id}, message={message}')
            return None

        url = f'{self.__api_url}/api/sendText'
        payload = {
            'session': self.__session,
            'chatId': chat_id,
            'text': message,
        }

        try:
            logger.debug(f'Sending message to {chat_id}: "{message[:50]}..."')
            response = self.__session_obj.post(
                url=url,
                json=payload,
                headers=self.__headers,
                auth=self.__auth,
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
                f'❌ Connection error sending message to {chat_id}. WAHA not reachable at {self.__api_url}')
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

        url = f'{self.__api_url}/api/startTyping'
        payload = {
            'session': self.__session,
            'chatId': chat_id,
        }

        try:
            response = self.__session_obj.post(
                url=url,
                json=payload,
                headers=self.__headers,
                auth=self.__auth,
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

        url = f'{self.__api_url}/api/stopTyping'
        payload = {
            'session': self.__session,
            'chatId': chat_id,
        }

        try:
            response = self.__session_obj.post(
                url=url,
                json=payload,
                headers=self.__headers,
                auth=self.__auth,
                timeout=self.__timeout
            )
            response.raise_for_status()
            logger.debug(f'✓ Typing stopped for {chat_id}')
            return response.json()
        except requests.RequestException as e:
            logger.debug(f'Warning: Could not stop typing for {chat_id}: {e}')
            return None

    def get_status(self) -> Optional[dict]:
        """Get Waha API status using the public /ping endpoint.

        Returns:
            Status information or None if unreachable
        """
        url = f'{self.__api_url}/ping'
        try:
            response = self.__session_obj.get(
                url=url,
                headers=self.__headers,
                timeout=self.__timeout
            )
            response.raise_for_status()
            logger.info('✓ Waha API is healthy (/ping responded)')
            return response.json()
        except requests.RequestException as e:
            logger.error(f'Error getting Waha status: {e}')
            return None
