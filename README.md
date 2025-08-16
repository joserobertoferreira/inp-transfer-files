# Projeto de Transferência de Ficheiros

Este projeto tem como objetivo automatizar a troca de ficheiros entre um servidor local e servidores FTP/SFTP de fornecedores, permitindo a parametrização da periodicidade por fornecedor. Futuramente, será integrado a um frontend para monitorização e controlo dos processos.

## Fase 1: Configuração do Ambiente e Estrutura do Projeto

Esta fase inicial estabelece as bases do projeto, garantindo um ambiente de desenvolvimento isolado, a instalação das dependências necessárias e uma estrutura de pastas organizada. Para a gestão de dependências e ambientes virtuais, foi escolhida a ferramenta moderna e de alta performance **`uv`**.

### 1.1 Ambiente Virtual com `uv`

Para isolar as dependências do projeto, foi criado um ambiente virtual (`.venv`) utilizando `uv`. Esta abordagem é significativamente mais rápida do que as ferramentas padrão.

```bash
# Pré-requisito: Instalar uv (se necessário)
pip install uv

# Criar a pasta do projeto e navegar para ela
mkdir file_transfer_backend
cd file_transfer_backend

# Criar o ambiente virtual com uv
uv venv

# Ativar o ambiente virtual (comandos variam por OS)
# No Windows:
.venv\Scripts\activate
# No Linux/macOS:
source .venv/bin/activate