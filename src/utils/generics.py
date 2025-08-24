import logging
import platform
from datetime import datetime
from typing import Any

from sqlalchemy import engine

# Configurar logging
logger = logging.getLogger(__name__)


class Generics:
    def __init__(self):
        pass

    @staticmethod
    def check_odbc_driver(driver_name):
        """
        Verifica se o driver ODBC é suportado no sistema operacional atual.
        :param driver_name: Nome do driver ODBC a ser verificado.
        :return: None se o driver for suportado, ou uma mensagem de erro se não for.
        """
        os_name = platform.system()
        error_message = None
        supported_drivers = {'ODBC Driver 17 for SQL Server', 'ODBC Driver 18 for SQL Server'}

        if os_name == 'Windows':
            if driver_name not in supported_drivers:
                error_message = f"Driver '{driver_name}' não é suportado no Windows."
            else:
                driver_name = driver_name.replace(' ', '+')
        elif os_name == 'Linux' and driver_name not in supported_drivers:
            error_message = f"Driver '{driver_name}' não é suportado no Linux."
        elif os_name == 'Darwin' and driver_name not in supported_drivers:
            error_message = f"Driver '{driver_name}' não é suportado no macOS."
        elif os_name not in {'Windows', 'Linux', 'Darwin'}:
            error_message = f"Sistema operacional '{os_name}' não suportado."

        return error_message, driver_name

    @staticmethod
    def build_connection_string(config: dict[str, Any], use_pyodbc: bool = False) -> engine.URL:
        """
        Builds the database connection string.
        :param config: Dictionary with the database configuration.
        :return: Formatted connection string.
        """
        driver_name = config.get('DRIVER', '')
        # error_message, driver_name = self.check_odbc_driver(driver_name)

        # if error_message:
        #     return error_message, None

        if use_pyodbc:
            conn_str = engine.URL.create(
                drivername='mssql+pyodbc',
                host=config['SERVER'],
                database=config['DATABASE'],
                username=config.get('USERNAME'),
                password=config.get('PASSWORD'),
                query={
                    'driver': driver_name,
                    # 'Encrypt': config['encrypt'],
                    # "TrustServerCertificate": "yes",
                    # "Trusted_Connection": config.get("trusted_connection", "no") # Se usar Windows Auth
                },
            )
        else:
            conn_str = engine.URL.create(
                drivername='mssql+pymssql',
                host=config['SERVER'],
                database=config['DATABASE'],
                username=config.get('USERNAME'),
                password=config.get('PASSWORD'),
                port=config.get('PORT', 1433),
            )

        logger.info(f'String de conexão criada: {conn_str}')
        return conn_str

    @staticmethod
    def get_year_and_iso_week() -> str:
        """
        Returns the current year and ISO week number in the format ISO 8601 (YYYY_WK).
        Example: '2024_03' for the third week of 2024.
        """

        # Get the current date and time
        today = datetime.now()

        # .isocalendar() returns a tuple (year, week, weekday)
        iso_calendar = today.isocalendar()

        # Extract the year and week
        iso_year = iso_calendar.year
        iso_week = iso_calendar.week

        # Format the output string.
        # The '02' in the f-string ensures that the week number is always two digits
        # (ex: 01, 02, ..., 10, 11).
        return f'{iso_year}_{iso_week:02}'
