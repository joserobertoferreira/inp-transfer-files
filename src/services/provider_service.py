import logging

from src.database.database import db
from src.models.models import EdiPartners
from src.utils.local_menus import YesNo

logger = logging.getLogger(__name__)


def get_active_providers() -> list[EdiPartners]:
    """
    Busca no banco de dados a lista de fornecedores ativos usando o ORM.
    Retorna uma lista de objetos EdiPartners.
    """
    logger.info('A buscar configurações de fornecedores ativos via ORM...')
    try:
        # Usamos o context manager para obter uma sessão segura
        with db.get_db() as session:
            providers = (
                session.query(EdiPartners)
                .filter(
                    EdiPartners.is_active == YesNo.YES,
                    EdiPartners.use_ftp == YesNo.YES,
                )
                .all()
            )

            if not providers:
                logger.warning('Nenhum fornecedor ativo encontrado na base de dados.')
                return []

            logger.info(f'Encontrados {len(providers)} fornecedores ativos.')
            return providers
    except Exception:
        logger.critical('Falha crítica ao buscar fornecedores no banco de dados via ORM.', exc_info=True)
        return []


# def get_active_providers_raw() -> list[dict[str, Any]]:
#     """
#     Busca no banco de dados a lista de fornecedores ativos para troca de ficheiros.

#     Returns:
#         Uma lista de dicionários, onde cada dicionário representa um fornecedor
#         e suas configurações de conexão (host, user, pass, protocol, etc.).
#     """
#     query = f"""
#         SELECT
#             a.BPRNUM_0 as provider_id,
#             a.BPRNAM_0 as provider_name,
#             ISNULL(b.LANMES_0,'ftp') as protocol,
#             a.FTPURL_0 as host,
#             a.FTPMOD_0 as mode,
#             a.FTPUSR_0 as username,
#             a.FTPPSW_0 as password,
#             a.FTPOUT_0 as remote_path_out,
#             a.FTPINP_0 as remote_path_in,
#             a.DRTOUT_0 as local_path_out,
#             a.DRTINP_0 as local_path_in
#         FROM {settings.SCHEMA}.ZEDIPAR a
#         LEFT JOIN {settings.SCHEMA}.APLSTD b ON b.LAN_0='POR' AND b.LANCHP_0=6241 AND b.LANNUM_0=a.FTPTYP_0
#         WHERE a.ENAFLG_0=2 AND a.FTPFLG_0=2
#     """

#     logger.info('A buscar configurações de fornecedores ativos na base de dados...')
#     try:
#         with db.get_db() as session:
#             providers = session.execute(query).fetchall()

#         if not providers:
#             logger.warning('Nenhum fornecedor ativo encontrado na base de dados.')
#             return []

#         logger.info(f'Encontrados {len(providers)} fornecedores ativos.')
#         return providers

#     except Exception:
#         logger.critical('Falha crítica ao buscar fornecedores no banco de dados:', exc_info=True)
#         return []
