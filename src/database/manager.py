import logging
from typing import Any, Optional

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from src.config import settings

# Configurar logging
logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages the database engine and provides both an ORM Session and a raw Connection.
    The session is managed within a transaction (commit/rollback).
    The connection is provided for direct query execution.
    """

    def __init__(self):
        """
        Inicializa o gerenciador, construir a string de conexão.
        """
        self.db_uri = (
            f'mssql+pymssql://'
            f'{settings.USERNAME}:{settings.PASSWORD}@'
            f'{settings.SERVER}:{settings.PORT}/'
            f'{settings.DATABASE}'
        )
        self.engine: Engine = create_engine(self.db_uri, echo=settings.DEBUG)  # 'echo' é útil para debug

        # Cria uma "fábrica" de sessions ligada ao engine
        self._SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        self.session: Optional[Session] = None
        self.connection: Optional[Connection] = None

    def __enter__(self):
        """
        Abre uma conexão e uma sessão ORM.
        """
        try:
            # Obtém uma conexão do pool
            self.connection = self.engine.connect()
            logger.info('Raw database connection opened.')

            # Cria uma sessão ORM a partir da conexão.
            # Isto garante que a sessão e a conexão participam da mesma transação.
            self.session = self._SessionLocal(bind=self.connection)
            logger.info('ORM session opened.')

            return self
        except SQLAlchemyError:
            logger.critical('Failed to create database session or connection.', exc_info=True)
            # Garante que limpamos tudo em caso de falha na inicialização
            self.__exit__(SQLAlchemyError, None, None)
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Faz commit/rollback na sessão e fecha tanto a sessão como a conexão.
        """
        if self.session:
            try:
                if exc_type is not None:
                    logger.warning('An exception occurred in the with-block. Rolling back ORM session.')
                    self.session.rollback()
                else:
                    logger.info('Committing ORM session.')
                    self.session.commit()
            except SQLAlchemyError:
                logger.error('Error during ORM session commit/rollback.', exc_info=True)
                self.session.rollback()
            finally:
                self.session.close()
                logger.info('ORM session closed.')

        if self.connection:
            self.connection.close()
            logger.info('Raw database connection closed.')

    def fetch_data(self, query_base: str, params: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        """
        Executa uma query "crua" e retorna os resultados como uma lista de dicionários.
        """
        if not self.connection:
            logging.error('Nenhuma conexão com o banco de dados ativa.')
            return []

        try:
            stmt = text(query_base)

            if settings.DEBUG:
                logging.info(f'Executando query: {stmt}')
                logging.info(f'Com parâmetros: {params}')

            result_proxy = self.connection.execute(stmt, params or {})

            results = [dict(row) for row in result_proxy.mappings().all()]

            return results
        except SQLAlchemyError as e:
            logging.error(f'Erro ao executar a query com SQLAlchemy: {e}')
            return []
