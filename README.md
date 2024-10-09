# Trabalho 1 (2024-1)

Trabalho 1 da disciplina de Fundamentos de Sistemas Embarcados (2024/1). Focado na simulação de um sistema distribuído para controle de estacionamentos. Cada andar é composto da seguinte forma:

* Térreo:
    * Cancela de entrada: um botão irá simular a chegada de uma carro, o sensor de presença indica a presença do carro aguardando a cancela abrir, a cancela e um sensor de passagem indicando que a cancela pode ser fechada;
    * Sinal de lotado (Led vermelho): indicando quando o estacionamento está cheio;
    * Cancela de saída: sensor de presença indicando a presença do carro aguardando a cancela abrir, a cancela e um sensor de passagem indicando que a cancela pode ser fechada;
    * 8 vagas com sensores indicando a ocupação da vaga e um botão para remover o carro.

* 1º e 2º Andar:
    * 8 vagas com sensores indicando a ocupação da vaga e um botão para remover o carro;
    * Sinal de lotado (Led vermelho): indicando quando o andar está lotado;
    * Dois sensores que indicam a passagem de veículos entre os andares.

Mais informações estão disponíveis no [Enunciado do trabalho](https://gitlab.com/fse_fga/trabalhos-2024_1/trabalho-1-2024-1).

## Estrutura do Projeto

```
├── central_server ---> Serviço do servidor central.
│   ├── connections ---> Classes para conectividade do servidor.v
│   │   ├── client.py ---> Envio de mensagens para os servidores distribuídos.
│   │   └── server.py ---> Recebimento de mensagens dos servidores distribuídos.
│   ├── controller ---> Classes para manipulação de dados.
│   │   └── message_handler.py ---> Tratamento das mensagens dos servidores distribuídos.
│   ├── main.py ---> Script para iniciar o serviço.
│   ├── model ---> Classes para armazenamento de dados do estacionamento.
│   │   ├── car.py ---> Dados e métodos para os carros.
│   │   └── floor.py ---> Dados e métodos para os andares.
│   └── view ---> Classes para visualização de dados e interface.
│       └── view.py ---> Visualização do estacionamento e envio de comandos.
|
├── ground_floor ---> Serviço do servidor distribuído do andar térreo.
│   ├── connections ---> Classes para conectividade do servidor.
│   │   ├── client.py ---> Envio de mensagens para o servidor central.
│   │   └── server.py ---> Recebimento de mensagens do servidor central.
│   ├── main.py ---> Script para iniciar o serviço.
│   └── model ---> Classes para armazenamento de dados do andar.
│       └── floor.py ---> Dados e métodos para o andar, além de tratamento das GPIO.
|
├── README.md ---> README do repositório.
├── requirements.txt ---> Dependências da aplicação.
├── reset_all.py ---> Script para reset das GPIO.
|
├── setup ---> Configurações de setup dos serviços.
│   └── config.json ---> Definição dos endereços e portas dos servidores, assim como GPIO.
|
└── upper_floors ---> Serviços dos servidores distribuídos do primeiro e segundo andar.
    ├── connections ---> Classes para conectividade do servidor.
    │   ├── client.py ---> Envio de mensagens para o servidor central.
    │   └── server.py ---> Recebimento de mensagens do servidor central.
    ├── main.py ---> Script para iniciar o serviço.
    └── model ---> Classes para armazenamento de dados dos andares.
        └── floor.py ---> Dados e métodos para os andares, além de tratamento das GPIO.
```

O projeto está estruturado em três grandes módulos: **central_server**, **ground_floor** e **upper_floors**. O primeiro tem o código do serviço do servidor central, o segundo do servidor distribuído para o andar térreo e o terceiro do servidor distribuído para o primeiro e segundo andar.

Além disso, a configuração dos endereços de IP/portas de cada servidor, assim como as GPIO, são configuradas no arquivo **config.json** no diretório **setup**. Mais detalhes da estrutura podem ser vistos na árvore de diretórios acima.

### Servidor Central

- [client.py](central_server/connections/client.py): gerencia uma lista de endereços de clientes e envia mensagens JSON para um cliente específico via uma conexão TCP, reportando erros em caso de falha na conexão.
- [server.py](central_server/connections/server.py): gerencia um servidor TCP que aceita conexões de clientes, recebendo e processando mensagens usando MessageHandler, reportando erros em caso de falhas na conexão ou no processamento das mensagens.
- [message_handler.py](central_server/controller/message_handler.py): gerencia mensagens relacionadas ao estacionamento, lidando com a entrada, movimentação, estacionamento e saída de carros, e atualizando os estados dos andares, enviando sinais de lotação aos clientes quando necessário.
- [car.py](central_server/model/car.py): define uma classe Car que representa um carro com atributos de tempo de entrada, vaga de estacionamento, e valor de estacionamento, fornecendo métodos para calcular o valor do estacionamento com base no tempo de permanência e para formatar e representar esses dados de maneira legível.
- [floor.py](central_server/model/floor.py): representa um andar de estacionamento, gerencia o estado das vagas e os carros estacionados, permitindo estacionar um carro, liberar uma vaga e verificar o número de vagas ocupadas para diferentes tipos de vagas.
- [view.py](central_server/view/view.py): define uma classe View que atua como interface de usuário e configura um servidor e um cliente a partir de um arquivo de configuração JSON, gerenciando sinais de lotação para diferentes andares de um estacionamento e enviando mensagens apropriadas a partir de opções do usuário.

### Servidores Distribuídos

- [floor.py (térreo)](ground_floor/model/floor.py) e [floor.py (primeiro e segundo)](upper_floors/model/floor.py): controla os dispositivos de um andar de estacionamento (cancela de entrada, cancela de saída, sinal de lotação, sensores de vagas, sensor de passagem e afins) usando GPIO em um Raspberry Pi, enviando mensagens ao servidor central para relatar estados de ocupação de vagas e movimentação de carros. Essencialmente, o código controla o estado das vagas de estacionamento e detecta a passagem de carros entre os andares do estacionamento, comunicando essas informações com um servidor central.
- [client.py (térreo)](ground_floor/connections/client.py) e [client.py (primeiro e segundo)](upper_floors/connections/client.py): estabelece uma conexão TCP com um servidor central e envia dados codificados em JSON, gerenciando e relatando qualquer erro que ocorra durante o envio da mensagem.
- [server.py (térreo)](ground_floor/connections/server.py) e [server.py (primeiro e segundo)](upper_floors/connections/server.py): configura e executa um servidor TCP para um andar de estacionamento, aceita conexões de clientes e processa mensagens JSON para ativar ou desativar um sinal de lotação, gerenciando erros de conexão e desligamento do servidor.

## Como rodar o projeto

1. Instale as dependências do projeto, executando na raiz do repositório o comando: ```pip install -r requirements.txt```
2. Configure o endereço de ip de cada servidor e as gpios no [arquivo de configuração](setup/config.json) 
3. Ainda na raiz do projeto, suba cada serviço executando sua respectiva main.py:
    1. Servidor central:
       - ``` python3 central_server/main.py```
    2. Servidor Distribuído 1 - Térreo:
        - ``` python3 ground_floor/main.py```
    3. **OBS**: o código para os servidores do primeiro e segundo andar é o mesmo, o que diferencia qual é o servidor executado é o número passado como argumento na hora de subir os serviços. ``1`` indica o primeiro andar e ``2`` o segundo. Esses argumentos devem ser passados exatamente dessa forma para que os serviços funcionem corretamente.
    4. Servidor Distribuído 2 - Primeiro Andar:
        - ``` python3 upper_floors/main.py 1```
    5. Servidor Distribuído 3 - Segundo Andar:
        - ``` python3 upper_floors/main.py 2```


## Vídeo de Apresentação

[Link para o vídeo da apresentação no youtube](https://youtu.be/yKywRDp2SVQ)

