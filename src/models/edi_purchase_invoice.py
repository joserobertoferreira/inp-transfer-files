import datetime
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    Index,
    Integer,
    Numeric,
    PrimaryKeyConstraint,
    SmallInteger,
    Unicode,
    text,
)
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column

from src.config.settings import DEFAULT_LEGACY_DATETIME, SCHEMA
from src.database.base import Base
from src.models.generics_mixins import ArrayColumnMixin
from src.models.mixins import AuditMixin, PrimaryKeyMixin


class PurchaseInvoiceHeader(Base, PrimaryKeyMixin, AuditMixin, ArrayColumnMixin):
    __tablename__ = 'ZPINVOICEV'
    __table_args__ = (
        PrimaryKeyConstraint('ROWID', name='ZPINVOICEV_ROWID'),
        Index('ZPINVOICEV_ZPIV0', 'NUM_0', unique=True),
        Index('ZPINVOICEV_ZPIV1', 'BPR_0', 'BPRVCR_0'),
        {'schema': f'{SCHEMA}'},
    )

    invoice_number: Mapped[str] = mapped_column('NUM_0', Unicode(20, 'Latin1_General_BIN2'), default=text("''"))
    invoice_type: Mapped[str] = mapped_column('PIVTYP_0', Unicode(5, 'Latin1_General_BIN2'), default=text("''"))
    category: Mapped[int] = mapped_column('PIHTYP_0', TINYINT, default=text('((1))'))
    supplier: Mapped[str] = mapped_column('BPR_0', Unicode(15, 'Latin1_General_BIN2'), default=text("''"))
    supplier_invoice_number: Mapped[str] = mapped_column(
        'BPRVCR_0', Unicode(20, 'Latin1_General_BIN2'), default=text("''")
    )
    document_lines: Mapped[int] = mapped_column('LINNBR_0', SmallInteger, default=text('((0))'))
    accounting_date: Mapped[datetime.datetime] = mapped_column(
        'ACCDAT_0', DateTime, default=text(f"'{DEFAULT_LEGACY_DATETIME}'")
    )
    supplier_invoice_date: Mapped[datetime.datetime] = mapped_column(
        'BPRDAT_0', DateTime, default=text(f"'{DEFAULT_LEGACY_DATETIME}'")
    )
    due_date: Mapped[datetime.datetime] = mapped_column(
        'DUDDAT_0', DateTime, default=text(f"'{DEFAULT_LEGACY_DATETIME}'")
    )
    gex_code: Mapped[str] = mapped_column('GEXPEX_0', Unicode(7, 'Latin1_General_BIN2'), default=text("''"))
    filename: Mapped[str] = mapped_column('FICNAM_0', Unicode(60, 'Latin1_General_BIN2'), default=text("''"))
    status: Mapped[int] = mapped_column('STA_0', TINYINT, default=text('((1))'))
    currency: Mapped[str] = mapped_column('CUR_0', Unicode(3, 'Latin1_General_BIN2'), default=text("''"))
    amount_excluding_tax: Mapped[Decimal] = mapped_column('AMTNOT_0', Numeric(27, 13), default=text('((0))'))
    amount_including_tax: Mapped[Decimal] = mapped_column('AMTATI_0', Numeric(27, 13), default=text('((0))'))
    quantity: Mapped[int] = mapped_column('QTY_0', Integer, default=text('((0))'))
    delivery_mode: Mapped[str] = mapped_column('MDLEDI_0', Unicode(3, 'Latin1_General_BIN2'), default=text("''"))
    edi_invoice_type: Mapped[str] = mapped_column('INVTYP_0', Unicode(1, 'Latin1_General_BIN2'), default=text("''"))

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='PIHNUM',
        property_name='purchase_invoice',
        count=4,
        column_type=Unicode,
        column_args=(20, 'Latin1_General_BIN2'),
        python_type=str,
        default=text("''"),
    )

    purchase_invoices = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='PIHTYPE',
        property_name='purchase_type',
        count=4,
        column_type=TINYINT,
        python_type=int,
        default=text('((1))'),
    )

    purchase_types = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='PIHDAT',
        property_name='purchase_date',
        count=4,
        column_type=DateTime,
        python_type=datetime.datetime,
        default=text(f"'{DEFAULT_LEGACY_DATETIME}'"),
    )

    purchase_dates = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    liquidation_number: Mapped[str] = mapped_column('LQDNUM_0', Unicode(20, 'Latin1_General_BIN2'))


