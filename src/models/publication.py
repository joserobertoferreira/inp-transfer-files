from decimal import Decimal

from sqlalchemy import (
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

from src.config.settings import SCHEMA
from src.database.base import Base
from src.models.generics_mixins import ArrayColumnMixin
from src.models.mixins import AuditMixin, PrimaryKeyMixin


class Publication(Base, PrimaryKeyMixin, AuditMixin, ArrayColumnMixin):
    __tablename__ = 'ZPUBLIC'
    __table_args__ = (
        PrimaryKeyConstraint('ROWID', name='ZPUBLIC_ROWID'),
        Index('ZPUBLIC_ZPUB0', 'CODPUB_0', unique=True),
        {'schema': f'{SCHEMA}'},
    )

    code: Mapped[str] = mapped_column('CODPUB_0', Unicode(7, 'Latin1_General_BIN2'), default=text("('')"))
    description: Mapped[str] = mapped_column('DESPUB_0', Unicode(30, 'Latin1_General_BIN2'), default=text("('')"))
    short_description: Mapped[str] = mapped_column('DESSHO_0', Unicode(10, 'Latin1_General_BIN2'), default=text("('')"))
    counter: Mapped[str] = mapped_column('PUBCOU_0', Unicode(5, 'Latin1_General_BIN2'), default=text("('')"))
    is_active: Mapped[int] = mapped_column('ZPUBSTA_0', TINYINT, default=text('((2))'))
    status: Mapped[int] = mapped_column('PUBSTA_0', TINYINT, default=text('((1))'))
    category: Mapped[str] = mapped_column('TCLCOD_0', Unicode(5, 'Latin1_General_BIN2'), default=text("('')"))
    product_line: Mapped[str] = mapped_column('CFGLIN_0', Unicode(5, 'Latin1_General_BIN2'), default=text("('')"))

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='BPSNUM',
        property_name='supplier',
        count=2,
        column_type=Unicode,
        column_args=(15, 'Latin1_General_BIN2'),
        python_type=str,
        default=text("''"),
    )

    suppliers = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    editor: Mapped[str] = mapped_column('BPSEDI_0', Unicode(15, 'Latin1_General_BIN2'), default=text("('')"))
    supplier_reference: Mapped[str] = mapped_column(
        'BPSREF_0', Unicode(15, 'Latin1_General_BIN2'), default=text("('')")
    )

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='TSICOD',
        property_name='statistical_code',
        count=5,
        column_type=Unicode,
        column_args=(20, 'Latin1_General_BIN2'),
        python_type=str,
        default=text("''"),
    )

    statistical_codes = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='CRY',
        property_name='country',
        count=2,
        column_type=Unicode,
        column_args=(3, 'Latin1_General_BIN2'),
        python_type=str,
        default=text("''"),
    )

    countries = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    language: Mapped[str] = mapped_column('LAN_0', Unicode(5, 'Latin1_General_BIN2'), default=text("('')"))
    periodic_code: Mapped[str] = mapped_column('CODPER_0', Unicode(20, 'Latin1_General_BIN2'), default=text("('')"))
    periodicity: Mapped[int] = mapped_column('PERNUM_0', TINYINT, default=text('((1))'))
    time_for_sale: Mapped[int] = mapped_column('TIMSAL_0', Integer, default=text('((0))'))
    shipping_method: Mapped[str] = mapped_column('SHIWAY_0', Unicode(20, 'Latin1_General_BIN2'), default=text("('')"))
    percentage_increase: Mapped[Decimal] = mapped_column('PERMAJ_0', Numeric(10, 3), default=text('((0))'))
    form_of_distribution: Mapped[int] = mapped_column('FORDIS_0', TINYINT, default=text('((0))'))
    company: Mapped[str] = mapped_column('CPY_0', Unicode(5, 'Latin1_General_BIN2'), default=text("('')"))

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='PURBASPRI',
        property_name='standard_price',
        count=7,
        column_type=Numeric,
        column_args=(18, 5),
        python_type=Decimal,
        default=text('((0))'),
    )

    standard_prices = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='BASPRI',
        property_name='base_price',
        count=7,
        column_type=Numeric,
        column_args=(14, 3),
        python_type=Decimal,
        default=text('((0))'),
    )

    base_prices = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    purchase_price: Mapped[Decimal] = mapped_column('PURPRI_0', Numeric(14, 3), default=text('((0))'))
    default_price: Mapped[Decimal] = mapped_column('PRICE', Numeric(14, 3), default=text('((0))'))
    tax_level: Mapped[str] = mapped_column('VACITM_0', Unicode(5, 'Latin1_General_BIN2'), default=text("('')"))
    supplier_discount: Mapped[Decimal] = mapped_column('DSCBPS_0', Numeric(10, 3), default=text('((0))'))
    agent_discount: Mapped[Decimal] = mapped_column('DSCAGE_0', Numeric(10, 3), default=text('((0))'))
    vasp_discount: Mapped[Decimal] = mapped_column('DSCVSP_0', Numeric(10, 3), default=text('((0))'))
    nob_discount: Mapped[Decimal] = mapped_column('DSCNOB_0', Numeric(10, 3), default=text('((0))'))
    returned_percentage: Mapped[Decimal] = mapped_column('PERDEV_0', Numeric(10, 3), default=text('((0))'))
    vasp_code: Mapped[str] = mapped_column('PUBVSP_0', Unicode(15, 'Latin1_General_BIN2'), default=text("('')"))

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='PUBDAY',
        property_name='week_day',
        count=7,
        column_type=TINYINT,
        python_type=int,
        default=text('((0))'),
    )

    week_days = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    is_holiday: Mapped[int] = mapped_column('HOLIDAY_0', TINYINT, default=text('((1))'))
    isbn: Mapped[str] = mapped_column('ISBN_0', Unicode(20, 'Latin1_General_BIN2'), default=text("('')"))

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='EANCOD',
        property_name='ean_code',
        count=7,
        column_type=Unicode,
        column_args=(20, 'Latin1_General_BIN2'),
        python_type=str,
        default=text("('')"),
    )

    ean_codes = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    vat_rate: Mapped[Decimal] = mapped_column('CDIVVD_0', Numeric(16, 7), default=text('((0))'))
    sent_to_vasp: Mapped[int] = mapped_column('FLGENV_0', TINYINT, default=text('((1))'))
    is_product: Mapped[int] = mapped_column('ITMFLG_0', TINYINT, default=text('((1))'))
    customs_reference: Mapped[str] = mapped_column('CUSREF_0', Unicode(12, 'Latin1_General_BIN2'), default=text("('')"))
    scrap_destination: Mapped[str] = mapped_column('CODSCR_0', Unicode(20, 'Latin1_General_BIN2'), default=text("('')"))
    quantity_to_storage: Mapped[int] = mapped_column('QTYARM_0', Integer, default=text('((0))'))
    quantity_to_return: Mapped[int] = mapped_column('QTYEDI_0', Integer, default=text('((0))'))
    quantity_to_export: Mapped[int] = mapped_column('QTYEXP_0', Integer, default=text('((0))'))
    quantity_to_special_delivery: Mapped[int] = mapped_column('QTYESP_0', Integer, default=text('((0))'))
    is_vasp: Mapped[int] = mapped_column('DISTVSP_0', TINYINT, default=text('((1))'))
    delivery_mode: Mapped[str] = mapped_column('MDL_0', Unicode(5, 'Latin1_General_BIN2'), default=text("('')"))
    default_bipad: Mapped[str] = mapped_column('REFEDI_0', Unicode(15, 'Latin1_General_BIN2'), default=text("('')"))
    extension: Mapped[str] = mapped_column('EXTEDI_0', Unicode(2, 'Latin1_General_BIN2'), default=text("('')"))

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='BIPAD',
        property_name='bipad',
        count=7,
        column_type=Unicode,
        column_args=(15, 'Latin1_General_BIN2'),
        python_type=str,
        default=text("('')"),
    )

    bipads = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='BIPEXT',
        property_name='bipad_ext',
        count=7,
        column_type=Unicode,
        column_args=(3, 'Latin1_General_BIN2'),
        python_type=str,
        default=text("('')"),
    )

    bipad_extension = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='BIPDEF',
        property_name='bipad_def',
        count=7,
        column_type=TINYINT,
        python_type=int,
        default=text('((1))'),
    )

    is_default_bipad = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='POLO',
        property_name='hub',
        count=10,
        column_type=TINYINT,
        python_type=int,
        default=text('((0))'),
    )

    hubs = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    manager: Mapped[str] = mapped_column('PUBGES_0', Unicode(15, 'Latin1_General_BIN2'), default=text("('')"))
    analyst: Mapped[str] = mapped_column('PUBANA_0', Unicode(15, 'Latin1_General_BIN2'), default=text("('')"))
    is_billable: Mapped[int] = mapped_column('FATFLG_0', TINYINT, default=text('((1))'))
    notes: Mapped[str] = mapped_column('NOTAS_0', Unicode(250, 'Latin1_General_BIN2'), default=text("('')"))
    packing: Mapped[str] = mapped_column('PCK_0', Unicode(5, 'Latin1_General_BIN2'), default=text("('')"))
    packing_capacity: Mapped[int] = mapped_column('PCKCAP_0', SmallInteger, default=text('((0))'))
    is_returnable_by_edi: Mapped[int] = mapped_column('RETFLG_0', TINYINT, default=text('((0))'))
    is_nob_deliverable: Mapped[int] = mapped_column('DLVFLG_0', TINYINT, default=text('((0))'))
    distribution_debit: Mapped[Decimal] = mapped_column('DEBDIS_0', Numeric(14, 3), default=text('((0))'))
    return_debit: Mapped[Decimal] = mapped_column('DEBDEV_0', Numeric(14, 3), default=text('((0))'))
