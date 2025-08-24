import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.data_models import EditorParameters
from src.models.edition import Edition

logger = logging.getLogger(__name__)


class EditionRepository:
    """
    Handles all database operations for Editions.
    """

    def __init__(self, session: Session):
        self.session = session

    def get_edition_by_code(self, code: str) -> Optional[Edition]:
        """
        Fetches a Edition record by its code.
        Replaces your 'get_counter' method.
        """
        stmt = select(Edition).where(Edition.edition == code)
        return self.session.scalars(stmt).one_or_none()

    def get_edition_by_editor_code(self, params: EditorParameters) -> Optional[Edition]:
        """
        Fetches a Edition record by its editor code, edition number, suffix, provider_id, description and cover_date.
        Replaces your 'get_counter' method.
        """
        stmt = select(Edition).where(
            Edition.bipad == params.bipad,
            Edition.edition_number == params.edition_number,
            Edition.suffix == params.suffix,
            Edition.description == params.description,
            Edition.cover_date == params.cover_date,
        )
        return self.session.scalars(stmt).one_or_none()
