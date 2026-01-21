#!/usr/bin/env python3
"""
Sistema de Lembretes Automáticos via WhatsApp
Envia mensagens programadas usando Evolution API
"""
import json
import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict
import schedule
from services.evolution_api import EvolutionAPI

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GerenciadorLembretes:
    def __init__(self, arquivo_lembretes: str = 'lembretes.json'):
        self.arquivo = arquivo_lembretes
        self.whatsapp = EvolutionAPI()
        self.lembretes_enviados = set()
        logger.info('Gerenciador de Lembretes iniciado')

    def carregar_lembretes(self) -> List[Dict]:
        """Carrega lembretes do arquivo JSON"""
        try:
            with open(self.arquivo, 'r', encoding='utf-8') as f:
                lembretes = json.load(f)
                logger.info(f'✓ {len(lembretes)} lembretes carregados')
                return lembretes
        except FileNotFoundError:
            logger.error(f'Arquivo {self.arquivo} não encontrado')
            return []
        except json.JSONDecodeError as e:
            logger.error(f'Erro ao ler JSON: {e}')
            return []

    def verificar_e_enviar_lembretes(self):
        """Verifica e envia lembretes pendentes"""
        agora = datetime.now()
        data_hora_atual = agora.strftime('%Y-%m-%d %H:%M')

        lembretes = self.carregar_lembretes()

        for lembrete in lembretes:
            if not lembrete.get('ativo', True):
                continue

            # Monta identificador único para este lembrete + data/hora
            id_envio = f"{lembrete['id']}_{data_hora_atual}"

            # Verifica se já foi enviado neste minuto
            if id_envio in self.lembretes_enviados:
                continue

            # Verifica se é hora de enviar
            data_lembrete = lembrete.get('data')
            hora_lembrete = lembrete.get('hora')

            if not data_lembrete or not hora_lembrete:
                continue

            data_hora_lembrete = f"{data_lembrete} {hora_lembrete}"

            # Verifica se chegou a hora
            if data_hora_lembrete == data_hora_atual:
                self.enviar_lembrete(lembrete)
                self.lembretes_enviados.add(id_envio)

                # Se for recorrente, agenda próximo
                if lembrete.get('recorrente'):
                    self.agendar_proximo(lembrete)

    def enviar_lembrete(self, lembrete: Dict):
        """Envia um lembrete via WhatsApp"""
        try:
            numero = lembrete['numero']
            mensagem = lembrete['mensagem']

            # Formata número para padrão WhatsApp
            chat_id = f"{numero}@s.whatsapp.net"

            logger.info(f'Enviando lembrete para {numero}...')

            # Envia mensagem
            resultado = self.whatsapp.send_message(chat_id, mensagem)

            if resultado:
                logger.info(f'✓ Lembrete enviado com sucesso para {numero}')
                logger.info(f'  Mensagem: {mensagem[:50]}...')
            else:
                logger.error(f'✗ Falha ao enviar lembrete para {numero}')

        except Exception as e:
            logger.error(f'Erro ao enviar lembrete: {e}')

    def agendar_proximo(self, lembrete: Dict):
        """Agenda próximo envio para lembretes recorrentes"""
        recorrencia = lembrete.get('recorrente')
        data_atual = datetime.strptime(lembrete['data'], '%Y-%m-%d')

        if recorrencia == 'diario':
            proxima_data = data_atual + timedelta(days=1)
        elif recorrencia == 'semanal':
            proxima_data = data_atual + timedelta(weeks=1)
        elif recorrencia == 'mensal':
            # Aproximação: adiciona 30 dias
            proxima_data = data_atual + timedelta(days=30)
        else:
            return

        # Atualiza data no arquivo
        lembretes = self.carregar_lembretes()
        for l in lembretes:
            if l['id'] == lembrete['id']:
                l['data'] = proxima_data.strftime('%Y-%m-%d')
                break

        with open(self.arquivo, 'w', encoding='utf-8') as f:
            json.dump(lembretes, f, indent=2, ensure_ascii=False)

        logger.info(
            f'✓ Próximo lembrete ID {lembrete["id"]} agendado para {proxima_data.strftime("%Y-%m-%d")}')

    def listar_proximos_lembretes(self, quantidade: int = 5):
        """Lista próximos lembretes a serem enviados"""
        lembretes = self.carregar_lembretes()
        agora = datetime.now()

        proximos = []
        for lembrete in lembretes:
            if not lembrete.get('ativo'):
                continue

            try:
                data_hora = datetime.strptime(
                    f"{lembrete['data']} {lembrete['hora']}",
                    '%Y-%m-%d %H:%M'
                )

                if data_hora >= agora:
                    diferenca = data_hora - agora
                    lembrete['_tempo_restante'] = str(diferenca).split('.')[0]
                    proximos.append(lembrete)
            except:
                continue

        # Ordena por data/hora
        proximos.sort(key=lambda x: f"{x['data']} {x['hora']}")

        return proximos[:quantidade]

    def iniciar_monitoramento(self):
        """Inicia o loop de monitoramento"""
        logger.info('='*60)
        logger.info('Sistema de Lembretes Automáticos')
        logger.info('='*60)
        logger.info(f'Arquivo de lembretes: {self.arquivo}')
        logger.info('Monitoramento iniciado (Ctrl+C para parar)')
        logger.info('='*60)

        # Lista próximos lembretes
        proximos = self.listar_proximos_lembretes()
        if proximos:
            logger.info('\nPróximos lembretes:')
            for l in proximos:
                logger.info(
                    f"  [{l['data']} {l['hora']}] -> {l['numero']}: {l['mensagem'][:40]}...")
                logger.info(f"    ⏱️  Falta: {l['_tempo_restante']}")
        else:
            logger.info('\nNenhum lembrete ativo agendado')

        logger.info('\n' + '='*60 + '\n')

        # Agenda verificação a cada minuto
        schedule.every(1).minutes.do(self.verificar_e_enviar_lembretes)

        # Loop principal
        try:
            while True:
                schedule.run_pending()
                time.sleep(30)  # Verifica a cada 30 segundos
        except KeyboardInterrupt:
            logger.info('\n\n✓ Sistema de lembretes finalizado')


def main():
    gerenciador = GerenciadorLembretes()
    gerenciador.iniciar_monitoramento()


if __name__ == '__main__':
    main()
