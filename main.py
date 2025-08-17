import logging

from src.config.logging import setup_logging
from src.services.provider_service import get_active_providers
from src.services.transfer_service import process_provider_transfer

# Configura o logging assim que a aplicação inicia
setup_logging()


def main():
    """
    Ponto de entrada principal da aplicação.
    """
    logger = logging.getLogger(__name__)
    logger.info('Iniciando o backend de transferência de ficheiros...')

    # Passo 1: Buscar os fornecedores do banco de dados
    providers = get_active_providers()

    if not providers:
        logger.info('Nenhuma tarefa a ser executada. Encerrando.')
        return

    # Por enquanto, apenas imprimimos os dados para verificar se funcionou
    logger.info('Fornecedores carregados com sucesso:')
    for provider in providers:
        process_provider_transfer(provider)


if __name__ == '__main__':
    main()
