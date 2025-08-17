import logging

from src.models.models import EdiPartners
from src.services.strategies import get_strategy_for_provider
from src.transfer.ftp_manager import FtpManager
from src.transfer.sftp_manager import SftpManager
from src.utils.local_menus import Chapter1

logger = logging.getLogger(__name__)


def process_provider_transfer(provider: EdiPartners):
    """
    Orquestra a transferência de ficheiros para um único fornecedor,
    selecionando o manager de conexão e a estratégia de transferência apropriados.
    """
    provider_id = provider.provider
    protocol_code = str(provider.protocol)

    logger.info(f"A iniciar processamento para o fornecedor: {provider_id} com código de protocolo: '{protocol_code}'")

    # Mapeamento do código do protocolo (vindo do DB) para a classe Manager.
    # Isto torna o código mais explícito e fácil de entender.
    manager_map = {
        '1': FtpManager,  # Supondo que 1 = FTP
        '2': SftpManager,  # Supondo que 2 = SFTP
    }

    ManagerClass = manager_map.get(protocol_code)

    if not ManagerClass:
        logger.error(
            (
                f"Protocolo '{protocol_code}' desconhecido ou não suportado para o fornecedor "
                f'{provider_id}. A saltar processamento.'
            )
        )
        return

    extra_params = {}

    if ManagerClass is SftpManager and provider.private_key_folder:
        extra_params['private_key'] = provider.private_key_folder

    if ManagerClass is FtpManager and provider.binary_mode == Chapter1.YES:
        extra_params['binary_mode'] = True

    try:
        # 1. Obter a classe de estratégia correta para este fornecedor.
        #    A função `get_strategy_for_provider` decide se usa a base ou uma personalizada.
        StrategyClass = get_strategy_for_provider(provider)

        # 2. Iniciar o manager de conexão (FTP ou SFTP) usando um context manager.
        #    Isto garante que a conexão é sempre fechada corretamente.
        default_port = None

        with ManagerClass(
            host=provider.url,
            port=default_port,
            user=provider.username,
            password=provider.password,
            **extra_params,
        ) as manager:
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
