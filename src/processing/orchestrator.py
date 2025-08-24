import logging
from datetime import datetime
from pathlib import Path

from src.models.edi_partner import EdiPartner
from src.processing.handlers import get_handler_for_provider
from src.processing.parsers.csv_format_parser import CsvParser
from src.processing.parsers.fixed_format_parser import FixedFormatParser
from src.services.strategies.base import TransferTask

logger = logging.getLogger(__name__)

# Map of parser types to their engine classes
PARSER_ENGINE_MAP = {
    'FIXED_FORMAT': FixedFormatParser,
    'CSV': CsvParser,
}


class FileProcessingOrchestrator:
    """Orchestrates the Parser -> Handler pipeline."""

    def __init__(self, provider: EdiPartner, task: TransferTask):
        self.provider = provider
        self.task = task
        self.provider_id = provider.provider

    def process(self, file_path: Path) -> bool:
        logger.info(f'[{self.provider_id}] Starting processing orchestration for: {file_path.name}')

        handler = None

        try:
            # 1. Decide which Handler to use
            HandlerClass = get_handler_for_provider(self.provider_id)
            handler = HandlerClass(self.provider)

            # 2. The Handler provides the recipe for parsing
            parser_config = handler.get_parser_config()

            # 3. The Orchestrator selects the correct Parser Engine
            parser_type = parser_config.pop('parser_type')
            ParserEngineClass = PARSER_ENGINE_MAP[parser_type]
            parser_engine = ParserEngineClass()

            # 4. The Engine parses the file using the Handler's recipe
            parsed_data = parser_engine.parse(file_path, config=parser_config)

            # 5. The Handler applies business logic to the structured data
            success = handler.post_process(parsed_data)

            if success:
                logger.info(f"[{self.provider_id}] Processing of '{file_path.name}' completed successfully.")
                archive_dir = handler.get_archive_path(file_path)
                file_path.rename(archive_dir)
                logger.info(f'File moved to: {archive_dir}')
            else:
                logger.error(
                    f"[{self.provider_id}] Business logic failed for '{file_path.name}'. Moving to error folder."
                )
                error_dir = handler.get_error_path(file_path)
                file_path.rename(error_dir)
                logger.info(f'File moved to: {error_dir}')

            return success

        except Exception:
            logger.critical(
                f'[{self.provider_id}] Critical failure in processing pipeline for {file_path.name}', exc_info=True
            )

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            error_filename = f'{file_path.stem}_{timestamp}{file_path.suffix}'

            if handler:
                error_dir = handler.get_error_path(file_path).with_name(error_filename)
            else:
                # Fallback seguro
                error_dir = file_path.parent / 'ERROR' / error_filename
                error_dir.parent.mkdir(parents=True, exist_ok=True)

            # Garante que não perdemos o ficheiro em caso de erro crítico
            if file_path.exists():
                file_path.rename(error_dir)
                logger.info(f'File moved to fallback error path: {error_dir}')

            return False
