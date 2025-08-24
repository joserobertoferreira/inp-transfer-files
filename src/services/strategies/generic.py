import logging
from datetime import datetime
from pathlib import Path

from .base import BaseTransferStrategy

logger = logging.getLogger(__name__)


class SpecificFilenameDownloadStrategy(BaseTransferStrategy):
    """
    Estratégia para fornecedores onde precisamos compor o nome dos
    ficheiros a serem baixados (ex: baseado na data de hoje).
    """

    def get_files_to_download(self) -> list[str]:
        # Exemplo: O fornecedor espera um ficheiro chamado 'dados_YYYYMMDD.csv'
        today_str = datetime.now().strftime('%Y%m%d')
        expected_filename = f'dados_{today_str}.csv'

        remote_path = self.provider.remote_input_folder
        logger.info(f'[{self.provider_id}] A procurar por ficheiro específico: {expected_filename} em {remote_path}')

        remote_files = self.manager.list_files(remote_path)
        # Usamos Path para extrair o nome base de cada ficheiro retornado pela listagem
        remote_basenames = [Path(f).name for f in remote_files]

        if expected_filename in remote_basenames:
            return [expected_filename]
        else:
            logger.warning(f"[{self.provider_id}] Ficheiro esperado '{expected_filename}' não encontrado no servidor.")
            return []
