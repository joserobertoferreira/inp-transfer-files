import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from src.processing.parsers.base_parser import BaseParser

logger = logging.getLogger(__name__)


@dataclass
class ParsedDocumentRaw:
    """Um contentor para os dados crus (strings) lidos do ficheiro."""

    header: dict[str, str] = field(default_factory=dict)
    details: list[dict[str, str]] = field(default_factory=list)
    totals: list[dict[str, str]] = field(default_factory=list)
    footer: dict[str, str] = field(default_factory=dict)


class FixedFormatParser(BaseParser):
    """
    A generic parsing engine for fixed-format files with a
    header-details-footer structure. It is configured by a handler.
    """

    @staticmethod
    def _slice_line(line: str, line_map: dict[str, tuple]) -> dict[str, str]:
        """Extrai as substrings de uma linha com base no mapa."""
        data = {}
        for field_name, (start, end) in line_map.items():
            if len(line) >= end:
                data[field_name] = line[start:end]  # Não faz .strip() aqui, deixa para o handler
            else:
                logger.warning(
                    f'Line is too short to slice for field "{field_name}". '
                    f'Line length: {len(line)}, expected end: {end}.'
                )
                data[field_name] = ''

        return data

    @staticmethod
    def _get_line_type(line: str, line_definitions: dict[str, tuple]) -> Optional[str]:
        """
        Identifica o tipo de linha (ex: 'header', 'detail') com base nas definições.
        Retorna o nome do tipo ou None se não corresponder a nenhum.
        """
        for type_name, (start, end, expected_value) in line_definitions.items():
            if line[start:end] == expected_value:
                return type_name
        return None

    def parse(self, file_path: Path, config: dict[str, Any]) -> ParsedDocumentRaw:
        logger.info(f"Extracting raw string data from '{file_path.name}' with FixedFormatParser.")

        line_definitions = config['line_definitions']
        header_map = config.get('header_map', {})
        detail_map = config.get('detail_map', {})
        totals_map = config.get('totals_map', {})
        footer_map = config.get('footer_map', {})
        encoding = config.get('encoding', 'latin-1')

        raw_document = ParsedDocumentRaw()
        state = 'EXPECTING_HEADER'

        state_actions = {
            'EXPECTING_HEADER': {
                'header': lambda line: (
                    setattr(raw_document, 'header', self._slice_line(line, header_map)),
                    'EXPECTING_DETAILS',
                ),
            },
            'EXPECTING_DETAILS': {
                'detail': lambda line: (
                    raw_document.details.append(self._slice_line(line, detail_map)),
                    'EXPECTING_DETAILS',
                ),
                'totals': lambda line: (
                    raw_document.totals.append(self._slice_line(line, totals_map)),
                    'EXPECTING_TOTALS',
                ),
            },
            'EXPECTING_TOTALS': {
                'totals': lambda line: (
                    raw_document.totals.append(self._slice_line(line, totals_map)),
                    'EXPECTING_TOTALS',
                ),
                'footer': lambda line: (
                    setattr(raw_document, 'footer', self._slice_line(line, footer_map)),
                    'EXPECTING_EOF',
                ),
            },
        }

        with open(file_path, 'r', encoding=encoding) as f:
            for line_num, raw_line in enumerate(f, 1):
                line = raw_line.rstrip('\n\r')
                if not line:
                    continue

                line_type_id = self._get_line_type(line, line_definitions)

                if not line_type_id:
                    logger.warning(f'Ignoring unrecognized line format on line {line_num}.')
                    continue

                if state == 'EXPECTING_EOF':
                    raise ValueError(f'Structural error on line {line_num}: Extra data found after footer.')

                actions = state_actions.get(state, {})
                if line_type_id in actions:
                    _, next_state = actions[line_type_id](line)
                    state = next_state
                else:
                    expected_types = ' or '.join(actions.keys())
                    raise ValueError(
                        f'Structural error on line {line_num}: Expected a "{expected_types}" line, '
                        f'found "{line_type_id}".'
                    )

        if not raw_document.footer:
            raise ValueError('Structural error: End of file reached but footer (type 3) was not found.')

        return raw_document
