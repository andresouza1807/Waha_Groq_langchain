"""Message storage and management."""

import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Arquivo de armazenamento
MESSAGES_FILE = os.getenv('MESSAGES_DB', 'messages.json')


@dataclass
class Message:
    """Classe para representar uma mensagem."""
    id: str
    sender_id: str
    sender_name: str
    message: str
    timestamp: str
    response: Optional[str] = None
    response_timestamp: Optional[str] = None
    responded: bool = False
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Criar a partir de dicionário."""
        return cls(**data)


class MessageStore:
    """Gerenciador de armazenamento de mensagens."""

    def __init__(self, db_file: str = MESSAGES_FILE):
        """Inicializar store."""
        self.db_file = db_file
        self._ensure_db()

    def _ensure_db(self) -> None:
        """Garantir que o arquivo de banco existe."""
        if not os.path.exists(self.db_file):
            self._save_messages([])
            logger.info(f'Database criado: {self.db_file}')

    def _load_messages(self) -> List[Dict[str, Any]]:
        """Carregar mensagens do arquivo."""
        try:
            if not os.path.exists(self.db_file):
                return []
            with open(self.db_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception as e:
            logger.error(f'Erro ao carregar mensagens: {e}')
            return []

    def _save_messages(self, messages: List[Dict[str, Any]]) -> None:
        """Salvar mensagens no arquivo."""
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(messages, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f'Erro ao salvar mensagens: {e}')

    def add_message(self, sender_id: str, sender_name: str, message: str) -> Message:
        """Adicionar nova mensagem."""
        messages = self._load_messages()

        # Gerar ID único
        msg_id = f"{sender_id}_{datetime.now().timestamp()}"

        new_msg = Message(
            id=msg_id,
            sender_id=sender_id,
            sender_name=sender_name,
            message=message,
            timestamp=datetime.now().isoformat(),
            response=None,
            response_timestamp=None,
            responded=False,
            notes=""
        )

        messages.append(new_msg.to_dict())
        self._save_messages(messages)

        logger.info(f'Mensagem salva: {msg_id}')
        return new_msg

    def get_messages(self, limit: int = 100, offset: int = 0) -> List[Message]:
        """Obter mensagens com paginação."""
        messages = self._load_messages()
        # Ordenar por timestamp descendente (mais recentes primeiro)
        messages.sort(key=lambda m: m.get('timestamp', ''), reverse=True)

        paginated = messages[offset:offset + limit]
        return [Message.from_dict(m) for m in paginated]

    def get_total_count(self) -> int:
        """Obter total de mensagens."""
        return len(self._load_messages())

    def get_pending_messages(self, limit: int = 50) -> List[Message]:
        """Obter mensagens que ainda não receberam resposta."""
        messages = self._load_messages()
        pending = [m for m in messages if not m.get('responded', False)]
        pending.sort(key=lambda m: m.get('timestamp', ''))
        return [Message.from_dict(m) for m in pending[:limit]]

    def add_response(self, msg_id: str, response: str) -> bool:
        """Adicionar resposta a uma mensagem."""
        messages = self._load_messages()

        for msg in messages:
            if msg['id'] == msg_id:
                msg['response'] = response
                msg['response_timestamp'] = datetime.now().isoformat()
                msg['responded'] = True
                self._save_messages(messages)
                logger.info(f'Resposta adicionada: {msg_id}')
                return True

        logger.warning(f'Mensagem não encontrada: {msg_id}')
        return False

    def get_message(self, msg_id: str) -> Optional[Message]:
        """Obter uma mensagem específica."""
        messages = self._load_messages()

        for msg in messages:
            if msg['id'] == msg_id:
                return Message.from_dict(msg)

        return None

    def get_stats(self) -> Dict[str, int]:
        """Obter estatísticas."""
        messages = self._load_messages()
        total = len(messages)
        responded = sum(1 for m in messages if m.get('responded', False))
        pending = total - responded

        return {
            'total': total,
            'responded': responded,
            'pending': pending
        }
