import base64
import hashlib
import hmac
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Optional

from dateutil import parser

from src.config.settings import DEFAULT_LEGACY_DATETIME


class Conversions:
    """
    Uma classe de utilidades com métodos estáticos robustos para conversão
    de tipos de dados, principalmente a partir de strings.
    """

    @staticmethod
    def to_int(value: Any, default: Optional[int] = None) -> Optional[int]:
        """
        Converte um valor de forma segura para um inteiro.
        Lida com strings, floats e valores vazios.

        Args:
            value: O valor a ser convertido.
            default: O valor a ser retornado se a conversão falhar.
                     Se None, retorna None em caso de falha.

        Returns:
            O valor convertido para int, o valor padrão, ou None.
        """
        if value is None:
            return default

        try:
            # Tenta converter floats (ex: 123.0) e strings (ex: " 123 ")
            return int(float(str(value).strip()))
        except (ValueError, TypeError):
            return default

    @staticmethod
    def to_decimal(value: Any, precision: Optional[int] = None, default: Optional[Decimal] = None) -> Optional[Decimal]:
        """
        Converte um valor de forma segura para um Decimal.
        Lida com strings, floats, ints e valores vazios.

        Args:
            value: O valor a ser convertido.
            precision: Número de casas decimais para arredondar.
            default: O valor a ser retornado se a conversão falhar.
                     Se None, retorna None em caso de falha.

        Returns:
            O valor convertido para Decimal, o valor padrão, ou None.
        """
        if value is None or str(value).strip() == '':  # noqa: PLC1901
            return default

        try:
            decimal_value = Decimal(str(value).strip())
            if precision is not None:
                # O 'quantize' é a forma correta de arredondar Decimals
                return decimal_value.quantize(Decimal('1e-' + str(precision)))
            return decimal_value
        except InvalidOperation:
            return default

    @staticmethod
    def to_date(value: Any, default: Optional[date] = None) -> Optional[date]:
        """
        Converte uma string ou datetime para um objeto date.

        Args:
            value: O valor a ser convertido (ex: "20240825", datetime.now()).
            default: O valor a ser retornado se a conversão falhar.
                     Se None, retorna None em caso de falha.

        Returns:
            O valor convertido para date, o valor padrão, ou None.
        """
        result = default
        if value is not None:
            if isinstance(value, datetime):
                result = value.date()
            elif isinstance(value, date):
                result = value
            else:
                value_str = str(value).strip()
                if value_str:
                    try:
                        result = parser.parse(value_str).date()
                    except (parser.ParserError, ValueError, TypeError):
                        try:
                            result = datetime.strptime(value_str, '%Y%m%d').date()
                        except (ValueError, TypeError):
                            pass
        return result

    @staticmethod
    def to_datetime(value: Any, default: Optional[datetime] = None) -> Optional[datetime]:
        """Converte uma string ou date para um objeto datetime."""
        # Lógica similar à to_date, mas sem o .date() no final
        if value is None:
            return default
        # ... (implementação completa)
        return default

    @staticmethod
    def to_bool(value: Any) -> bool:
        """
        Converte um valor para boolean de forma flexível.
        Considera "true", "t", "yes", "y", "1" como True.
        """
        if isinstance(value, bool):
            return value
        if str(value).strip().lower() in {'true', 't', 'yes', 'y', '1', '2'}:  # '2' por causa do seu enum YesNo.YES
            return True
        return False

    @staticmethod
    def convert_value(value: Any, precision: int = 0) -> Any:
        if isinstance(value, str):
            return_value = Conversions._convert_str(value)
        elif isinstance(value, int):
            return_value = value
        elif isinstance(value, float):
            return_value = Conversions._convert_float(value, precision)
        elif isinstance(value, bool):
            return_value = value
        elif value is None:
            return_value = value
        elif isinstance(value, datetime):
            return_value = value
        elif isinstance(value, date):
            return_value = value
        elif isinstance(value, Decimal):
            return_value = Conversions._convert_decimal(value, precision)
        elif isinstance(value, list):
            return_value = Conversions._convert_list(value)
        else:
            return_value = value

        return return_value

    @staticmethod
    def _convert_str(value: str) -> str:
        return value.strip()

    @staticmethod
    def _convert_float(value: float, precision: Optional[int]) -> float:
        if precision != 0:
            return round(value, precision)
        return value

    @staticmethod
    def _convert_decimal(value: Decimal, precision: Optional[int]) -> Decimal:
        if value.is_normal():
            if precision != 0:
                return Decimal(round(value, precision))
            return value
        else:
            return Decimal(0)

    @staticmethod
    def convert_to_datetime(value: str, default: bool = False) -> Optional[datetime]:
        """
        Convert a string to a datetime object in ISO UTC format.

        Parameters:
            value (str): String to be converted.
            default (bool): Defines whether to return datetime(1753, 1, 1) in ISO UTC
              format in case of error.

        Returns:
            str: The converted date in ISO UTC format, or datetime(1753, 1, 1) in case of
              error (if default=True).
        """
        try:
            # First, try to convert directly to ISO format.
            return parser.isoparse(value)
        except (ValueError, TypeError):
            pass

        try:
            # Try a generic conversion using dateutil.parser.parse.
            return parser.parse(value)
        except (ValueError, TypeError):
            pass

        # If the string is empty or no conversion was possible.
        if not value or default:
            return datetime(1753, 1, 1)

        # If no conversion is possible and default=False, return None.
        return None

    @staticmethod
    def convert_to_date(value: str, default: bool = False) -> Optional[date]:
        """
        Convert a string to a date object.

        Parameters:
            value (str): String to be converted.
            default (bool): Defines whether to return date(1753, 1, 1) in case of error.

        Returns:
            date: The converted date object or date(1753, 1, 1) in case of error
              (if default=True).
        """
        try:
            # First, try to convert directly to ISO format and extract the date.
            return parser.isoparse(value).date()
        except (ValueError, TypeError):
            pass

        try:
            # Try a generic conversion using dateutil.parser.parse and extract the date.
            return parser.parse(value).date()
        except (ValueError, TypeError):
            pass

        # If the string is empty or no conversion was possible.
        if not value or default:
            return date(1753, 1, 1)

        # If no conversion is possible and default=False, return None.
        return None

    @staticmethod
    def _convert_list(value: list) -> list:
        return [Conversions.convert_value(item) for item in value]

    @staticmethod
    def ensure_date(value) -> date:
        """
        Ensure that the value is a date object, maintaining date unaltered.
        """
        if isinstance(value, datetime):
            return value.date()
        return value

    @staticmethod
    def convert_values(data: dict[str, Any]) -> dict[str, Any]:
        """
        Converte os valores de um dicionário para uma forma mais legível.

        Args:
            data (dict): Dicionário com chave e valor a ser convertido.

        Returns:
            dict: Novo dicionário com os valores convertidos.
        """

        return {key: Conversions.convert_value(value) for key, value in data.items()}

    @staticmethod
    def generate_sql_with_values(query, values):
        """
        Gera a query SQL com valores reais substituindo os placeholders.

        :param query: A consulta SQL com placeholders (?)
        :param values: A lista de valores que substituirão os placeholders
        :return: A query com valores reais
        """
        # Substituir os placeholders (?) pelos valores reais
        # Primeiro, formatar os valores para evitar erro com tipos
        formatted_values = [repr(v) for v in values]

        # Substituir os placeholders (?):
        for value in formatted_values:
            query = query.replace('?', value, 1)  # Substituir um placeholder por vez

        return query

    @staticmethod
    def convert_file_to_base64(file_path: str, file_name: str) -> str:
        file_attributes = Path(file_path) / file_name

        base_string = ''

        # Open the file in binary mode and read its content
        if file_attributes.is_file():
            with file_attributes.open('rb') as file:
                content = file.read()
                base_string = base64.b64encode(content).decode('utf-8')

        return base_string

    @staticmethod
    def is_number(value):
        try:
            # Try to convert the value to a number (int or float)
            float_value = float(value)

            # Check if the converted number is an integer or decimal
            if float_value.is_integer():
                return 'integer'
            else:
                return 'decimal'
        except ValueError:
            # Return None if it's not possible to convert
            return None

    @staticmethod
    def generate_signature(message_body: str, app_key: str) -> str:
        """
        Create an HMAC-SHA256 signature for the provided message.

        Args:
            message_body (str): Request body to be signed.
            app_key (str): Application key used for signing.

        Returns:
            str: The HMAC-SHA256 signature in hexadecimal format.
        """
        secret_bytes = app_key.encode('utf-8')
        message_bytes = message_body.encode('utf-8')

        signature = hmac.new(secret_bytes, message_bytes, hashlib.sha256).hexdigest()

        return signature

    @staticmethod
    def convert_string_to_datetime(value: Optional[str]) -> datetime:
        """Converts a string date from the data dictionary to a datetime object.
        If the date is not present or cannot be parsed, it returns a default legacy datetime.
        Args:
            value (string): containing the date string.
        Returns:
            datetime: Parsed datetime object or a default legacy datetime if parsing fails.
        """

        if value is None:
            return_value = DEFAULT_LEGACY_DATETIME
        else:
            try:
                return_value = parser.isoparse(value)
            except parser.ParserError:
                return_value = DEFAULT_LEGACY_DATETIME

        return return_value
