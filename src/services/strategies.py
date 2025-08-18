import logging
import posixpath
from dataclasses import dataclass, field
from datetime import datetime
from fnmatch import fnmatch
from pathlib import Path

from src.models.models import EdiPartners
from src.utils.local_menus import ImportExport, YesNo

logger = logging.getLogger(__name__)


@dataclass
class TransferTask:
    """Representa uma única tarefa de transferência definida pelos arrays."""

    delete: bool
    direction: ImportExport
    index: int
    is_active: bool
    prefix: str = field(default='')
    filenames: str = field(default='')


class BaseTransferStrategy:
    """
    Define o fluxo de trabalho de transferência padrão.
    Pode ser herdada para criar lógicas personalizadas para fornecedores específicos.
    """

    def __init__(self, manager, provider: EdiPartners):
        self.manager = manager
        self.provider = provider
        self.provider_id = self.provider.provider
        self.tasks: list[TransferTask] = []
        self._build_tasks()

    def _build_tasks(self):
        logger.debug(f'[{self.provider_id}] A construir lista de tarefas a partir do objeto EdiPartners.')

        # Acesso direto aos atributos do objeto!
        actives = self.provider.active_files
        directions = self.provider.direction_files
        prefixes = self.provider.prefix_files
        deletes = self.provider.delete_files

        if not (len(actives) == len(directions) == len(prefixes) == len(deletes)):
            logger.error(
                f'[{self.provider_id}] Inconsistência nos tamanhos dos arrays de configuração! '
                f'Nenhuma tarefa será executada.'
            )
            return

        for i, (active, direction_val, prefix, delete) in enumerate(zip(actives, directions, prefixes, deletes)):
            try:
                task = TransferTask(
                    delete=YesNo(delete) == YesNo.YES,
                    direction=ImportExport(direction_val),
                    index=i,
                    is_active=(YesNo(active) == YesNo.YES),
                    prefix=prefix if prefix is not None else '',
                )
                self.tasks.append(task)
            except (ValueError, TypeError) as e:
                logger.info(f'[{self.provider_id}] Valor inválido na configuração da Tarefa {i}: {e}. Ignorar tarefa.')
                continue

        logger.info((f'[{self.provider_id}] Foram selecionadas {len(self.tasks)} tarefas para execução.'))

    def _prepare_task(self, task: TransferTask) -> TransferTask:
        """
        Hook para modificar uma tarefa antes da sua execução.
        A implementação base retorna a tarefa sem modificações.
        """
        logger.debug(f'[{self.provider_id}] A preparar Tarefa {task.index} com a lógica base.')
        task.filenames = f'{task.prefix}*'
        logger.info(f"[{self.provider_id}] Tarefa {task.index} usará o padrão de ficheiro: '{task.filenames}'")
        return task

    def execute(self):
        """Ponto de entrada principal para executar a estratégia."""
        class_name = self.__class__.__name__
        logger.info(f'[{self.provider_id}] A executar a estratégia: {class_name}')

        if not self.tasks:
            logger.warning(f'[{self.provider_id}] Nenhuma tarefa válida foi construída. Nada a fazer.')
            return

        for task in self.tasks:
            # Prepara a tarefa para execução
            execute_task = self._prepare_task(task)

            # Verifica se a tarefa está ativa antes de processar
            if not execute_task.is_active:
                logger.info(
                    f'[{self.provider_id}] Tarefa {execute_task.index} (prefixo "{execute_task.prefix}") está inativa.'
                )
                continue

            # Log de início de processamento da tarefa
            log_direction = 'IMPORT/DOWNLOAD' if execute_task.direction == ImportExport.IMPORT else 'EXPORT/UPLOAD'
            logger.info(
                f'[{self.provider_id}] A processar Tarefa {task.index}: Direção={log_direction}, '
                f'Prefixo="{execute_task.prefix}"'
            )

            if execute_task.direction == ImportExport.IMPORT:
                self.process_download(execute_task)
            elif execute_task.direction == ImportExport.EXPORT:
                self.process_upload(execute_task)
            else:
                logger.warning(
                    f'[{self.provider_id}] Tarefa {execute_task.index} tem uma direção desconhecida: '
                    f'"{execute_task.direction}".'
                )

    # Lógica de Upload
    def get_files_to_upload(self) -> list[Path]:
        """Retorna uma lista de objetos Path para os ficheiros a serem enviados."""
        local_path = Path(self.provider.local_output_folder)
        if not local_path:
            return []

        local_path.mkdir(parents=True, exist_ok=True)  # Garante que o diretório existe

        # Uso de iterdir() e is_file() para uma abordagem mais limpa
        files = [file for file in local_path.iterdir() if file.is_file()]

        if files:
            logger.info(f"[{self.provider_id}] Encontrados {len(files)} ficheiros para upload em '{local_path}'.")
        return files

    def after_upload_success(self, local_file_path: Path, task: TransferTask):
        logger.debug(f'[{self.provider_id}] Tarefa {task.index}: Upload de {local_file_path.name} bem-sucedido.')

    def process_upload(self, task: TransferTask):
        # Acesso direto às propriedades e atributos do objeto!
        local_path = self.provider.local_output_folder
        remote_path = self.provider.remote_input_folder

        if not (local_path and remote_path):
            logger.error(f'[{self.provider_id}] Tarefa {task.index}: pastas de upload não configuradas.')
            return

        local_path = Path(local_path)
        local_path.mkdir(parents=True, exist_ok=True)

        all_remote_files = [f for f in local_path.iterdir() if f.is_file()]
        files_to_upload = [f for f in all_remote_files if fnmatch(Path(f).name, task.filenames)]

        if not files_to_upload:
            logger.info(
                f'[{self.provider_id}] Tarefa {task.index}: Nenhum ficheiro encontrado em {local_path} '
                f'com o prefixo {task.prefix}.'
            )
            return

        logger.info(
            f'[{self.provider_id}] Tarefa {task.index}: Encontrados {len(files_to_upload)} ficheiros para upload.'
        )

        for local_file in files_to_upload:
            remote_file = f'{remote_path}/{local_file.name}'
            logger.info(f'[{self.provider_id}] A enviar: {local_file} -> {remote_file}')
            if self.manager.upload_file(str(local_file), remote_file):
                self.after_upload_success(local_file, task)
            else:
                logger.error(f'[{self.provider_id}] Falha no upload de {local_file.name}.')

    # Lógica de Download
    def get_files_to_download(self) -> list[Path]:
        """Retorna uma lista de objetos Path para os ficheiros a serem baixados."""
        remote_path = self.provider.remote_input_folder
        if not remote_path:
            return []

        files = self.manager.list_files(remote_path)
        if files:
            logger.info(f'[{self.provider_id}] Encontrados {len(files)} ficheiros para download em {remote_path}.')
        return files

    def after_download_success(self, remote_file: str, task: TransferTask):
        logger.debug(f'[{self.provider_id}] Tarefa {task.index}: Download de {remote_file} bem-sucedido.')

    def process_download(self, task: TransferTask):
        # Acesso direto às propriedades e atributos do objeto!
        local_path = self.provider.local_input_folder
        remote_path = self.provider.remote_output_folder

        if not (local_path and remote_path):
            logger.error(f'[{self.provider_id}] Tarefa {task.index}: pastas de download não configuradas.')
            return

        local_path = Path(local_path)
        local_path.mkdir(parents=True, exist_ok=True)

        all_remote_files = self.manager.list_files(remote_path)
        files_to_download = [f for f in all_remote_files if fnmatch(Path(f).name, task.filenames)]

        if not files_to_download:
            logger.info(
                f'[{self.provider_id}] Tarefa {task.index}: Nenhum ficheiro encontrado em {remote_path} '
                f'com o prefixo "{task.prefix}".'
            )
            return

        logger.info(
            f'[{self.provider_id}] Tarefa {task.index}: Encontrados {len(files_to_download)} ficheiros para download.'
        )

        for remote_filename in files_to_download:
            base_filename = Path(remote_filename).name
            remote_file = f'{remote_path}/{base_filename}'
            local_file = local_path / base_filename
            logger.info(f'[{self.provider_id}] A receber: {remote_file} -> {local_file}')
            if self.manager.download_file(remote_file, str(local_file)):
                self.after_download_success(remote_file, task)
            else:
                logger.error(f'[{self.provider_id}] Falha no download de {base_filename}.')


