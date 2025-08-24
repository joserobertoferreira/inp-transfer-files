import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.config.settings import SCHEMA
from src.database.database_core import DatabaseCoreManager
from src.models.publication import Publication

logger = logging.getLogger(__name__)


class PublicationRepository:
    """
    Handles all database operations for publications.
    """

    def __init__(self, session: Session):
        self.session = session
        self.db_core = DatabaseCoreManager(session)
        self.schema = SCHEMA

    def get_publication_by_code(self, code: str) -> Optional[Publication]:
        """
        Fetches a publication record by its code.
        Replaces your 'get_counter' method.
        """
        stmt = select(Publication).where(Publication.code == code)
        return self.session.scalars(stmt).one_or_none()

    def find_publication_code(self, bipad: str, provider_id: str, description: str) -> Optional[str]:
        """
        Tenta encontrar um código de publicação através de várias lógicas em cascata.

        Args:
            bipad: Número do BIPAD da publicação.
            provider_id: Código do fornecedor.
            description: Descrição da publicação.

        Returns:
            O código da publicação (CODPUB_0) como string, ou None se não for encontrado.
        """
        logger.info(f"Searching for publication code for supplier '{provider_id}' and bipad '{bipad}'.")

        # Tentativa 1: Busca por dia da semana
        for day in range(1, 8):
            logger.info(f'Attempt 1: Searching by actual day of week ({day})...')
            result = self.db_core.execute_query(
                table=f'{self.schema}.ZREFPUB',
                columns=['CODPUB_0'],
                where_clauses={
                    'BPSREF_0': ('=', provider_id),
                    'REFEDI_0': ('=', bipad),
                    'DIADIS_0': ('=', day),
                    'ENAFLG_0': ('=', 2),
                },
                limit=1,
            )

            if result['status'] == 'success' and result['records'] > 0:
                pub_code = result['data'][0]['CODPUB_0']
                logger.info(f"Found publication code '{pub_code}' via day of week match.")
                return pub_code

        # Tentativa 2: Busca por bipad
        logger.info(f'Attempt 2: Searching by bipad ({bipad})...')
        result = self.db_core.execute_query(
            table=f'{self.schema}.ZREFPUB',
            columns=['CODPUB_0'],
            where_clauses={
                'BPSREF_0': ('=', provider_id),
                'REFEDI_0': ('=', bipad),
                'ENAFLG_0': ('=', 2),
            },
            limit=1,
        )

        if result['status'] == 'success' and result['records'] > 0:
            pub_code = result['data'][0]['CODPUB_0']
            logger.info(f"Found publication code '{pub_code}' by bipad.")
            return pub_code

        # Limpa os dados da descrição
        cleaned_input_desc = description.strip().replace("'", '').upper()
        if not cleaned_input_desc:
            cleaned_input_desc = ''

        # Tentativa 3: Busca por descrição
        pattern = f'{cleaned_input_desc}%'
        stmt = select(Publication.code, Publication.description, Publication.supplier_reference).where(
            Publication.description.like(pattern)
        )

        results = self.session.execute(stmt)

        for row in results:
            cleaned_desc = row.description.strip().replace("'", '').upper()
            if cleaned_desc == cleaned_input_desc:
                logger.info(f"Found publication code '{row.code}' via description match.")
                return row.code

        # Tentativa 4: Busca pelo código do fornecedor somente
        stmt = select(Publication.code, Publication.description).where(Publication.supplier_reference == provider_id)

        results = self.session.execute(stmt)

        for row in results:
            cleaned_desc = row.description.strip().replace("'", '').upper()
            if cleaned_desc == cleaned_input_desc:
                logger.info(f"Found publication code '{row.code}' via description match.")
                return row.code

        return None
