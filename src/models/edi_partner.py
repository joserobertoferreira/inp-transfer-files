import datetime
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    Index,
    Numeric,
    PrimaryKeyConstraint,
    SmallInteger,
    Unicode,
    text,
)
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column

from src.config.settings import DEFAULT_LEGACY_DATETIME, SCHEMA, STANDARD_FOLDER
from src.database.base import Base
from src.models.generics_mixins import ArrayColumnMixin
from src.models.mixins import AuditMixin, PrimaryKeyMixin


class EdiPartner(Base, PrimaryKeyMixin, AuditMixin, ArrayColumnMixin):
    __tablename__ = 'ZEDIPAR'
    __table_args__ = (
        PrimaryKeyConstraint('ROWID', name='ZEDIPAR_ROWID'),
        Index('ZEDIPAR_ZECP0', 'BPRNUM_0', unique=True),
        {'schema': f'{SCHEMA}'},
    )

    provider: Mapped[str] = mapped_column('BPRNUM_0', Unicode(15, 'Latin1_General_BIN2'), default=text("''"))
    provider_name: Mapped[str] = mapped_column('BPRNAM_0', Unicode(35, 'Latin1_General_BIN2'), default=text("''"))
    is_active: Mapped[int] = mapped_column('ENAFLG_0', TINYINT, default=text('((2))'))
    provider_id: Mapped[int] = mapped_column('BPRID_0', SmallInteger, default=text('((0))'))
    use_ftp: Mapped[int] = mapped_column('FTPFLG_0', TINYINT, default=text('((1))'))
    protocol: Mapped[int] = mapped_column('FTPTYP_0', TINYINT, default=text('((1))'))
    url: Mapped[str] = mapped_column('FTPURL_0', Unicode(80, 'Latin1_General_BIN2'), default=text("''"))
    username: Mapped[str] = mapped_column('FTPUSR_0', Unicode(15, 'Latin1_General_BIN2'), default=text("''"))
    password: Mapped[str] = mapped_column('FTPPSW_0', Unicode(50, 'Latin1_General_BIN2'), default=text("''"))
    binary_mode: Mapped[int] = mapped_column('FTPMOD_0', TINYINT, default=text('((1))'))
    remote_input_folder: Mapped[str] = mapped_column('FTPINP_0', Unicode(30, 'Latin1_General_BIN2'), default=text("''"))
    remote_output_folder: Mapped[str] = mapped_column(
        'FTPOUT_0', Unicode(30, 'Latin1_General_BIN2'), default=text("''")
    )
    formula: Mapped[str] = mapped_column('FTPFOR_0', Unicode(150, 'Latin1_General_BIN2'), default=text("''"))
    x3_script: Mapped[str] = mapped_column('FTPTRT_0', Unicode(30, 'Latin1_General_BIN2'), default=text("''"))
    private_key_folder: Mapped[str] = mapped_column('FTPFIC_0', Unicode(150, 'Latin1_General_BIN2'), default=text("''"))
    export_process: Mapped[int] = mapped_column('FTPEXP_0', TINYINT, default=text('((1))'))
    one_execution: Mapped[int] = mapped_column('FTPUNI_0', TINYINT, default=text('((1))'))
    process_frequency: Mapped[int] = mapped_column('FTPFRQ_0', TINYINT, default=text('((0))'))

    _local_input_folder: Mapped[str] = mapped_column(
        'DRTINP_0', Unicode(120, 'Latin1_General_BIN2'), default=text("''")
    )
    local_input_extension: Mapped[str] = mapped_column(
        'EXTINP_0', Unicode(5, 'Latin1_General_BIN2'), default=text("''")
    )
    _local_output_folder: Mapped[str] = mapped_column(
        'DRTOUT_0', Unicode(120, 'Latin1_General_BIN2'), default=text("''")
    )
    local_output_extension: Mapped[str] = mapped_column(
        'EXTOUT_0', Unicode(5, 'Latin1_General_BIN2'), default=text("''")
    )
    file_extension: Mapped[str] = mapped_column('FICEXT_0', Unicode(5, 'Latin1_General_BIN2'), default=text("''"))
    file_separator: Mapped[str] = mapped_column('FICSEP_0', Unicode(1, 'Latin1_General_BIN2'), default=text("''"))

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='FICFLG',
        property_name='active_file',
        count=10,
        column_type=TINYINT,
        python_type=int,
        default=text('((1))'),
    )

    active_files = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='FICPRE',
        property_name='prefix_file',
        count=10,
        column_type=Unicode,
        column_args=(3, 'Latin1_General_BIN2'),
        python_type=str,
        default=text("''"),
    )

    prefix_files = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='FICCOU',
        property_name='counter_file',
        count=10,
        column_type=Unicode,
        column_args=(5, 'Latin1_General_BIN2'),
        python_type=str,
        default=text("''"),
    )

    counter_files = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='FICDES',
        property_name='description_file',
        count=10,
        column_type=Unicode,
        column_args=(30, 'Latin1_General_BIN2'),
        python_type=str,
        default=text("''"),
    )

    description_files = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='FICPRO',
        property_name='process_file',
        count=10,
        column_type=TINYINT,
        python_type=int,
        default=text('((1))'),
    )

    process_files = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='FICDIR',
        property_name='direction_file',
        count=10,
        column_type=TINYINT,
        python_type=int,
        default=text('((1))'),
    )

    direction_files = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='FICDAT',
        property_name='update_file',
        count=10,
        column_type=DateTime,
        python_type=datetime.datetime,
        default=text(f"'{DEFAULT_LEGACY_DATETIME}'"),
    )

    update_files = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='FICDEL',
        property_name='delete_file',
        count=10,
        column_type=TINYINT,
        python_type=int,
        default=text('((1))'),
    )

    delete_files = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='FICFOR',
        property_name='formula_file',
        count=10,
        column_type=Unicode,
        column_args=(150, 'Latin1_General_BIN2'),
        python_type=str,
        default=text("''"),
    )

    formula_files = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='FICNUM',
        property_name='number_file',
        count=10,
        column_type=Unicode,
        column_args=(5, 'Latin1_General_BIN2'),
        python_type=str,
        default=text("''"),
    )

    number_files = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='PEREDI',
        property_name='editor_period',
        count=10,
        column_type=Unicode,
        column_args=(3, 'Latin1_General_BIN2'),
        python_type=str,
        default=text("''"),
    )

    editor_periods = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='PERIODI',
        property_name='edition_period',
        count=10,
        column_type=Unicode,
        column_args=(20, 'Latin1_General_BIN2'),
        python_type=str,
        default=text("''"),
    )

    edition_periods = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='MDL',
        property_name='delivery_mode',
        count=5,
        column_type=Unicode,
        column_args=(5, 'Latin1_General_BIN2'),
        python_type=str,
        default=text("''"),
    )

    delivery_modes = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='MDLTIM',
        property_name='delivery_date',
        count=5,
        column_type=SmallInteger,
        python_type=int,
        default=text('((0))'),
    )

    delivery_dates = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    manager: Mapped[str] = mapped_column('PUBGES_0', Unicode(15, 'Latin1_General_BIN2'), default=text("''"))
    analyst: Mapped[str] = mapped_column('PUBANA_0', Unicode(15, 'Latin1_General_BIN2'), default=text("''"))
    master_data: Mapped[int] = mapped_column('FLGBAS_0', TINYINT, default=text('((1))'))
    translate_quantity: Mapped[int] = mapped_column('FLGQTY_0', TINYINT, default=text('((1))'))
    generate_edition_number: Mapped[int] = mapped_column('FLGNUM_0', TINYINT, default=text('((1))'))
    excel: Mapped[int] = mapped_column('FLGXLS_0', TINYINT, default=text('((1))'))
    packing_list: Mapped[int] = mapped_column('FLGPAC_0', TINYINT, default=text('((1))'))
    is_colored: Mapped[int] = mapped_column('COLOR_0', TINYINT, default=text('((1))'))
    supplier_discount: Mapped[Decimal] = mapped_column('DSCBPS_0', Numeric(10, 3), default=text('((0))'))

    @property
    def local_input_folder(self) -> str:
        """
        Retorna o caminho de input local completo, substituindo [EDI]
        pelo caminho base definido nas configurações.
        """
        if not self._local_input_folder:
            return ''
        # Usamos o .replace() para substituir o placeholder
        return self._local_input_folder.replace('[EDI]', STANDARD_FOLDER)

    @property
    def local_output_folder(self) -> str:
        """
        Retorna o caminho de output local completo, substituindo [EDI]
        pelo caminho base definido nas configurações.
        """
        if not self._local_output_folder:
            return ''
        return self._local_output_folder.replace('[EDI]', STANDARD_FOLDER)
