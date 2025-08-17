from typing import Dict, List, Optional, Tuple, Type, TypeVar, cast

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.type_api import TypeEngine  # For proper type hint of column_type

# Genérico para o tipo Python, ajuda nos type hints
T = TypeVar('T')


class ArrayColumnMixin:
    """
    Mixin to create a hybrid_property that acts like a list
    mapped to multiple columns in the database (ex: COL_0, COL_1, ...).
    This is useful for cases where you want to store a list of values
    in separate columns but access them as a single list in Python.
    """

    @classmethod
    def create_array_property(  # noqa: PLR0913, PLR0917
        cls,
        db_column_prefix: str,
        property_name: str,
        count: int,
        column_type: Type[TypeEngine],  # Ex: Date, Unicode, Integer (tipo SQLAlchemy)
        column_args: Tuple = (),  # Ex: (10, 'Latin1_General_BIN2') para Unicode
        python_type: Type[T] = object,  # Ex: date, str, int (tipo Python para hints)
        **kwargs,  # Argumentos extras para mapped_column (nullable, server_default, etc.)
    ) -> Tuple[hybrid_property[List[Optional[T]]], Dict[str, Mapped[Optional[T]]]]:
        # ) -> Tuple[hybrid_property, Dict[str, Mapped[Optional[T]]]]:
        """
        Create and return a hybrid_property and a dictionary of the underlying Mapped columns.

        Args:
            db_column_prefix: Prefix of the column names in the database (e.g., 'DATINV').
            property_name: Desired name for the hybrid property in the Python model (e.g., 'datinv').
            count: Number of columns in the database (e.g., 3 for DATINV_0, DATINV_1, DATINV_2).
            column_type: The SQLAlchemy type CLASS for the columns (e.g., Date, Unicode, Integer).
            column_args: Arguments to instantiate the column_type (e.g., (10,) for Unicode).
            python_type: The corresponding Python type for type hints (e.g., date, str, int).
            **kwargs: Additional arguments passed to each `mapped_column` (e.g., nullable=True).

        Returns:
            A tuple containing:
            1. The configured hybrid_property object.
            2. A dictionary where the keys are the names of the internal attributes
               (e.g., '_datinv_0') and the values are the corresponding Mapped objects.
        """
        mapped_columns: Dict[str, Mapped[Optional[T]]] = {}
        internal_attr_names: List[str] = []

        # 1. Prepara a instância do tipo SQLAlchemy
        if column_args:
            type_instance: TypeEngine = column_type(*column_args)
        else:
            type_instance: TypeEngine = column_type()  # Ex: Date(), Integer()

        # 2. Generate names and create Mapped objects for individual columns
        for i in range(count):
            db_column_name = f'{db_column_prefix}_{i}'
            # use property_name to ensure uniqueness if using the mixin multiple times
            internal_attr_name = f'_{property_name}_{i}'
            internal_attr_names.append(internal_attr_name)

            # create the mapped_column for this index
            mapped_columns[internal_attr_name] = mapped_column(db_column_name, type_instance, **kwargs)

        # 3. Defines a getter function that retrieves the values of the internal attributes
        def getter(self) -> List[Optional[python_type]]:  # type: ignore
            """Read the internal attributes and return as a list."""
            return [getattr(self, name, None) for name in internal_attr_names]

        # 4. Defines a setter function that takes a list and assigns it to the internal attributes
        def setter(self, value: List[Optional[python_type]]) -> None:  # type: ignore
            """Receive a list and distribute it to the internal attributes."""
            if not isinstance(value, list):
                raise TypeError(f"Valor atribuído a '{property_name}' deve ser uma lista.")

            # Opcional: Validar tamanho máximo
            if len(value) > count:
                raise ValueError(f"Lista para '{property_name}' não pode ter mais que {count} elementos.")

            # Set the values to the internal attributes, padding with None if necessary or
            # the list is shorter than 'count'
            padded_values = value + [None] * (count - len(value))
            for i in range(count):
                setattr(self, internal_attr_names[i], padded_values[i])

        # 5. Create the hybrid_property using the getter and setter functions
        array_prop = hybrid_property(fget=getter, fset=setter)

        # 6. Return the hybrid_property and the dictionary of mapped columns
        # return array_prop, mapped_columns
        return cast(hybrid_property[List[Optional[T]]], array_prop), mapped_columns
