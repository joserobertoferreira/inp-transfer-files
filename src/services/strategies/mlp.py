import logging
from datetime import datetime
from fnmatch import fnmatch
from pathlib import Path

from src.services.strategies.base import BaseTransferStrategy, TransferTask
from src.utils.local_menus import ImportExport, YesNo

logger = logging.getLogger(__name__)


class MlpStrategy(BaseTransferStrategy):
    """Estratégia para o fornecedor 1510 (usando o modelo EdiPartners)."""

    def _prepare_task(self, task: TransferTask) -> TransferTask:
        # task_date = datetime.now().strftime('%Y%m%d')
        task_date = '20250814'

        logger.info(f'[{self.provider_id}][MLP] Processar ficheiros para a {task_date} com o prefixo "{task.prefix}".')

        task.filename = f'{task.prefix}{task_date}{self.provider.local_input_extension}'

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
