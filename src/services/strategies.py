import logging
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class BaseTransferStrategy:
    """
    Define o fluxo de trabalho de transferência padrão.
    Pode ser herdada para criar lógicas personalizadas para fornecedores específicos.
    """

    def __init__(self, manager, provider_config: dict[str, Any]):
        self.manager = manager
        self.provider = provider_config
        self.provider_id = self.provider.get('provider_id', 'N/A')

    def execute(self):
        """Ponto de entrada principal para executar a estratégia."""
        logger.info(f'[{self.provider_id}] A executar a estratégia de transferência padrão.')
        self.process_downloads()
        self.process_uploads()

    # Lógica de Upload
    def get_files_to_upload(self) -> list[Path]:
        """Retorna uma lista de objetos Path para os ficheiros a serem enviados."""
        local_path_str = self.provider.get('local_path_out')
        if not local_path_str:
            return []

        local_path = Path(local_path_str)
        local_path.mkdir(parents=True, exist_ok=True)  # Garante que o diretório existe

        # Uso de iterdir() e is_file() para uma abordagem mais limpa
        files = [file for file in local_path.iterdir() if file.is_file()]

        if files:
            logger.info(f"[{self.provider_id}] Encontrados {len(files)} ficheiros para upload em '{local_path}'.")
        return files

    def after_upload_success(self, local_file: Path):
        """Ação a ser executada após um upload bem-sucedido. Padrão: não fazer nada."""
        logger.debug(f'[{self.provider_id}] Upload de {local_file} bem-sucedido. Nenhuma ação pós-upload definida.')
        # Futuramente: Mover para um arquivo. Ex: os.rename(local_file, f"{local_file}.bak")

    def process_uploads(self):
        remote_path = self.provider.get('remote_path_out')
        if not remote_path:
            logger.debug(f'[{self.provider_id}] Configuração de upload (remote_path_out) incompleta. A saltar.')
            return

        for local_file in self.get_files_to_upload():
            # O operador / junta caminhos de forma segura
            remote_file = f'{remote_path}/{local_file.name}'

            logger.info(f'[{self.provider_id}] A enviar ficheiro: {local_file} -> {remote_file}')
            # Passamos o caminho como string para a função de upload, que espera uma string
            if self.manager.upload_file(str(local_file), remote_file):
                self.after_upload_success(local_file)
            else:
                logger.error(f'[{self.provider_id}] Falha no upload de {local_file.name}.')

    # Lógica de Download
    def get_files_to_download(self) -> list[Path]:
        """Retorna uma lista de objetos Path para os ficheiros a serem baixados."""
        remote_path = self.provider.get('remote_path_in')
        if not remote_path:
            return []

        files = self.manager.list_files(remote_path)
        if files:
            logger.info(f"[{self.provider_id}] Encontrados {len(files)} ficheiros para download em '{remote_path}'.")
        return files

    def after_download_success(self, remote_file: str):
        """Ação a ser executada após um download bem-sucedido. Padrão: não fazer nada."""
        logger.debug(
            f'[{self.provider_id}] Download de {remote_file} bem-sucedido. Nenhuma ação pós-download definida.'
        )

    def process_downloads(self):
        remote_path = self.provider.get('remote_path_in')
        local_path = self.provider.get('local_path_in')

        if not (remote_path and local_path):
            logger.debug(f'[{self.provider_id}] Configuração de download incompleta. A saltar.')
            return

        local_path = Path(local_path)
        local_path.mkdir(parents=True, exist_ok=True)

        for remote_filename in self.get_files_to_download():
            # Usamos Path para extrair o nome base do ficheiro de forma robusta
            base_filename = Path(remote_filename).name
            remote_file = f'{remote_path}/{base_filename}'
            # O operador / junta o diretório local com o nome do ficheiro
            local_file = local_path / base_filename

            logger.info(f'[{self.provider_id}] A receber ficheiro: {remote_file} -> {local_file}')
            # Passamos o caminho como string para a função de download
            if self.manager.download_file(remote_file, str(local_file)):
                self.after_download_success(remote_file)
            else:
                logger.error(f'[{self.provider_id}] Falha no download de {base_filename}.')


# --- Estratégias Personalizadas ---


class DeleteAfterDownloadStrategy(BaseTransferStrategy):
    """
    Estratégia para fornecedores que exigem que o ficheiro seja removido
    do servidor após o download bem-sucedido.
    """

    def after_download_success(self, remote_file: str):
        logger.info(f'[{self.provider_id}] Download de {remote_file} bem-sucedido. A remover ficheiro remoto.')
        if not self.manager.delete_file(remote_file):
            logger.error(f'[{self.provider_id}] Falha ao remover o ficheiro remoto: {remote_file}')


class SpecificFilenameDownloadStrategy(BaseTransferStrategy):
    """
    Estratégia para fornecedores onde precisamos compor o nome dos
    ficheiros a serem baixados (ex: baseado na data de hoje).
    """

    def get_files_to_download(self) -> list[str]:
        # Exemplo: O fornecedor espera um ficheiro chamado 'dados_YYYYMMDD.csv'
        today_str = datetime.now().strftime('%Y%m%d')
        expected_filename = f'dados_{today_str}.csv'

        remote_path = self.provider.get('remote_path_in')
        logger.info(f'[{self.provider_id}] A procurar por ficheiro específico: {expected_filename} em {remote_path}')

        remote_files = self.manager.list_files(remote_path)
        # Usamos Path para extrair o nome base de cada ficheiro retornado pela listagem
        remote_basenames = [Path(f).name for f in remote_files]

        if expected_filename in remote_basenames:
            return [expected_filename]
        else:
            logger.warning(f"[{self.provider_id}] Ficheiro esperado '{expected_filename}' não encontrado no servidor.")
            return []


# --- Mapa de Estratégias ---

# Aqui associamos um provider_id (ou outro identificador) à sua estratégia.
# A chave é o ID do fornecedor vindo do banco de dados (ex: '5508').
STRATEGY_MAP = {
    'FORNECEDOR_QUE_DELETA': DeleteAfterDownloadStrategy,
    'FORNECEDOR_COM_NOME_ESPECIFICO': SpecificFilenameDownloadStrategy,
}


def get_strategy_for_provider(provider_config: dict[str, Any]) -> type[BaseTransferStrategy]:
    """
    Factory function que retorna a CLASSE de estratégia apropriada para um fornecedor.
    Se nenhuma estratégia específica for encontrada, retorna a classe base padrão.
    """
    # Usamos o provider_id (ou outro campo) para procurar no mapa de estratégias.
    provider_id = str(provider_config.get('provider_id'))

    # .get() com um valor padrão é perfeito aqui. Se o ID não estiver no mapa, usa BaseTransferStrategy.
    StrategyClass = STRATEGY_MAP.get(provider_id, BaseTransferStrategy)

    logger.info(f"Fornecedor '{provider_id}' usará a classe de estratégia: {StrategyClass.__name__}")

    # Retornamos a classe em si, não uma instância.
    return StrategyClass
