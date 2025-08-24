import logging

from sqlalchemy.orm import Session

from src.models.data_models import FranceMessagerieInvoice

logger = logging.getLogger(__name__)


class FranceMessagerieInvoiceRepository:
    """
    Handles all database operations for France Messagerie invoices.
    """

    def __init__(self, session: Session):
        self.session = session

    def create_invoice(self, invoice: FranceMessagerieInvoice) -> None:
        """
        Creates a new France Messagerie invoice in the database.
        """

        # Verifica se existe liquidação para a fatura

        self.session.add(invoice)
