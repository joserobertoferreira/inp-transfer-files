from decimal import Decimal

from sqlalchemy import (
    Index,
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
from src.models.mixins import AuditMixin, CreateUpdateDateMixin, PrimaryKeyMixin


class CodeNumbers(Base, PrimaryKeyMixin, CreateUpdateDateMixin, AuditMixin, ArrayColumnMixin):
    __tablename__ = 'ACODNUM'
    __table_args__ = (
        PrimaryKeyConstraint('ROWID', name='ACODNUM_ROWID'),
        Index('ACODNUM_ANM0', 'CODNUM_0', unique=True),
        {'schema': f'{SCHEMA}'},
    )

    code_number: Mapped[str] = mapped_column('CODNUM_0', Unicode(5, 'Latin1_General_BIN2'), default=text("''"))
    length: Mapped[int] = mapped_column('LNG_0', SmallInteger, default=text('((0))'))
    definition_level: Mapped[int] = mapped_column('NIVDEF_0', TINYINT, default=text('((0))'))
    rtz_level: Mapped[int] = mapped_column('NIVRAZ_0', TINYINT, default=text('((0))'))
    type: Mapped[int] = mapped_column('TYP_0', TINYINT, default=text('((0))'))
    number_of_components: Mapped[int] = mapped_column('NBPOS_0', SmallInteger, default=text('((0))'))

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='POSTYP',
        property_name='component_type',
        count=10,
        column_type=TINYINT,
        python_type=int,
        default=text('((1))'),
    )

    components_type = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='POSLNG',
        property_name='component_length',
        count=10,
        column_type=SmallInteger,
        python_type=int,
        default=text('((1))'),
    )

    components_length = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='POSCTE',
        property_name='constant',
        count=10,
        column_type=Unicode,
        column_args=(80, 'Latin1_General_BIN2'),
        python_type=str,
        default=text("''"),
    )

    constants = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    chrono_control: Mapped[int] = mapped_column('CTLCHR_0', TINYINT, default=text('((0))'))
    reset_to_zero: Mapped[int] = mapped_column('ZERO_0', TINYINT, default=text('((0))'))
    sequence: Mapped[int] = mapped_column('SEQ_0', TINYINT, default=text('((0))'))
    table: Mapped[str] = mapped_column('SEQTBL_0', Unicode(12, 'Latin1_General_BIN2'), default=text("''"))
    abbreviation: Mapped[str] = mapped_column('SEQABR_0', Unicode(8, 'Latin1_General_BIN2'), default=text("''"))
    numerals: Mapped[int] = mapped_column('SEQNBR_0', SmallInteger, default=text('((0))'))
    legislation: Mapped[str] = mapped_column('LEG_0', Unicode(20, 'Latin1_General_BIN2'), default=text("''"))


class SequenceNumbers(Base, PrimaryKeyMixin, AuditMixin):
    __tablename__ = 'AVALNUM'
    __table_args__ = (
        PrimaryKeyConstraint('ROWID', name='AVALNUM_ROWID'),
        Index('AVALNUM_AVN0', 'CODNUM_0', 'SITE_0', 'PERIODE_0', 'COMP_0', unique=True),
        {'schema': f'{SCHEMA}'},
    )

    code_number: Mapped[str] = mapped_column('CODNUM_0', Unicode(5, 'Latin1_General_BIN2'), default=text("''"))
    site: Mapped[str] = mapped_column('SITE_0', Unicode(5, 'Latin1_General_BIN2'), default=text("''"))
    period: Mapped[int] = mapped_column('PERIODE_0', SmallInteger, default=text('((0))'))
    complement: Mapped[str] = mapped_column('COMP_0', Unicode(25, 'Latin1_General_BIN2'), default=text("''"))
    sequence_number: Mapped[Decimal] = mapped_column('VALEUR_0', Numeric(21, 1), default=text('((0))'))
