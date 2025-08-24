import logging
from datetime import date
from typing import Optional

from src.config.settings import DEFAULT_LEGACY_DATE, SCHEMA
from src.database.database_core import DatabaseCoreManager

logger = logging.getLogger(__name__)


class SupplierRepository:
    def __init__(self, core_db: DatabaseCoreManager):
        self.core_db = core_db
        self.schema = SCHEMA

    def get_start_liquidation_date(self, supplier_id: str) -> Optional[date]:
        """
        Busca a data de arranque da liquidação (ZARRLQD) para um fornecedor usando uma raw query.
        """
        query_result = self.core_db.execute_query(
            table=f'{self.schema}.BPSUPPLIER',
            columns=['ZARRLQD_0'],
            where_clauses={'BPRNUM_0': ('=', supplier_id)},
        )

        if query_result['status'] == 'success' and query_result['records'] > 0:
            # O resultado é uma lista de dicionários. Pegamos no primeiro.
            arrival_date = query_result['data'][0].get('ZARRLQD_0')

            # O driver pode retornar a data como um objeto datetime ou date, ou None
            if isinstance(arrival_date, date):
                return arrival_date

            logger.warning(
                f'O campo ZARRLQD_0 para o fornecedor {supplier_id} não é um objeto de data válido: {arrival_date}'
            )

        return None  # Retorna None se não encontrar ou se o campo for nulo

    def use_liquidation(self, supplier_id: str) -> bool:
        """
        Executa a lógica de negócio completa: busca a data e a compara.
        """
        try:
            start_date = self.get_start_liquidation_date(supplier_id)

            if not start_date or start_date <= DEFAULT_LEGACY_DATE:
                return False

            return start_date <= date.today()

        except Exception:
            logger.error(f'Erro ao verificar a data de chegada para o fornecedor {supplier_id}', exc_info=True)
            return False
