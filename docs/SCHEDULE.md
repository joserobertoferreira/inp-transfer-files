## Fase 5: Agendamento de Tarefas

Nesta fase, o script foi transformado num serviço de backend contínuo, capaz de executar as transferências de ficheiros de forma periódica e configurável por fornecedor.

### 5.1 Biblioteca de Agendamento

Foi utilizada a biblioteca `schedule` pela sua simplicidade e legibilidade para definir tarefas periódicas (ex: "a cada X minutos").

### 5.2 Arquitetura Multi-Thread

Para permitir a futura integração com um frontend de monitorização, a lógica do agendador foi encapsulada para correr numa **thread dedicada em segundo plano**.

-   **Thread Principal (`main.py`):** Responsável por iniciar a aplicação, carregar as configurações, configurar as tarefas e iniciar a thread do agendador. Esta thread permanece livre e é o local onde um futuro servidor de API (Flask, FastAPI) será executado.
-   **Thread do Agendador (`scheduler.py`):** Contém um loop que corre continuamente, verificando e executando as tarefas pendentes (`schedule.run_pending()`).

### 5.3 Paragem Graciosa (Graceful Shutdown)

A comunicação entre a thread principal e a do agendador é gerida por um `threading.Event`. Quando a aplicação recebe um sinal de paragem (como `Ctrl+C`), a thread principal sinaliza o evento, permitindo que a thread do agendador termine o seu ciclo atual e feche de forma limpa, sem interromper uma transferência a meio.

### 5.4 Configuração por Fornecedor

O modelo de dados `EdiPartners` foi estendido para incluir um campo (`schedule_interval_minutes`) que define a frequência de execução para cada fornecedor. O sistema lê este valor no arranque e configura uma tarefa de agendamento individual para cada fornecedor ativo que tenha um intervalo de execução válido.