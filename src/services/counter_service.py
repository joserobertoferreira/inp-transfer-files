import logging
from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from src.models.counter import CodeNumbers, SequenceNumbers
from src.repositories.sequence_numbers_repository import SequenceRepository
from src.utils.local_menus import PositionType

logger = logging.getLogger(__name__)


class CounterService:
    """
    Generates formatted sequence numbers based on dynamic rules
    defined in the database (ACODNUM table).
    """

    def __init__(self, session: Session):
        """
        Initializes the service with an SQLAlchemy session.
        """
        self.session = session
        self.repo = SequenceRepository(session)

    def generate_number(self, code: str, site: str, generation_date: date, complement: str = '') -> Optional[str]:
        """
        The main method to generate a new formatted number.

        Args:
            code: The counter code (CODNUM_0).
            site: The site context for the sequence.
            generation_date: The date to use for date-based parts of the sequence.
            complement: An optional complement for sequences that depend on it.

        Returns:
            The newly generated formatted number as a string, or None if generation fails.
        """
        logger.info(f"Generating number for counter '{code}' with site '{site}' and complement '{complement}'.")

        # 1. Get the counter rules from ACODNUM
        counter_rules = self.repo.get_code_number_by_code(code)
        if not counter_rules:
            logger.error(f"Counter rules for code '{code}' not found in ACODNUM.")
            return None

        # 2. Check if a sequence complement is needed
        if not self._has_sequence_component(counter_rules):
            logger.info(f"Counter '{code}' has no sequence component. Returning static number.")
            return self._build_formatted_number(counter_rules, generation_date, 0, complement)

        # 3. Determine the complement component for the sequence lookup
        lookup_complement = complement if self._has_complement_component(counter_rules) else ''

        # 4. Determine the period and component for the sequence lookup
        period = self._get_period(counter_rules, generation_date)

        # 5. Get the current sequence value from AVALNUM
        sequence = self.repo.get_sequence_number(code, site, period, lookup_complement)

        if sequence:
            # Sequence exists, increment it
            new_sequence_value = self.repo.increment_sequence_number(sequence=sequence)
        else:
            # Sequence does not exist, create a new one starting at 1
            new_sequence_value = 1
            new_sequence_record = SequenceNumbers(
                code_number=code,
                site=site or '',
                period=period,
                complement=lookup_complement,
                sequence_number=new_sequence_value,
            )
            self.repo.create_sequence_number(new_sequence_record)

        # 5. Build the final formatted number string
        return self._build_formatted_number(counter_rules, generation_date, new_sequence_value, complement)

    @staticmethod
    def _has_sequence_component(counter_rules: CodeNumbers) -> bool:
        """Checks if any component is of type SEQUENCE."""
        return any(comp_type == PositionType.SEQUENCE for comp_type in counter_rules.components_type)

    @staticmethod
    def _has_complement_component(counter_rules: CodeNumbers) -> bool:
        """Checks if any component is of type COMPLEMENT."""
        return any(comp_type == PositionType.COMPLEMENT for comp_type in counter_rules.components_type)

    @staticmethod
    def _get_period(counter_rules: CodeNumbers, current_date: date) -> int:
        """Calculates the period based on the reset-to-zero level."""
        rtz_level = counter_rules.rtz_level
        if rtz_level == 2:  # Yearly reset  # noqa: PLR2004
            return int(current_date.strftime('%y'))
        elif rtz_level == 3:  # Monthly reset  # noqa: PLR2004
            return int(current_date.strftime('%y%m'))
        return 0  # No reset

    @staticmethod
    def _build_formatted_number(rules: CodeNumbers, current_date: date, sequence_number: int, complement: str) -> str:
        """
        Constructs the final formatted string based on the counter rules.
        """
        parts = []
        for i in range(rules.number_of_components):
            comp_type = PositionType(rules.components_type[i])  # Convert int to Enum
            comp_length = rules.components_length[i]
            constant = rules.constants[i]

            if comp_length is None:
                comp_length = 0

            part = ''
            if comp_type == PositionType.CONSTANT:
                part = constant
            elif comp_type == PositionType.YEAR:
                part = f'{current_date.year:0{comp_length}d}'[-comp_length:]  # Handles 2 or 4 digits
            elif comp_type == PositionType.MONTH:
                part = f'{current_date.month:02d}'
            elif comp_type == PositionType.DAY:
                part = f'{current_date.day:02d}'
            elif comp_type == PositionType.WEEK:
                part = current_date.strftime('%V')  # ISO Week
            elif comp_type == PositionType.SEQUENCE:
                part = f'{sequence_number:0{comp_length}d}'
            elif comp_type == PositionType.COMPLEMENT:
                part = complement

            parts.append(str(part))

        return ''.join(parts)
