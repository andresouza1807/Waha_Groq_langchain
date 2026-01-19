"""AI Bot module for LangChain and Groq integration."""

import logging
import os
from decouple import config
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

logger = logging.getLogger(__name__)

# Load and validate GROQ_API_KEY
groq_api_key = config('GROQ_API_KEY', default=None)
if not groq_api_key:
    error_msg = 'GROQ_API_KEY not configured in .env file'
    logger.error(error_msg)
    raise ValueError(error_msg)

if not groq_api_key.startswith('gsk_'):
    logger.warning(
        f'GROQ_API_KEY format issue (starts with: {groq_api_key[:10]})')

os.environ['GROQ_API_KEY'] = groq_api_key
logger.info('GROQ_API_KEY loaded successfully')


class AIBot:
    """AI Bot class for handling chat interactions with Groq LLaMA.

    Attributes:
        model: The model name (llama-3.3-70b-versatile)
        temperature: Temperature for response generation (0.7)
        max_tokens: Maximum tokens in response (1024)
    """

    def __init__(self, model: str = 'llama-3.3-70b-versatile',
                 temperature: float = 0.7,
                 max_tokens: int = 1024):
        """Initialize the AI Bot with Groq chat model.

        Args:
            model: The model to use for chat
            temperature: Controls randomness (0.0-1.0)
            max_tokens: Maximum tokens in response
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        try:
            self.__chat = ChatGroq(
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=groq_api_key,
            )
            logger.info(f'AIBot initialized successfully with model: {model}')
            logger.info(
                f'Temperature: {temperature}, Max tokens: {max_tokens}')
        except Exception as e:
            error_msg = f'Failed to initialize ChatGroq: {e}'
            logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg) from e

    def invoke(self, question: str) -> str | None:
        """Generate a response to a user question.

        Args:
            question: The user's question or message

        Returns:
            The AI response string or None if an error occurs
        """
        if not question or not isinstance(question, str):
            logger.warning(f'Invalid question type: {type(question)}')
            return None

        question = question.strip()
        if not question:
            logger.warning('Question is empty after stripping whitespace')
            return None

        prompt = PromptTemplate(
            input_variables=['texto'],
            template="Você é um assistente útil e amigável. Responda de forma breve, clara e educada.\n\nPergunta: {texto}\n\nResposta:",
        )

        try:
            chain = prompt | self.__chat | StrOutputParser()
            logger.info(f'Invoking bot with: "{question[:100]}..."')
            response = chain.invoke({'texto': question})

            if not response:
                logger.warning('Bot returned empty response')
                return None

            response = response.strip()
            logger.info(f'Bot response received: "{response[:100]}..."')
            return response

        except Exception as e:
            logger.error(f'Error invoking bot: {e}', exc_info=True)
            error_msg = 'Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente.'
            if '401' in str(e) or 'Unauthorized' in str(e):
                error_msg = 'Erro de autenticação na API. Verifique a chave do Groq.'
            elif 'timeout' in str(e).lower():
                error_msg = 'A resposta levou muito tempo. Tente uma pergunta mais simples.'
            return error_msg

    def set_model(self, model: str) -> bool:
        """Change the model at runtime.

        Args:
            model: The new model name

        Returns:
            True if successful, False otherwise
        """
        try:
            self.model = model
            self.__chat = ChatGroq(
                model=model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                api_key=groq_api_key,
            )
            logger.info(f'Model changed to: {model}')
            return True
        except Exception as e:
            logger.error(f'Failed to change model: {e}')
            return False
