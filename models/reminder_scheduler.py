"""Background scheduler for reminders."""

import logging
import time
from threading import Thread, Event
from datetime import datetime
import schedule

from models.reminder_store import ReminderStore
from services.waha_client import WAHAClient

logger = logging.getLogger(__name__)


class ReminderScheduler:
    """Scheduler para lembretes automáticos."""

    def __init__(self, reminder_store: ReminderStore, waha_client: WAHAClient = None):
        """Inicializar scheduler."""
        self.reminder_store = reminder_store
        self.waha_client = waha_client
        self.running = False
        self.thread = None
        self.stop_event = Event()

    def start(self) -> None:
        """Iniciar scheduler em thread."""
        if self.running:
            logger.warning('Scheduler já está rodando')
            return

        self.running = True
        self.stop_event.clear()
        self.thread = Thread(target=self._run, daemon=True)
        self.thread.start()
        logger.info('✓ Reminder scheduler iniciado')

    def stop(self) -> None:
        """Parar scheduler."""
        if not self.running:
            return

        self.running = False
        self.stop_event.set()

        if self.thread:
            self.thread.join(timeout=5)

        logger.info('✓ Reminder scheduler parado')

    def _run(self) -> None:
        """Loop principal do scheduler."""
        # Agendar verificação a cada minuto
        schedule.every(1).minutes.do(self._check_reminders)

        logger.info('Scheduler loop iniciado')

        while self.running and not self.stop_event.is_set():
            try:
                schedule.run_pending()
                time.sleep(10)  # Check a cada 10 segundos
            except Exception as e:
                logger.error(f'Erro no scheduler loop: {e}')
                time.sleep(60)

    def _check_reminders(self) -> None:
        """Verificar e enviar lembretes pendentes."""
        try:
            pending = self.reminder_store.get_pending_reminders()

            if not pending:
                return

            logger.info(f'Encontrados {len(pending)} lembretes pendentes')

            for reminder in pending:
                self._send_reminder(reminder)

        except Exception as e:
            logger.error(f'Erro ao verificar lembretes: {e}')

    def _send_reminder(self, reminder) -> None:
        """Enviar um lembrete."""
        try:
            # Tentar enviar via WAHA
            if self.waha_client:
                success = self.waha_client.send_message(
                    chat_id=reminder.numero,
                    message=reminder.mensagem
                )

                if success:
                    self.reminder_store.mark_sent(reminder.id)
                    logger.info(
                        f'✓ Lembrete {reminder.id} enviado para {reminder.numero}')
                    return

            logger.warning(f'Não foi possível enviar lembrete {reminder.id}')

        except Exception as e:
            logger.error(f'Erro ao enviar lembrete {reminder.id}: {e}')

    def is_running(self) -> bool:
        """Verificar se scheduler está rodando."""
        return self.running
