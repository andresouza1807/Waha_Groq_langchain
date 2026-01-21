"""Reminder management and scheduling."""

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict, field
from pathlib import Path
import schedule
import time
from threading import Thread

logger = logging.getLogger(__name__)

REMINDERS_FILE = os.getenv('REMINDERS_DB', 'lembretes.json')


@dataclass
class Reminder:
    """Classe para representar um lembrete."""
    id: int
    numero: str
    mensagem: str
    data: str
    hora: str
    recorrente: str  # False, 'diario', 'semanal', 'mensal'
    ativo: bool = True
    criado_em: str = field(default_factory=lambda: datetime.now().isoformat())
    ultimo_envio: Optional[str] = None
    notas: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Reminder':
        """Criar a partir de dicionário."""
        return cls(**data)


class ReminderStore:
    """Gerenciador de armazenamento de lembretes."""

    def __init__(self, db_file: str = REMINDERS_FILE):
        """Inicializar store."""
        self.db_file = db_file
        self._ensure_db()

    def _ensure_db(self) -> None:
        """Garantir que o arquivo de banco existe."""
        if not os.path.exists(self.db_file):
            self._save_reminders([])
            logger.info(f'Reminders database criado: {self.db_file}')

    def _load_reminders(self) -> List[Dict[str, Any]]:
        """Carregar lembretes do arquivo."""
        try:
            if not os.path.exists(self.db_file):
                return []
            with open(self.db_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception as e:
            logger.error(f'Erro ao carregar lembretes: {e}')
            return []

    def _save_reminders(self, reminders: List[Dict[str, Any]]) -> None:
        """Salvar lembretes no arquivo."""
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(reminders, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f'Erro ao salvar lembretes: {e}')

    def _get_next_id(self) -> int:
        """Obter próximo ID."""
        reminders = self._load_reminders()
        if not reminders:
            return 1
        return max(r.get('id', 0) for r in reminders) + 1

    def add_reminder(self, numero: str, mensagem: str, data: str,
                     hora: str, recorrente: str = False, notas: str = "") -> Reminder:
        """Adicionar novo lembrete."""
        reminders = self._load_reminders()

        reminder = Reminder(
            id=self._get_next_id(),
            numero=numero,
            mensagem=mensagem,
            data=data,
            hora=hora,
            recorrente=recorrente,
            ativo=True,
            notas=notas
        )

        reminders.append(reminder.to_dict())
        self._save_reminders(reminders)

        logger.info(f'Lembrete criado: ID {reminder.id}')
        return reminder

    def get_reminders(self, limit: int = 100, offset: int = 0,
                      only_active: bool = True) -> List[Reminder]:
        """Obter lembretes com paginação."""
        reminders = self._load_reminders()

        if only_active:
            reminders = [r for r in reminders if r.get('ativo', True)]

        # Ordenar por data/hora
        reminders.sort(
            key=lambda r: f"{r.get('data', '')} {r.get('hora', '')}")

        paginated = reminders[offset:offset + limit]
        return [Reminder.from_dict(r) for r in paginated]

    def get_reminder(self, reminder_id: int) -> Optional[Reminder]:
        """Obter um lembrete específico."""
        reminders = self._load_reminders()

        for r in reminders:
            if r['id'] == reminder_id:
                return Reminder.from_dict(r)

        return None

    def update_reminder(self, reminder_id: int, **kwargs) -> bool:
        """Atualizar lembrete."""
        reminders = self._load_reminders()

        for r in reminders:
            if r['id'] == reminder_id:
                r.update(kwargs)
                self._save_reminders(reminders)
                logger.info(f'Lembrete atualizado: ID {reminder_id}')
                return True

        return False

    def delete_reminder(self, reminder_id: int) -> bool:
        """Deletar lembrete."""
        reminders = self._load_reminders()
        original_len = len(reminders)

        reminders = [r for r in reminders if r['id'] != reminder_id]

        if len(reminders) < original_len:
            self._save_reminders(reminders)
            logger.info(f'Lembrete deletado: ID {reminder_id}')
            return True

        return False

    def get_pending_reminders(self) -> List[Reminder]:
        """Obter lembretes pendentes para enviar."""
        reminders = self._load_reminders()
        pending = []
        now = datetime.now()

        for r in reminders:
            if not r.get('ativo', True):
                continue

            try:
                reminder_datetime = datetime.strptime(
                    f"{r['data']} {r['hora']}", "%Y-%m-%d %H:%M"
                )

                if reminder_datetime <= now:
                    # Verificar se já foi enviado hoje
                    if r.get('ultimo_envio'):
                        ultimo = datetime.fromisoformat(r['ultimo_envio'])
                        if ultimo.date() == now.date():
                            continue

                    pending.append(Reminder.from_dict(r))
            except Exception as e:
                logger.warning(
                    f"Erro ao processar lembrete {r.get('id')}: {e}")

        return pending

    def mark_sent(self, reminder_id: int) -> bool:
        """Marcar lembrete como enviado."""
        return self.update_reminder(
            reminder_id,
            ultimo_envio=datetime.now().isoformat()
        )

    def get_stats(self) -> Dict[str, int]:
        """Obter estatísticas."""
        reminders = self._load_reminders()
        total = len(reminders)
        active = sum(1 for r in reminders if r.get('ativo', True))

        return {
            'total': total,
            'active': active,
            'inactive': total - active
        }
