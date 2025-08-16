import logging
from typing import Any

from src.config import settings
from src.database.manager import DatabaseManager

logger = logging.getLogger(__name__)


def get_active_providers() -> list[dict[str, Any]]:
    """
    Busca no banco de dados a lista de fornecedores ativos para troca de ficheiros.

    Returns:
        Uma lista de dicionários, onde cada dicionário representa um fornecedor
        e suas configurações de conexão (host, user, pass, protocol, etc.).
    """
    query = f"""
        SELECT
            a.BPRNUM_0 as provider_id,
            a.BPRNAM_0 as provider_name,
            ISNULL(b.LANMES_0,'ftp') as protocol,
            a.FTPURL_0 as host,
            a.FTPMOD_0 as mode,
            a.FTPUSR_0 as username,
            a.FTPPSW_0 as password,
            a.FTPOUT_0 as remote_path_out,
            a.FTPINP_0 as remote_path_in,
            a.DRTOUT_0 as local_path_out,
            a.DRTINP_0 as local_path_in
        FROM {settings.SCHEMA}.ZEDIPAR a
        LEFT JOIN {settings.SCHEMA}.APLSTD b ON b.LAN_0='POR' AND b.LANCHP_0=6241 AND b.LANNUM_0=a.FTPTYP_0
        WHERE a.ENAFLG_0=2 AND a.FTPFLG_0=2
    """

    logger.info('A buscar configurações de fornecedores ativos na base de dados...')
    try:
        with DatabaseManager() as db:
            providers = db.fetch_data(query)

        if not providers:
            logger.warning('Nenhum fornecedor ativo encontrado na base de dados.')
            return []

        logger.info(f'Encontrados {len(providers)} fornecedores ativos.')
        return providers

    except Exception:
        logger.critical('Falha crítica ao buscar fornecedores no banco de dados:', exc_info=True)
        return []
