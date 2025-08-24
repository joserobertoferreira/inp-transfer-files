import logging
from fnmatch import fnmatch
from pathlib import Path

from src.models.data_models import TransferTask
from src.models.edi_partner import EdiPartner
from src.processing.orchestrator import FileProcessingOrchestrator
from src.utils.local_menus import ImportExport, YesNo

logger = logging.getLogger(__name__)


class BaseTransferStrategy:
    """
    Defines the standard workflow for transferring files.
    Its primary job is to connect to a remote server, find the correct files
    based on a task, and download/upload them.
    After a successful download, it triggers the processing orchestrator.
    """

    def __init__(self, manager, provider: EdiPartner):
        self.manager = manager
        self.provider = provider
        self.provider_id = self.provider.provider
        self.tasks: list[TransferTask] = []
        self._build_tasks()

    def _build_tasks(self):
        """Builds a list of TransferTask objects from the provider's configuration."""
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
        Hook to modify a task before execution. The base implementation
        creates a simple wildcard pattern from the task prefix.
        """
        logger.debug(f'[{self.provider_id}] A preparar Tarefa {task.index} com a lógica base.')
        task.filename = f'{task.prefix}*'
        logger.info(f"[{self.provider_id}] Tarefa {task.index} usará o padrão de ficheiro: '{task.filename}'")
        return task

    def execute(self):
        """Main entry point to execute the transfer strategy."""
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
    def get_files_to_upload(self, task: TransferTask) -> list[Path]:
        """Return a list of Path objects for the files to be uploaded."""
        local_path = Path(self.provider.local_output_folder)
        if not local_path.is_dir():
            logger.warning(f'[{self.provider_id}] Local output directory not found: {local_path}')
            return []

        local_path.mkdir(parents=True, exist_ok=True)  # Garante que o diretório existe

        # Uso de iterdir() e is_file() para uma abordagem mais limpa
        files = [file for file in local_path.iterdir() if file.is_file()]

        # Filter using the pattern prepared in _prepare_task
        to_upload = [f for f in files if fnmatch(f.name, task.filename)]

        if to_upload:
            logger.info(f'[{self.provider_id}] Encontrados {len(to_upload)} ficheiros para upload em {local_path}.')

        return to_upload

    def after_upload_success(self, local_file_path: Path, task: TransferTask):
        """Hook called after a successful upload."""
        logger.debug(f'[{self.provider_id}] Task {task.index}: Upload of {local_file_path.name} successful.')
        if task.delete:
            logger.info(f'[{self.provider_id}] Deleting local file after upload: {local_file_path.name}')
            try:
                local_file_path.unlink()
            except OSError as e:
                logger.error(f'[{self.provider_id}] Failed to delete local file {local_file_path}: {e}')

    def process_upload(self, task: TransferTask):
        """Handles the upload logic for a single task."""
        remote_path = self.provider.remote_input_folder

        if not remote_path:
            logger.error(f'[{self.provider_id}] Tarefa {task.index}: pastas de upload não configuradas.')
            return

        files_to_upload = self.get_files_to_upload(task)

        if not files_to_upload:
            logger.info(
                f'[{self.provider_id}] Tarefa {task.index}: Nenhum ficheiro encontrado com o prefixo {task.prefix}.'
            )
            return

        logger.info(
            f'[{self.provider_id}] Tarefa {task.index}: Encontrados {len(files_to_upload)} ficheiros para upload.'
        )

        for local_file in files_to_upload:
            remote_file = f'{remote_path.rstrip("/")}/{local_file.name}'

            logger.info(f'[{self.provider_id}] A enviar: {local_file} -> {remote_file}')

            if self.manager.upload_file(str(local_file), remote_file):
                self.after_upload_success(local_file, task)
            else:
                logger.error(f'[{self.provider_id}] Falha no upload de {local_file.name}.')

    # Lógica de Download
    def get_files_to_download(self, task: TransferTask) -> list[str]:
        """Retorna uma lista de objetos Path para os ficheiros a serem baixados."""
        remote_path = self.provider.remote_input_folder
        if not remote_path:
            return []

        files = self.manager.list_files(remote_path)

        # Filter the list on the client side
        to_download = [f for f in files if fnmatch(Path(f).name, task.filename)]

        if to_download:
            logger.info(
                f'[{self.provider_id}] Encontrados {len(to_download)} ficheiros para download em {remote_path}.'
            )
        return to_download

    def after_download_success(self, remote_file: str, local_file: Path, task: TransferTask):
        """
        Hook called after a successful download. This is the integration point
        with the processing layer.
        """
        logger.debug(
            f'[{self.provider_id}] Download de {remote_file} para {local_file} bem-sucedido. Iniciar processamento.'
        )

        orchestrator = FileProcessingOrchestrator(provider=self.provider, task=task)
        orchestrator.process(local_file)

        # After processing, we might still want to delete the remote file
        if task.delete:
            logger.info(f'[{self.provider_id}] Deleting remote file after processing: {remote_file}')
            if not self.manager.delete_file(remote_file):
                logger.error(f'[{self.provider_id}] Failed to delete remote file: {remote_file}')

    def process_download(self, task: TransferTask):
        """Handles the download logic for a single task."""
        local_path = self.provider.local_input_folder
        remote_path = self.provider.remote_output_folder

        if not (local_path and remote_path):
            logger.error(f'[{self.provider_id}] Tarefa {task.index}: pastas de download não configuradas.')
            return

        local_path = Path(local_path)
        local_path.mkdir(parents=True, exist_ok=True)

        files_to_download = self.get_files_to_download(task)

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
            remote_file = f'{remote_path.rstrip("/")}/{base_filename}'
            local_file = local_path / base_filename

            logger.info(f'[{self.provider_id}] A receber: {remote_file} -> {local_file}')

            if self.manager.download_file(remote_file, str(local_file)):
                self.after_download_success(remote_file, local_file, task)
            else:
                logger.error(f'[{self.provider_id}] Falha no download de {base_filename}.')
