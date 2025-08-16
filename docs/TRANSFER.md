# Documentação da Lógica de Transferência

Este documento detalha a arquitetura de transferência de ficheiros, que é projetada para ser modular, extensível e capaz de lidar com regras de negócio específicas para cada fornecedor sem a necessidade de modificar o código principal.

## Arquitetura Geral

A lógica de transferência é dividida em três componentes principais que trabalham em conjunto:

1.  **Managers (`src/transfer`)**: Classes responsáveis pela comunicação de baixo nível com os servidores. Existe um `Manager` para cada protocolo suportado (ex: `FtpManager`, `SftpManager`). A sua única responsabilidade é conectar, desconectar e executar operações básicas de ficheiros (`upload`, `download`, `list`, `delete`).

2.  **Estratégias (`src/services/strategies.py`)**: Classes que definem o **fluxo de trabalho** e as **regras de negócio** para a transferência. Cada estratégia encapsula a lógica de "o que fazer" e "quando fazer". Por exemplo, uma estratégia define se um ficheiro deve ser apagado após o download ou se os nomes dos ficheiros precisam de ser gerados dinamicamente.

3.  **Serviço de Orquestração (`src/services/transfer_service.py`)**: Atua como o "maestro". Ele não conhece os detalhes da transferência, mas sabe como:
    *   Selecionar o `Manager` correto com base no protocolo do fornecedor.
    *   Selecionar a `Strategy` correta com base no ID do fornecedor (ou outro critério).
    *   Juntar os dois e iniciar o processo.

## O Padrão de Projeto "Strategy"

O núcleo desta arquitetura é o Padrão de Projeto *Strategy*. Ele permite definir uma família de algoritmos (nossas estratégias de transferência), encapsular cada um deles e torná-los intercambiáveis.

### `BaseTransferStrategy`

É a classe base localizada em `src/services/strategies.py`. Ela define o fluxo de trabalho padrão, que consiste em:
1.  Executar `process_downloads()`.
2.  Executar `process_uploads()`.

Ela também contém métodos "gancho" (hooks) como `after_download_success()` e `after_upload_success()`, que por defeito não fazem nada.

### Estratégias Personalizadas

Para fornecedores com regras especiais, criamos novas classes que herdam de `BaseTransferStrategy` e sobrescrevem apenas os métodos necessários.

**Exemplo 1: Apagar ficheiro após download**
```python
class DeleteAfterDownloadStrategy(BaseTransferStrategy):
    """
    Sobrescreve apenas a ação a ser executada após um download bem-sucedido.
    """
    def after_download_success(self, remote_file: str):
        logger.info(f"A remover ficheiro remoto: {remote_file}")
        self.manager.delete_file(remote_file)
```

**Exemplo 2: Baixar ficheiros com nome específico**
```python
class SpecificFilenameDownloadStrategy(BaseTransferStrategy):
    """
    Sobrescreve o método que decide quais ficheiros devem ser baixados.
    """
    def get_files_to_download(self) -> List[str]:
        # Lógica para gerar o nome do ficheiro esperado
        today_str = datetime.now().strftime('%Y%m%d')
        expected_filename = f"dados_{today_str}.csv"
        # ... lógica para verificar se o ficheiro existe no servidor ...
        return [expected_filename]

```
