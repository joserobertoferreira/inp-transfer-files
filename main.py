import logging
import threading
import time
from typing import Optional

from src.config.logging import setup_logging
from src.database.database import db
from src.repositories.publication_repository import PublicationRepository
from src.scheduler.scheduler import run_scheduler, setup_schedules, stop_event
from src.services.provider_service import get_active_providers
from src.services.transfer_service import process_provider_transfer


def run_debug_mode(provider_id: Optional[str] = None):
    """
    Executa o ciclo de transferência uma vez e sai.
    Se provider_id for fornecido, executa apenas para esse fornecedor.
    """
    if provider_id:
        logger.info(f'Processar fornecedor: {provider_id}')
    else:
        logger.info('Processar todos os fornecedores ativos')

    providers = get_active_providers()

    if provider_id:
        providers = [p for p in providers if str(p.provider_id) == provider_id]
        if not providers:
            logger.error(f"Fornecedor '{provider_id}' não foi encontrado ou está inativo.")
            return

    if not providers:
        logger.warning('Nenhum fornecedor ativo encontrado para processar.')
        return

    for provider in providers:
        process_provider_transfer(provider)

    logger.info('Ciclo de execução única concluído.')


def start_scheduler_service():
    """
    Inicia o serviço de agendamento.
    """

    # Passo 1: Buscar os fornecedores do banco de dados
    providers = get_active_providers()

    if not providers:
        logger.info('Nenhuma tarefa a ser executada. Encerrando.')
        return

    # Passo 2: Configurar os agendamentos dos fornecedores
    setup_schedules(providers)

    # Passo 3: Criar e iniciar a thread que vai executar as tarefas agendadas
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.start()

    logger.info('Thread principal a aguardar. O agendador está a correr em segundo plano.')
    logger.info('Pressione Ctrl+C para parar o serviço.')

    # 4. Manter o programa principal a correr.
    #    No futuro, é AQUI que você iniciaria o seu servidor de API (Flask/FastAPI).
    try:
        # O programa principal vai ficar aqui à espera até ser interrompido.
        while True:
            time.sleep(3600)  # Dorme por longos períodos, apenas para manter o processo vivo.
    except KeyboardInterrupt:
        logger.info('Recebido sinal de interrupção (Ctrl+C). Iniciar paragem graciosa...')
    finally:
        # 5. Lógica de paragem graciosa
        logger.info('Sinalizar à thread do agendador para parar...')
        stop_event.set()

        # Espera que a thread do agendador termine o seu ciclo atual.
        scheduler_thread.join(timeout=5)  # Espera no máximo 5 segundos


def main():
    """
    Ponto de entrada principal da aplicação.
    """
    # if settings.DEBUG:
    #     run_debug_mode()
    # else:
    #     start_scheduler_service()

    try:
        # Usamos o context manager para obter uma sessão segura
        with db.get_db() as session:
            repo = PublicationRepository(session)

            publication = repo.find_publication_code(
                bipad='0184', provider_id='1526', description='AUJOURD HUI  DIMANCHE'
            )

            print(publication)

    except Exception:
        logger.critical('Falha crítica ao buscar fornecedores no banco de dados via ORM.', exc_info=True)


if __name__ == '__main__':
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info('Iniciando o backend de transferência de ficheiros...')
    main()
