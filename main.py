import logging

from src.config.logging import setup_logging
from src.services.provider_service import get_active_providers

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
        # Imprimimos sem a senha por segurança
        provider_info_safe = provider.copy()
        provider_info_safe['password'] = '********'
        logger.info(f'-> {provider_info_safe}')

    # Próximos passos (Fase 3):
    # - Iterar sobre cada 'provider'
    # - Instanciar o cliente correto (FTP ou SFTP) com as credenciais
    # - Executar a lógica de transferência


if __name__ == '__main__':
    main()
