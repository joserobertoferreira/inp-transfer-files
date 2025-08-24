import logging

from src.config.connection_ftp import FtpConfig
from src.models.edi_partner import EdiPartner
from src.services.strategies import get_strategy_for_provider
from src.transfer.ftp_manager import FtpManager
from src.transfer.sftp_manager import SftpManager
from src.utils.local_menus import FtpProtocol

logger = logging.getLogger(__name__)


def process_provider_transfer(provider: EdiPartner):
    """
    Orquestra a transferência de ficheiros para um único fornecedor,
    selecionando o manager de conexão e a estratégia de transferência apropriados.
    """
    provider_id = provider.provider

    try:
        # Converte o valor inteiro do banco de dados para um membro do Enum
        protocol_code = FtpProtocol(provider.protocol)
    except ValueError:
        logger.error(f'Fornecedor {provider_id} tem um código de protocolo inválido: {provider.protocol}')
        return

    logger.info(f"A iniciar processamento para o fornecedor: {provider_id} com protocolo: '{protocol_code.name}'")

    manager_map = {
        FtpProtocol.FTP: FtpManager,
        FtpProtocol.SFTP: SftpManager,
    }

    ManagerClass = manager_map.get(protocol_code)

    if not ManagerClass:
        logger.error(f'Nenhum Manager encontrado para o protocolo {protocol_code.name}')
        return

    try:
        if ManagerClass == FtpManager:
            # Configuração específica para FTP
            # is_binary = provider.binary_mode == YesNo.YES
            is_binary = True

            conn_config = FtpConfig(
                host=provider.url,
                user=provider.username,
                password=provider.password,
                binary_mode=is_binary,
                encoding='latin-1',
            )

        # 1. Obter a classe de estratégia correta para este fornecedor.
        #    A função `get_strategy_for_provider` decide se usa a base ou uma personalizada.
        StrategyClass = get_strategy_for_provider(provider)

        if StrategyClass.__name__ == 'BaseTransferStrategy':
            logger.info('Não processar se for uma estratégia genérica.')
            return

        # 2. Iniciar o manager de conexão (FTP ou SFTP) usando um context manager.
        #    Isto garante que a conexão é sempre fechada corretamente.
        with ManagerClass(config=conn_config) as manager:
            # 3. Instanciar a estratégia, passando o manager (já conectado) e a configuração do fornecedor.
            strategy_instance = StrategyClass(manager, provider)

            # 4. Mandar a estratégia executar o seu fluxo de trabalho.
            #    Toda a lógica de upload/download está encapsulada aqui.
            strategy_instance.execute()

        logger.info(f'Processamento para o fornecedor {provider_id} concluído com sucesso.')

    except Exception:
        # O logging com exc_info=True captura o traceback completo, essencial para depuração.
        logger.critical(
            f'Ocorreu um erro crítico não tratado durante o processamento do fornecedor {provider_id}.', exc_info=True
        )
