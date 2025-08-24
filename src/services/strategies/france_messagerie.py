import logging
import posixpath
from fnmatch import fnmatch
from pathlib import Path

from .base import BaseTransferStrategy, TransferTask

logger = logging.getLogger(__name__)


class FranceMessagerieStrategy(BaseTransferStrategy):
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

        task.filename = f'{task.prefix}{self.provider.username}.*'

        return task

    def get_files_to_download(self, task: TransferTask) -> list[str]:
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
        files_to_download = []
        for filename in filtered_list:
            basename = Path(filename).name
            if fnmatch(basename, task.filename):
                # 4. Construir o caminho completo de forma segura com posixpath.join
                full_path = posixpath.join(remote_path, basename)
                files_to_download.append(full_path)

        if files_to_download:
            logger.info(
                (
                    f'[{self.provider_id}] Filtro aplicado. Encontrados {len(files_to_download)} '
                    f'ficheiros para download com o padrão "{task.filename}".'
                )
            )
        else:
            logger.info(
                (
                    f'[{self.provider_id}] Nenhum ficheiro correspondente ao padrão '
                    f'"{task.filename}" encontrado no servidor.'
                )
            )

        return files_to_download

    def get_files_to_upload(self, task: TransferTask) -> list[Path]:
        local_path = Path(self.provider.local_output_folder)
        if not local_path.is_dir():
            logger.warning(f'[{self.provider_id}] Diretório de output local não encontrado: {local_path}')
            return []

        all_local_files = [f for f in local_path.iterdir() if f.is_file()]

        # O padrão para upload que definimos era 'I' + username
        files_to_upload = [f for f in all_local_files if fnmatch(f.name, task.filename)]

        if files_to_upload:
            logger.info(
                f'[{self.provider_id}] Filtro aplicado. Encontrados {len(files_to_upload)} '
                f'ficheiros para upload com o padrão {task.filename}.'
            )

        return files_to_upload