class PurchaseInvoiceLines(Base, PrimaryKeyMixin, AuditMixin):
    __tablename__ = 'ZPINVOICED'
    __table_args__ = (
        PrimaryKeyConstraint('ROWID', name='ZPINVOICED_ROWID'),
        Index('ZPINVOICED_ZPID0', 'NUM_0', 'PIDLIN_0', unique=True),
        {'schema': f'{SCHEMA}'},
    )

    invoice_number: Mapped[str] = mapped_column('NUM_0', Unicode(20, 'Latin1_General_BIN2'), default=text("''"))
    line_number: Mapped[int] = mapped_column('PIDLIN_0', Integer, default=text('((0))'))
    invoice_type: Mapped[str] = mapped_column('PIVTYP_0', Unicode(5, 'Latin1_General_BIN2'), default=text("''"))
    supplier: Mapped[str] = mapped_column('BPR_0', Unicode(15, 'Latin1_General_BIN2'), default=text("''"))
    category: Mapped[int] = mapped_column('PIHTYP_0', TINYINT, default=text('((1))'))
    document_type: Mapped[int] = mapped_column('LCTTYP_0', TINYINT, default=text('((1))'))
    publication: Mapped[str] = mapped_column('CODPUB_0', Unicode(7, 'Latin1_General_BIN2'), default=text("''"))
    edition: Mapped[str] = mapped_column('ITMREF_0', Unicode(20, 'Latin1_General_BIN2'), default=text("''"))
    description: Mapped[str] = mapped_column('ITMDES_0', Unicode(70, 'Latin1_General_BIN2'), default=text("''"))
    bipad: Mapped[str] = mapped_column('REFEDI_0', Unicode(15, 'Latin1_General_BIN2'), default=text("''"))
    edition_number: Mapped[str] = mapped_column('NUMEDI_0', Unicode(15, 'Latin1_General_BIN2'), default=text("''"))
    suffix: Mapped[str] = mapped_column('SUFEDI_0', Unicode(1, 'Latin1_General_BIN2'), default=text("''"))
    extension: Mapped[str] = mapped_column('EXTEDI_0', Unicode(2, 'Latin1_General_BIN2'), default=text("''"))
    label: Mapped[str] = mapped_column('LBLEDI_0', Unicode(2, 'Latin1_General_BIN2'), default=text("''"))
    nim_code: Mapped[str] = mapped_column('NIMEDI_0', Unicode(2, 'Latin1_General_BIN2'), default=text("''"))
    chrono: Mapped[str] = mapped_column('CHRONO_0', Unicode(6, 'Latin1_General_BIN2'), default=text("''"))
    quantity: Mapped[int] = mapped_column('QTY_0', Integer, default=text('((0))'))
    gross_price: Mapped[Decimal] = mapped_column('GROPRI_0', Numeric(19, 5), default=text('((0))'))
    net_price: Mapped[Decimal] = mapped_column('NETPRI_0', Numeric(19, 5), default=text('((0))'))
    original_net_price: Mapped[Decimal] = mapped_column('ORINETPRI_0', Numeric(19, 5), default=text('((0))'))
    discount_value_1: Mapped[Decimal] = mapped_column('DISCRGVAL1_0', Numeric(19, 5), default=text('((0))'))
    amount_excluding_tax: Mapped[Decimal] = mapped_column('AMTNOTLIN_0', Numeric(15, 3), default=text('((0))'))
    amount_including_tax: Mapped[Decimal] = mapped_column('AMTATILIN_0', Numeric(15, 3), default=text('((0))'))
    tax: Mapped[Decimal] = mapped_column('RATVAT_0', Numeric(8, 3), default=text('((0))'))
    weight: Mapped[Decimal] = mapped_column('ITMWEI_0', Numeric(13, 4), default=text('((0))'))
    original_invoice: Mapped[str] = mapped_column('ORIFAC_0', Unicode(20, 'Latin1_General_BIN2'), default=text("''"))
    correction_type: Mapped[str] = mapped_column('TYPFIX_0', Unicode(1, 'Latin1_General_BIN2'), default=text("''"))
    is_manual: Mapped[int] = mapped_column('MANFLG_0', SmallInteger, default=text('((0))'))
    liquidation_number: Mapped[str] = mapped_column('LQDNUM_0', Unicode(20, 'Latin1_General_BIN2'), default=text("''"))
    liquidation_line: Mapped[int] = mapped_column('LQDLIN_0', Integer, default=text('((0))'))
