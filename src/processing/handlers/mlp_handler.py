import logging
from dataclasses import dataclass
from typing import Any, Dict, List

from .base_handler import BaseHandler, register_handler

logger = logging.getLogger(__name__)


# 1. PROVIDER-SPECIFIC DATA MODEL
@dataclass
class MlpRow:
    product_id: str
    quantity: int


# 2. HANDLER REGISTRATION AND IMPLEMENTATION
@register_handler('1510')
class MlpHandler(BaseHandler):
    """Business logic handler for MLP."""

    def get_parser_config(self) -> Dict[str, Any]:
        """Provides the recipe for the CsvParser."""
        return {
            'parser_type': 'CSV',
            'data_model': MlpRow,
            'encoding': 'latin-1',
            'delimiter': ';',
            'column_map': {
                'product_id': 'ID-PROD',
                'quantity': 'QTY',
            },
        }

    def post_process(self, parsed_data: List[MlpRow]) -> bool:
        """Applies business logic to the parsed MLP data."""
        logger.info(f'[{self.provider_id}] Applying MLP business logic to {len(parsed_data)} rows...')
        total_quantity = sum(row.quantity for row in parsed_data if isinstance(row.quantity, int))
        logger.info(f'Total quantity from file: {total_quantity}')
        return True
