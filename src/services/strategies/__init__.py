import logging

from src.models.edi_partner import EdiPartner

# Importar a classe base para anotação de tipo
from .base import BaseTransferStrategy

# Importar as implementações concretas que serão usadas no mapa
from .france_messagerie import FranceMessagerieStrategy
from .mlp import MlpStrategy

logger = logging.getLogger(__name__)

# O mapa de estratégias vive aqui, no ponto de entrada do pacote.
STRATEGY_MAP = {
    '1526': FranceMessagerieStrategy,
    '1510': MlpStrategy,
}


def get_strategy_for_provider(provider: EdiPartner) -> type[BaseTransferStrategy]:
    """
    Factory function que retorna a CLASSE de estratégia apropriada para um fornecedor.
    Se nenhuma estratégia específica for encontrada, retorna a classe base padrão.
    """
    # Usamos o provider_id (ou outro campo) para procurar no mapa de estratégias.
    provider_id = str(provider.provider)

    # .get() com um valor padrão é perfeito aqui. Se o ID não estiver no mapa, usa BaseTransferStrategy.
    StrategyClass = STRATEGY_MAP.get(provider_id, BaseTransferStrategy)

    logger.info(f"Fornecedor '{provider_id}' usará a classe de estratégia: {StrategyClass.__name__}")

    # Retornamos a classe em si, não uma instância.
    return StrategyClass