class DeleteAfterDownloadStrategy(BaseTransferStrategy):
    """
    Estratégia para fornecedores que exigem que o ficheiro seja removido
    do servidor após o download bem-sucedido.
    """

    def after_download_success(self, remote_file: str, task: TransferTask):
        super().after_download_success(remote_file, task)

        logger.info(
            f'[{self.provider_id}][DeleteAfterDownload] Download de {remote_file} bem-sucedido. '
            f'A remover ficheiro remoto.'
        )

        # Extrai o nome base do ficheiro para o log, mas usa o caminho completo para a deleção.
        filename = Path(remote_file).name
        if not self.manager.delete_file(remote_file):
            logger.error(f'[{self.provider_id}] Falha ao remover o ficheiro remoto: {filename}')
        else:
            logger.info(f"[{self.provider_id}] Ficheiro remoto '{filename}' removido com sucesso.")


# Estratégias Personalizadas


class FranceMessagerieStrategy(DeleteAfterDownloadStrategy):
    """
    Estratégia específica para o fornecedor France Messagerie.
    - Download: ficheiros que começam com 'F' + username.
    - Upload: ficheiros que começam com 'I' + username.
    """

    def _prepare_task(self, task: TransferTask) -> TransferTask:
        prefix = task.prefix
        new_prefix = prefix[0] if prefix else ''

        if new_prefix != prefix:
            logger.info(
                f'[{self.provider_id}][FranceMessagerie] Ajustar prefixo da Tarefa {task.index} '
                f'de "{prefix}" para "{new_prefix}".'
            )
            task.prefix = new_prefix

        if task.prefix in {'R', 'C'}:
            task.is_active = False
            return task

        task.filenames = f'{task.prefix}{self.provider.username}.*'

        return task

    def get_files_to_download(self) -> list[str]:
        remote_path = self.provider.remote_output_folder
        if not remote_path:
            logger.warning(f'[{self.provider_id}] Diretório de input remoto não configurado.')
            return []

        # 1. Obter a lista "crua" do servidor
        raw_file_list = self.manager.list_files(remote_path)
        logger.debug(f'[{self.provider_id}] Lista de ficheiros recebida do servidor: {raw_file_list}')

        # 2. Filtrar as entradas especiais '.' e '..'
        #    Isto garante que só processamos nomes de ficheiros reais.
        filtered_list = [f for f in raw_file_list if f not in {'.', '..'}]

        # 3. Aplicar o padrão de nome de ficheiro específico do fornecedor
        filename_pattern = f'F{self.provider.username}.*'

        files_to_download = []
        for filename in filtered_list:
            basename = Path(filename).name
            if fnmatch(basename, filename_pattern):
                # 4. Construir o caminho completo de forma segura com posixpath.join
                full_path = posixpath.join(remote_path, basename)
                files_to_download.append(full_path)

        if files_to_download:
            logger.info(
                (
                    f'[{self.provider_id}] Filtro aplicado. Encontrados {len(files_to_download)} '
                    f'ficheiros para download com o padrão "{filename_pattern}".'
                )
            )
        else:
            logger.info(
                (
                    f'[{self.provider_id}] Nenhum ficheiro correspondente ao padrão '
                    f'"{filename_pattern}" encontrado no servidor.'
                )
            )

        return files_to_download

    def get_files_to_upload(self) -> list[Path]:
        local_path = Path(self.provider.local_output_folder)
        if not local_path.is_dir():
            logger.warning(f'[{self.provider_id}] Diretório de output local não encontrado: {local_path}')
            return []

        all_local_files = [f for f in local_path.iterdir() if f.is_file()]

        # O padrão para upload que definimos era 'I' + username
        filename_pattern = f'I{self.provider.username}.*'

        files_to_upload = [f for f in all_local_files if fnmatch(f.name, filename_pattern)]

        if files_to_upload:
            logger.info(
                f'[{self.provider_id}] Filtro aplicado. Encontrados {len(files_to_upload)} '
                f'ficheiros para upload com o padrão {filename_pattern}.'
            )

        return files_to_upload


