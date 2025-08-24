import csv
import logging
from pathlib import Path
from typing import Any, Dict, List

from .base_parser import BaseParser

logger = logging.getLogger(__name__)


class CsvParser(BaseParser):
    """
    A generic parsing engine for CSV files.
    It is configured by a handler to map columns to a specific data model.
    """

    def parse(self, file_path: Path, config: Dict[str, Any]) -> List[Any]:
        logger.info(f"Parsing '{file_path.name}' with CsvParser engine.")

        DataModelClass = config['data_model']
        column_map = config.get('column_map', {})  # e.g., {'model_attr': 'CSV_COLUMN_NAME'}
        delimiter = config.get('delimiter', ';')
        encoding = config.get('encoding', 'latin-1')

        parsed_rows = []
        with open(file_path, 'r', encoding=encoding, newline='') as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            for row_dict in reader:
                # Create a dictionary for the dataclass constructor
                model_data = {}
                for model_attr, csv_col in column_map.items():
                    model_data[model_attr] = row_dict.get(csv_col)

                # Create an instance of the specific data model and add to the list
                parsed_rows.append(DataModelClass(**model_data))

        logger.info(f"Successfully parsed {len(parsed_rows)} rows into '{DataModelClass.__name__}' objects.")
        return parsed_rows
