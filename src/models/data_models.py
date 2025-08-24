from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Optional

from src.models.edition import Edition
from src.utils.local_menus import ImportExport


@dataclass
class TransferTask:
    """Representa uma única tarefa de transferência definida pelos arrays."""

    delete: bool
    direction: ImportExport
    index: int
    is_active: bool
    prefix: str = field(default='')
    filename: str = field(default='')


@dataclass
class FranceMessagerieHeader:
    """Representa o cabeçalho do ficheiro da France Messagerie."""

    invoice_date: date
    gexpex_code: str
    nim_code: str
    invoice_number: str
    currency: str
    transport_type: str
    invoice_or_complement: str
    invoice_or_credit_note: str
    is_liquidation: bool


@dataclass
class FranceMessagerieDetailLine:
    """Representa uma linha de detalhe do ficheiro da France Messagerie."""

    bipad: str
    extension: str
    label: str
    edition: str
    suffix: str
    description: str
    chrono: str
    quantity: int
    net_price: Decimal
    original_invoice: str
    correction_type: str
    discount: Decimal
    weight: Decimal
    gross_price: Decimal
    tax: Decimal
    amount_with_tax: Decimal
    amount_without_tax: Decimal
    net_price_with_discount: Decimal
    amount_without_tax_with_discount: Decimal
    edition_object: Optional['Edition'] = None
    action: str = field(default='ignore')  # e.g., 'insert', 'update', 'delete'


@dataclass
class FranceMessagerieTotals:
    """Representa os totais do ficheiro da France Messagerie."""

    total_amount_including_tax: Decimal
    total_amount_excluding_tax: Decimal


@dataclass
class FranceMessagerieFooter:
    """Representa o rodapé do ficheiro da France Messagerie."""

    footer_line: str


@dataclass
class FranceMessagerieInvoice:
    """Estrutura para guardar os dados extraídos de um ficheiro completo."""

    header: Optional[FranceMessagerieHeader] = None
    details: list[FranceMessagerieDetailLine] = field(default_factory=list)
    totals: list[FranceMessagerieTotals] = field(default_factory=list)
    footer: Optional[FranceMessagerieFooter] = None


@dataclass
class EditorParameters:
    """Representa os parâmetros de busca de uma edição com os dados do editor."""

    bipad: str
    edition_number: str
    suffix: str
    provider_id: str
    description: str
    cover_date: date
