from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict

from src.models.edi_partner import EdiPartner
from src.utils.generics import Generics

# This dictionary will act as a registry for our handlers.
HANDLER_REGISTRY = {}


def register_handler(provider_id: str):
    """A decorator to automatically register handler classes."""

    def decorator(cls):
        HANDLER_REGISTRY[provider_id] = cls
        return cls

    return decorator


class BaseHandler(ABC):
    """
    Abstract Base Class for provider-specific business logic handlers.
    Each handler defines the data model, the parser configuration, and
    the business logic for processing the parsed data.
    """

    def __init__(self, provider: EdiPartner):
        self.provider = provider
        self.provider_id = provider.provider

    def get_archive_path(self, original_file_path: Path) -> Path:
        """
        Determines the destination path for successfully processed files.
        Subclasses can override this to implement custom archive structures.

        The default is: <original_path>/ARCHIVE/<provider_id>/<filename>/<iso_year_week>
        """
        archive_dir = original_file_path.parent / 'ARCHIVE' / self.provider_id / Generics.get_year_and_iso_week()
        archive_dir.mkdir(parents=True, exist_ok=True)
        return archive_dir / original_file_path.name

    @staticmethod
    def get_error_path(original_file_path: Path) -> Path:
        """
        Determines the destination path for files that failed processing.
        Subclasses can override this.

        The default is: <original_path>/ERROR/<filename>
        """
        error_dir = original_file_path.parent / 'ERROR'
        error_dir.mkdir(parents=True, exist_ok=True)
        return error_dir / original_file_path.name

    @abstractmethod
    def get_parser_config(self) -> Dict[str, Any]:
        """
        Returns the configuration recipe for the generic parser engine.
        This recipe tells the parser which data model to use and how to map the fields.
        """
        raise NotImplementedError

    @abstractmethod
    def post_process(self, parsed_data: Any) -> bool:
        """
        Receives the structured data from the parser and applies business logic.
        (e.g., validation, transformation, loading into X3).

        Returns:
            bool: True if processing was successful, False otherwise.
        """
        raise NotImplementedError
