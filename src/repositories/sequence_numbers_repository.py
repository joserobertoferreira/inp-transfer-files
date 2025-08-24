import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.counter import CodeNumbers, SequenceNumbers

logger = logging.getLogger(__name__)


class SequenceRepository:
    """
    Handles all database operations for CodeNumbers and SequenceNumbers.
    """

    def __init__(self, session: Session):
        self.session = session

    def get_code_number_by_code(self, code: str) -> Optional[CodeNumbers]:
        """
        Fetches a CodeNumbers record by its code.
        Replaces your 'get_counter' method.
        """
        stmt = select(CodeNumbers).where(CodeNumbers.code_number == code)
        return self.session.scalars(stmt).one_or_none()

    def get_sequence_number(self, code: str, site: str, period: int, component: str) -> Optional[SequenceNumbers]:
        """
        Fetches the current sequence value from AVALNUM.
        Replaces your 'get_sequence' method.
        """
        stmt = select(SequenceNumbers).where(
            SequenceNumbers.code_number == code,
            SequenceNumbers.site == site,
            SequenceNumbers.period == period,
            SequenceNumbers.complement == component,
        )
        return self.session.scalars(stmt).one_or_none()

    def create_sequence_number(self, new_sequence: SequenceNumbers) -> None:
        """ """
        logger.info(f"Creating new sequence for code '{new_sequence.code_number}'...")
        self.session.add(new_sequence)
        self.session.flush()

    def increment_sequence_number(self, sequence: SequenceNumbers) -> int:  # noqa: PLR6301
        """
        Increments the sequence value by one and returns the new value.
        This uses an update statement for atomicity.
        """
        logger.info(f"Incrementing sequence for code '{sequence.code_number}'...")

        # Incrementa o valor no objeto
        sequence.sequence_number += 1
        self.session.add(sequence)
        self.session.flush()

        # O SQLAlchemy vai detetar a mudança e fazer o UPDATE durante o commit.
        # Retornamos o novo valor.
        return int(sequence.sequence_number)
