# src/scheduler.py

import logging
import threading
import time
from typing import List

import schedule

from src.models.edi_partner import EdiPartner
from src.services.transfer_service import process_provider_transfer

logger = logging.getLogger(__name__)

# Este evento será usado para sinalizar à thread para parar de forma graciosa.
stop_event = threading.Event()


def run_provider_job(provider: EdiPartner):
    """
    Função 'wrapper' que será chamada pelo agendador.
    Ela executa a transferência para um único fornecedor.
    """
    provider_id = provider.provider_id
    logger.info(f'[Scheduler] A iniciar tarefa agendada para o fornecedor {provider_id}...')
    try:
        process_provider_transfer(provider)
        logger.info(f'[Scheduler] Tarefa agendada para o fornecedor {provider_id} concluída.')
    except Exception:
        # Captura qualquer exceção não tratada para que não quebre o agendador.
        logger.critical(
            f'[Scheduler] A tarefa agendada para o fornecedor {provider_id} falhou catastroficamente.', exc_info=True
        )


def setup_schedules(providers: List[EdiPartner]):
    """
    Configura todas as tarefas no 'schedule' com base na lista de fornecedores.
    """
    logger.info('A configurar os agendamentos dos fornecedores...')

    if not providers:
        logger.warning('Nenhum fornecedor para agendar.')
        return

    for provider in providers:
        interval = provider.process_frequency

        # Agendamos apenas se o intervalo for um número positivo.
        if interval and interval > 0:
            logger.info(f'Fornecedor {provider.provider_id}: agendado para executar a cada {interval} minuto(s).')
            # Agendamos a tarefa e passamos o objeto 'provider' como argumento.
            schedule.every(interval).minutes.do(run_provider_job, provider=provider)
        else:
            logger.info(f'Fornecedor {provider.provider_id}: sem agendamento (intervalo: {interval}).')


def run_scheduler():
    """
    O loop principal do agendador, que corre continuamente numa thread.
    Ele verifica e executa tarefas pendentes a cada segundo.
    """
    logger.info('Thread do agendador iniciada. A aguardar por tarefas...')
    while not stop_event.is_set():
        schedule.run_pending()
        time.sleep(1)

    logger.info('Thread do agendador recebeu sinal de paragem e está a terminar.')
