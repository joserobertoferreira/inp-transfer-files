from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict


class BaseParser(ABC):
    """
    Abstract Base Class (Interface) for all file parsers.
    Each parser is a generic "engine" for a specific file format.
    """

    @abstractmethod
    def parse(self, file_path: Path, config: Dict[str, Any]) -> Any:
        """
        Reads and processes the content of a file according to a given configuration.

        Args:
            file_path (Path): The path to the local file to be parsed.
            config (Dict[str, Any]): A dictionary containing the parsing rules,
                                     such as data models and field mappings.

        Returns:
            Any: A structured data object (or list of objects) with the parsed content.
        """
        raise NotImplementedError
