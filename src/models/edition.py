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


class Edition(Base, PrimaryKeyMixin, AuditMixin, ArrayColumnMixin):
    __tablename__ = 'ZITMINP'
    __table_args__ = (
        PrimaryKeyConstraint('ROWID', name='ZITMINP_ROWID'),
        Index('ZITMINP_ZINP0', 'ITMREF_0', unique=True),
        Index('ZITMINP_ZINP1', 'CODPUB_0', 'ITMREF_0', unique=True),
        Index('ZITMINP_ZINP2', 'COVDAT_0', 'ITMREF_0', unique=True),
        Index('ZITMINP_ZINP3', 'ITMDES_0', 'ITMREF_0', 'DISDAT_0'),
        {'schema': f'{SCHEMA}'},
    )

    edition: Mapped[str] = mapped_column('ITMREF_0', Unicode(20, 'Latin1_General_BIN2'), default=text("('')"))
    description: Mapped[str] = mapped_column('ITMDES_0', Unicode(70, 'Latin1_General_BIN2'), default=text("('')"))
    reference_status: Mapped[int] = mapped_column('ITMSTA_0', TINYINT, default=text('((1))'))
    status: Mapped[int] = mapped_column('STA_0', TINYINT, default=text('((1))'))
    publication: Mapped[str] = mapped_column('CODPUB_0', Unicode(7, 'Latin1_General_BIN2'), default=text("('')"))
    publication_description: Mapped[str] = mapped_column(
        'DESPUB_0', Unicode(30, 'Latin1_General_BIN2'), default=text("('')")
    )

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
    bipad: Mapped[str] = mapped_column('REFEDI_0', Unicode(15, 'Latin1_General_BIN2'), default=text("('')"))
    edition_number: Mapped[str] = mapped_column('NUMEDI_0', Unicode(15, 'Latin1_General_BIN2'), default=text("('')"))
    suffix: Mapped[str] = mapped_column('SUFEDI_0', Unicode(1, 'Latin1_General_BIN2'), default=text("('')"))
    extension: Mapped[str] = mapped_column('EXTEDI_0', Unicode(2, 'Latin1_General_BIN2'), default=text("('')"))
    label: Mapped[str] = mapped_column('LBLEDI_0', Unicode(2, 'Latin1_General_BIN2'), default=text("('')"))
    nim_code: Mapped[str] = mapped_column('NIMEDI_0', Unicode(2, 'Latin1_General_BIN2'), default=text("('')"))
    chrono: Mapped[str] = mapped_column('CHRONO_0', Unicode(6, 'Latin1_General_BIN2'), default=text("('')"))
    gex_code: Mapped[str] = mapped_column('GEXPEX_0', Unicode(7, 'Latin1_General_BIN2'), default=text("('')"))
    delivery_mode: Mapped[str] = mapped_column('MDLEDI_0', Unicode(3, 'Latin1_General_BIN2'), default=text("('')"))
    expedition_number: Mapped[str] = mapped_column('SHIEDI_0', Unicode(15, 'Latin1_General_BIN2'), default=text("('')"))
    expedition_date: Mapped[datetime.datetime] = mapped_column(
        'SHIDAT_0', DateTime, default=text(f"'{DEFAULT_LEGACY_DATETIME}'")
    )
    isbn: Mapped[str] = mapped_column('ISBN_0', Unicode(20, 'Latin1_General_BIN2'), default=text("('')"))
    cover_date: Mapped[datetime.datetime] = mapped_column(
        'COVDAT_0', DateTime, default=text(f"'{DEFAULT_LEGACY_DATETIME}'")
    )
    planned_date: Mapped[datetime.datetime] = mapped_column(
        'PREDAT_0', DateTime, default=text(f"'{DEFAULT_LEGACY_DATETIME}'")
    )
    distribution_date: Mapped[datetime.datetime] = mapped_column(
        'DISDAT_0', DateTime, default=text(f"'{DEFAULT_LEGACY_DATETIME}'")
    )
    pickup_date: Mapped[datetime.datetime] = mapped_column(
        'PICDAT_0', DateTime, default=text(f"'{DEFAULT_LEGACY_DATETIME}'")
    )
    return_date: Mapped[datetime.datetime] = mapped_column(
        'DEVDAT_0', DateTime, default=text(f"'{DEFAULT_LEGACY_DATETIME}'")
    )
    inp_end_date: Mapped[datetime.datetime] = mapped_column(
        'FACDAT_0', DateTime, default=text(f"'{DEFAULT_LEGACY_DATETIME}'")
    )
    return_week: Mapped[int] = mapped_column('DEVWEEK_0', SmallInteger, default=text('((0))'))
    return_year: Mapped[int] = mapped_column('DEVYEAR_0', SmallInteger, default=text('((0))'))
    distribution_day: Mapped[int] = mapped_column('DIADIS_0', TINYINT, default=text('((0))'))
    shipping_method: Mapped[str] = mapped_column('SHIWAY_0', Unicode(20, 'Latin1_General_BIN2'), default=text("('')"))
    percentage_increase: Mapped[Decimal] = mapped_column('PERMAJ_0', Numeric(10, 3), default=text('((0))'))
    form_of_distribution: Mapped[int] = mapped_column('FORDIS_0', TINYINT, default=text('((0))'))
    expedition_mode: Mapped[str] = mapped_column('MDL_0', Unicode(5, 'Latin1_General_BIN2'), default=text("('')"))
    is_invoiced: Mapped[int] = mapped_column('FLGINV_0', TINYINT, default=text('((1))'))
    is_billable: Mapped[int] = mapped_column('FATFLG_0', TINYINT, default=text('((1))'))
    scrap_destination: Mapped[str] = mapped_column('CODSCR_0', Unicode(20, 'Latin1_General_BIN2'), default=text("('')"))
    quantity_to_storage: Mapped[int] = mapped_column('QTYARM_0', Integer, default=text('((0))'))
    quantity_to_return: Mapped[int] = mapped_column('QTYEDI_0', Integer, default=text('((0))'))
    quantity_to_export: Mapped[int] = mapped_column('QTYEXP_0', Integer, default=text('((0))'))
    quantity_to_special_delivery: Mapped[int] = mapped_column('QTYESP_0', Integer, default=text('((0))'))
    vat_rate: Mapped[Decimal] = mapped_column('CDIVVD_0', Numeric(16, 7), default=text('((0))'))
    is_vasp: Mapped[int] = mapped_column('DISTVSP_0', TINYINT, default=text('((1))'))
    vasp_code: Mapped[str] = mapped_column('CODVSP_0', Unicode(20, 'Latin1_General_BIN2'))
    vasp_description: Mapped[str] = mapped_column('DESVSP_0', Unicode(30, 'Latin1_General_BIN2'))
    is_closed: Mapped[int] = mapped_column('FECEDI_0', TINYINT, default=text('((1))'))
    close_date: Mapped[datetime.datetime] = mapped_column(
        'DATFEC_0', DateTime, default=text(f"'{DEFAULT_LEGACY_DATETIME}'")
    )
    is_vasp_closed: Mapped[int] = mapped_column('FECVSP_0', TINYINT, default=text('((1))'))
    actual_quantity_received: Mapped[int] = mapped_column('QTYRREC_0', Integer, default=text('((0))'))
    actual_quantity_delivered: Mapped[int] = mapped_column('QTYREXP_0', Integer, default=text('((0))'))
    estimated_quantity_delivered: Mapped[int] = mapped_column('QTYEEXP_0', Integer, default=text('((0))'))
    actual_quantity_returned: Mapped[int] = mapped_column('QTYRDEV_0', Integer, default=text('((0))'))
    estimated_quantity_returned: Mapped[int] = mapped_column('QTYEDEV_0', Integer, default=text('((0))'))
    actual_complementary_quantity: Mapped[int] = mapped_column('QTYRFIR_0', Integer, default=text('((0))'))
    estimated_complementary_quantity: Mapped[int] = mapped_column('QTYEFIR_0', Integer, default=text('((0))'))
    nob_received_quantity: Mapped[int] = mapped_column('QTYRNOB_0', Integer, default=text('((0))'))
    nob_returned_quantity: Mapped[int] = mapped_column('QTYDNOB_0', Integer, default=text('((0))'))
    others_quantity: Mapped[int] = mapped_column('QTYOTH_0', Integer, default=text('((0))'))

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='QTYREP',
        property_name='delivery_quantity',
        count=10,
        column_type=Integer,
        python_type=int,
        default=text('((0))'),
    )

    delivery_quantities = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    packing_quantity: Mapped[int] = mapped_column('QTYPAC_0', Integer, default=text('((0))'))
    purchase_quantity: Mapped[int] = mapped_column('QTYPOH_0', Integer, default=text('((0))'))
    reception_difference: Mapped[int] = mapped_column('QTYRDIF_0', Integer, default=text('((0))'))

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='QTYPIH',
        property_name='invoice_quantity',
        count=2,
        column_type=Integer,
        python_type=int,
        default=text('((0))'),
    )

    invoice_quantities = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    receipted_quantity: Mapped[int] = mapped_column('QTYLENT_0', Integer, default=text('((0))'))
    returned_quantity: Mapped[int] = mapped_column('QTYLDEV_0', Integer, default=text('((0))'))
    returned_percentage: Mapped[Decimal] = mapped_column('PERDEV_0', Numeric(10, 3), default=text('((0))'))
    madeira_price: Mapped[Decimal] = mapped_column('PRIMAD_0', Numeric(14, 3), default=text('((0))'))
    supplier_discount: Mapped[Decimal] = mapped_column('DSCBPS_0', Numeric(10, 3), default=text('((0))'))
    agent_discount: Mapped[Decimal] = mapped_column('DSCAGE_0', Numeric(10, 3), default=text('((0))'))
    vasp_discount: Mapped[Decimal] = mapped_column('DSCVSP_0', Numeric(10, 3), default=text('((0))'))
    nob_discount: Mapped[Decimal] = mapped_column('DSCNOB_0', Numeric(10, 3), default=text('((0))'))
    weight: Mapped[Decimal] = mapped_column('ITMWEI_0', Numeric(13, 4), default=text('((0))'))
    packing: Mapped[str] = mapped_column('PCK_0', Unicode(5, 'Latin1_General_BIN2'), default=text("('')"))
    packing_capacity: Mapped[int] = mapped_column('PCKCAP_0', SmallInteger, default=text('((0))'))
    notes: Mapped[str] = mapped_column('NOTAS_0', Unicode(250, 'Latin1_General_BIN2'), default=text("('')"))
    sent_to_vasp: Mapped[int] = mapped_column('FLGENV_0', TINYINT, default=text('((0))'))
    sent_to_smartwatt: Mapped[int] = mapped_column('FLGSMW_0', TINYINT, default=text('((0))'))
    date_to_sent_smartwatt: Mapped[datetime.datetime] = mapped_column(
        'DATSMW_0', DateTime, default=text(f"'{DEFAULT_LEGACY_DATETIME}'")
    )
    user_to_sent_smartwatt: Mapped[str] = mapped_column(
        'USRSMW_0', Unicode(5, 'Latin1_General_BIN2'), default=text("('')")
    )
    category: Mapped[str] = mapped_column('TCLCOD_0', Unicode(5, 'Latin1_General_BIN2'), default=text("('')"))
    receipt_number: Mapped[str] = mapped_column('RCPNUM_0', Unicode(20, 'Latin1_General_BIN2'), default=text("('')"))
    receipt_date: Mapped[datetime.datetime] = mapped_column(
        'RCPDAT_0', DateTime, default=text(f"'{DEFAULT_LEGACY_DATETIME}'")
    )
    manager: Mapped[str] = mapped_column('PUBGES_0', Unicode(15, 'Latin1_General_BIN2'), default=text("('')"))
    analyst: Mapped[str] = mapped_column('PUBANA_0', Unicode(15, 'Latin1_General_BIN2'), default=text("('')"))
    last_date_return: Mapped[datetime.datetime] = mapped_column(
        'DATRET_0', DateTime, default=text(f"'{DEFAULT_LEGACY_DATETIME}'")
    )
    return_quantity: Mapped[int] = mapped_column('BPSRET_0', Integer, default=text('((0))'))
    is_returnable_by_edi: Mapped[int] = mapped_column('RETFLG_0', TINYINT, default=text('((0))'))
    purchase_flag: Mapped[int] = mapped_column('PURFLG_0', TINYINT, default=text('((0))'))
    invoiced_nob: Mapped[int] = mapped_column('INVNOB_0', TINYINT, default=text('((0))'))
    distribution_debit: Mapped[Decimal] = mapped_column('DEBDIS_0', Numeric(14, 3), default=text('((0))'))
    return_debit: Mapped[Decimal] = mapped_column('DEBDEV_0', Numeric(14, 3), default=text('((0))'))
    user_correction: Mapped[str] = mapped_column('CORUSR_0', Unicode(5, 'Latin1_General_BIN2'), default=text("('')"))
    correction_date: Mapped[datetime.datetime] = mapped_column(
        'CORDAT_0', DateTime, default=text(f"'{DEFAULT_LEGACY_DATETIME}'")
    )
    creation_date: Mapped[datetime.datetime] = mapped_column(
        'CREDAT_0', DateTime, default=text(f"'{DEFAULT_LEGACY_DATETIME}'")
    )
