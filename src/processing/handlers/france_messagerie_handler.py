import logging
from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from src.database.database import db
from src.database.database_core import DatabaseCoreManager
from src.models.data_models import (
    FranceMessagerieDetailLine,
    FranceMessagerieFooter,
    FranceMessagerieHeader,
    FranceMessagerieInvoice,
    FranceMessagerieTotals,
)
from src.models.edition import Edition
from src.processing.handlers.base_handler import BaseHandler, register_handler
from src.processing.parsers.fixed_format_parser import ParsedDocumentRaw
from src.repositories.edition_repository import EditionRepository
from src.repositories.supplier_repository import SupplierRepository
from src.utils.conversions import Conversions
from src.utils.local_menus import YesNo

logger = logging.getLogger(__name__)


@register_handler('1526')
class FranceMessagerieHandler(BaseHandler):
    """Business logic handler for France Messagerie."""

    def get_parser_config(self) -> dict[str, Any]:  # noqa: PLR6301
        """Provides the recipe for the FixedFormatParser."""
        return {
            'parser_type': 'FIXED_FORMAT',
            'encoding': 'cp1252',  # Specific encoding for this provider
            'data_model': FranceMessagerieInvoice,
            'header_model': FranceMessagerieHeader,
            'detail_model': FranceMessagerieDetailLine,
            'total_model': FranceMessagerieTotals,
            'footer_model': FranceMessagerieFooter,
            'line_definitions': {
                'header': (0, 1, '1'),
                'detail': (0, 1, '2'),
                'total': (0, 1, '3'),
                'footer': (0, 1, '4'),
            },
            'header_map': {
                'invoice_date': (1, 9),
                'gexpex_code': (9, 16),
                'nim_code': (23, 25),
                'invoice_number': (57, 67),
                'currency': (67, 70),
                'transport_type': (82, 83),
                'invoice_or_complement': (83, 84),
                'invoice_or_credit_note': (86, 87),
            },
            'detail_map': {
                'bipad': (11, 15),
                'extension': (15, 17),
                'label': (17, 19),
                'edition': (19, 25),
                'suffix': (25, 26),
                'quantity': (26, 33),
                'description': (40, 70),
                'chrono': (70, 76),
                'net_price': (77, 87),
                'original_invoice': (87, 97),
                'correction_type': (97, 98),
                'discount': (101, 106),
                'weight': (115, 119),
                'gross_price': (119, 123),
                'tax': (131, 137),
                'amount_with_tax': (138, 140),
                'amount_without_tax': (139, 141),
                'net_price_with_discount': (140, 142),
                'amount_without_tax_with_discount': (142, 143),
            },
            'totals_map': {
                'total_amount_including_tax': (16, 31),
                'total_amount_excluding_tax': (31, 46),
            },
            'footer_map': {
                'footer_line': (1, 80),
            },
        }

    def _get_header_data(
        self, db: DatabaseCoreManager, invoice_date: date, parsed_data: ParsedDocumentRaw
    ) -> FranceMessagerieHeader:
        """Extracts header data from the parsed document."""
        supplier_repo = SupplierRepository(db)
        liquidation_ok = supplier_repo.use_liquidation(self.provider_id)

        return FranceMessagerieHeader(
            invoice_date=invoice_date,
            gexpex_code=parsed_data.header.get('gexpex_code', ''),
            nim_code=parsed_data.header.get('nim_code', ''),
            invoice_number=parsed_data.header.get('invoice_number', ''),
            currency=parsed_data.header.get('currency', ''),
            transport_type=parsed_data.header.get('transport_type', ''),
            invoice_or_complement=parsed_data.header.get('invoice_or_complement', ''),
            invoice_or_credit_note=parsed_data.header.get('invoice_or_credit_note', ''),
            is_liquidation=liquidation_ok,
        )

    @staticmethod
    def _get_details_data(
        converter: Conversions, parsed_data: dict[str, str], editions_map: dict[str, Edition]
    ) -> FranceMessagerieDetailLine:
        """Extracts detail lines from the parsed document."""

        quantity = converter.to_int(parsed_data['quantity'].strip())

        if quantity is None:
            quantity = 0
        elif quantity < 0:
            quantity = abs(quantity)

        original_invoice = parsed_data.get('original_invoice', '').strip()
        if len(original_invoice) <= 0:
            original_invoice = ''

        net_price = Decimal(parsed_data.get('net_price', 0)) / 10000
        discount = Decimal(parsed_data['discount'].strip()) / 1000
        gross_price = Decimal(parsed_data.get('gross_price', 0)) / 10000
        weight = Decimal(parsed_data.get('weight', 0)) / 10000
        tax = Decimal(parsed_data.get('tax', 0)) / 10000

        amount_with_tax = gross_price * quantity
        amount_without_tax = net_price * quantity
        net_price_with_discount = net_price - (1 - (discount / 100))
        amount_without_tax_with_discount = net_price_with_discount * quantity

        edition = editions_map.get(parsed_data.get('edition', '').strip())

        return FranceMessagerieDetailLine(
            bipad=parsed_data.get('bipad', '').strip(),
            extension=parsed_data.get('extension', '').strip(),
            label=parsed_data.get('label', '').strip(),
            edition=parsed_data.get('edition', '').strip(),
            suffix=parsed_data.get('suffix', '').strip(),
            description=parsed_data.get('description', '').strip(),
            chrono=parsed_data.get('chrono', '').strip(),
            quantity=quantity,
            net_price=net_price,
            original_invoice=original_invoice,
            correction_type=parsed_data.get('correction_type', '').strip(),
            discount=discount,
            weight=weight,
            gross_price=gross_price,
            tax=tax,
            amount_with_tax=amount_with_tax,
            amount_without_tax=amount_without_tax,
            net_price_with_discount=net_price_with_discount,
            amount_without_tax_with_discount=amount_without_tax_with_discount,
        )

    @staticmethod
    def _get_totals_data(converter: Conversions, parsed_data: dict[str, str]) -> FranceMessagerieTotals:
        """Extracts totals data from the parsed document."""
        total_amount_including_tax = converter.to_decimal(
            parsed_data.get('total_amount_including_tax', 0), default=Decimal('0')
        )
        if total_amount_including_tax is not None:
            total_amount_including_tax /= Decimal('10000')
        else:
            total_amount_including_tax = Decimal('0')

        total_amount_excluding_tax = converter.to_decimal(
            parsed_data.get('total_amount_excluding_tax', 0), default=Decimal('0')
        )
        if total_amount_excluding_tax is not None:
            total_amount_excluding_tax /= Decimal('10000')
        else:
            total_amount_excluding_tax = Decimal('0')

        return FranceMessagerieTotals(
            total_amount_including_tax=total_amount_including_tax,
            total_amount_excluding_tax=total_amount_excluding_tax,
        )

    def post_process(self, parsed_data: ParsedDocumentRaw) -> bool:
        """
        Recebe os dados crus (strings) e converte-os para as dataclasses tipadas.
        """
        logger.info(f'[{self.provider_id}] Converting raw data from parser...')

        converter = Conversions()

        with db.get_db() as session:
            try:
                # Instancia o core manager COM a sessão da transação atual
                core_db = DatabaseCoreManager(session)

                str_date = parsed_data.header.get('invoice_date', '')
                invoice_date = converter.convert_to_date(str_date)

                if invoice_date is None:
                    logger.error(f'[{self.provider_id}] Invalid invoice date format: {str_date}')
                    return False

                header = self._get_header_data(core_db, invoice_date, parsed_data)

                details = []
                for raw_detail in parsed_data.details:
                    detail = self._get_details_data(converter, raw_detail)
                    details.append(detail)

                totals = []
                for raw_total in parsed_data.totals:
                    total = self._get_totals_data(converter, raw_total)
                    totals.append(total)

                footer = FranceMessagerieFooter(footer_line=parsed_data.footer.get('footer_line', '').strip())

                invoice = FranceMessagerieInvoice(header=header, details=details, totals=totals, footer=footer)

                # Validar os detalhes
                if not details:
                    logger.error('No details found for invoice.')
                    return False

                if invoice.footer is None:
                    logger.error('Footer is missing!')
                    return False

                if invoice.header is not None and hasattr(invoice.header, 'invoice_number'):
                    logger.info(f'Successfully converted data for invoice {invoice.header.invoice_number}.')
                else:
                    logger.info('Successfully converted data for invoice (invoice number not available).')

                if not self.update_tables(session, invoice):
                    logger.error('Failed to update tables.')
                    return False

                logger.info('Invoice persisted successfully.')

                return True
            except (KeyError, ValueError, TypeError) as e:
                logger.error(f'[{self.provider_id}] Failed to convert data: {e}', exc_info=True)
                return False
            except Exception as e:
                # Se qualquer coisa falhar (uma busca, uma conversão, ou a escrita),
                # o 'with' vai apanhar a exceção e fazer o ROLLBACK da transação inteira.
                logger.error(f'[{self.provider_id}] Failed during post-processing: {e}', exc_info=True)
                return False

    def update_tables(self, session: Session, invoice: FranceMessagerieInvoice) -> bool:
        edition_repository = EditionRepository(session)

        if self.provider.master_data == YesNo.YES:
            edition = edition_repository.get_edition_by_code(invoice.details[0].edition)

        liquidation_ok = invoice.header.is_liquidation if invoice.header else False

        if liquidation_ok:
            # Update the necessary tables for liquidation
            pass

        return True