class MlpStrategy(BaseTransferStrategy):
    """Estratégia para o fornecedor 1510 (usando o modelo EdiPartners)."""

    def _prepare_task(self, task: TransferTask) -> TransferTask:
        # task_date = datetime.now().strftime('%Y%m%d')
        task_date = '20250814'

        logger.info(f'[{self.provider_id}][MLP] Processar ficheiros para a {task_date} com o prefixo "{task.prefix}".')

        task.filenames = f'{task.prefix}{task_date}{self.provider.local_input_extension}'

        return task

    def get_files_to_download(self) -> list[str]:
        # Graças ao ArrayColumnMixin, podemos iterar diretamente!
        files_to_search = []
        today_str = datetime.now().strftime('%Y%m%d')

        # O Mixin nos dá listas, o que é muito mais limpo
        for i, prefix in enumerate(self.provider.prefix_files):
            is_active = self.provider.active_files[i] == YesNo.YES
            is_import = self.provider.direction_files[i] == ImportExport.IMPORT

            if is_active and is_import:
                filename_pattern = f'{prefix}{today_str}*.TXT'
                files_to_search.append(filename_pattern)

        remote_path = self.provider.remote_input_folder
        all_remote_files = self.manager.list_files(remote_path)

        matching_files = []
        for remote_file in all_remote_files:
            for pattern in files_to_search:
                if fnmatch(Path(remote_file).name, pattern):
                    matching_files.append(remote_file)
                    break

        return matching_files


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


# Mapa de Estratégias

# Aqui associamos um provider_id (ou outro identificador) à sua estratégia.
# A chave é o ID do fornecedor vindo do banco de dados (ex: '5508').
STRATEGY_MAP = {
    '1526': FranceMessagerieStrategy,
    '1510': MlpStrategy,
}


def get_strategy_for_provider(provider: EdiPartners) -> type[BaseTransferStrategy]:
    """
    Factory function que retorna a CLASSE de estratégia apropriada para um fornecedor.
    Se nenhuma estratégia específica for encontrada, retorna a classe base padrão.
    """
    # Usamos o provider_id (ou outro campo) para procurar no mapa de estratégias.
    provider_id = str(provider.provider)

    # .get() com um valor padrão é perfeito aqui. Se o ID não estiver no mapa, usa BaseTransferStrategy.
    StrategyClass = STRATEGY_MAP.get(provider_id, BaseTransferStrategy)

    logger.info(f"Fornecedor '{provider_id}' usará a classe de estratégia: {StrategyClass.__name__}")

    # Retornamos a classe em si, não uma instância.
    return StrategyClass
