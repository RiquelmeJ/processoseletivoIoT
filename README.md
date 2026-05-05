# Sistema de Alarme Inteligente IoT (Wokwi + MicroPython)

Este repositório contém a implementação de um sistema de alarme residencial desenvolvido no simulador Wokwi. O projeto utiliza um Raspberry Pi Pico W programado em MicroPython, integrando sensores virtuais para gerenciar a lógica de monitoramento. A ideia do projeto surgiu como uma refatoração do projeto que idealizei para a etapa final do Embarca Tech.

## 🛠️ Arquitetura de Hardware
A montagem no Wokwi utiliza os seguintes componentes:
- Raspberry Pi Pico W: Placa principal responsável pelo processamento lógico.
- RTC DS1307: Relógio em tempo real conectado via protocolo I2C (pinos 20 e 21). Utilizado para validar o período de funcionamento ativo do alarme (das 18h às 06h).
- Sensor PIR: Sensor de movimento (pino 16) que envia um sinal digital de nível alto ao detectar presença.
- Buzzer: Buzzer (pino 22) para alerta sonoro em caso de invasão, e um LED RGB (pinos 10, 11 e 12) para indicação visual do status (Verde para monitoramento ativo, Vermelho para inativo).

## 💻 Lógica do Firmware (Máquina de Estados)
Para garantir que o código seja responsivo e não perca leituras do sensor, o firmware foi estruturado utilizando o conceito de Máquina de Estados com temporização não-bloqueante (time.ticks_ms()), evitando o uso do comando time.sleep() que trava o processador.

O sistema transita entre três estados principais:
- 0 - INATIVO: Durante o dia, o alarme permanece desativado. O LED fica vermelho e o sistema confere o relógio a cada segundo.
- 1 - ATIVO: No período noturno, o alarme é ativado. O LED muda para verde e o microcontrolador monitora o sensor PIR continuamente, sem interrupções.
- 2 - DISPARADO: Caso o PIR detecte movimento, o buzzer é acionado por 500 milissegundos. Após o disparo, o sistema entra em um "cooldown" de 2 segundos antes de retornar ao estado de vigilância.

## 🔄 Fluxo de Dados e Integração Contínua
1. O firmware lê os registradores de hora do RTC via barramento I2C.
2. Verifica se o horário atual está dentro da janela de monitoramento definida pelas variáveis globais.
3. Se o sistema estiver ativo e o PIR detectar movimento, as saídas (buzzer e LED) são atualizadas instantaneamente.

**Pipeline de CI/CD (GitHub Actions)**: Para manter a integridade do código, há um fluxo automatizado configurado no diretório .github. A cada novo *push*, o GitHub executa a simulação do Wokwi em background para garantir que o firmware compila sem erros e atinge o estado inicial com sucesso.

## ⚠️ Resultados e Limitações
A simulação comprova a viabilidade do Raspberry Pi Pico W como central de alarme, rodando o firmware de forma fluida. No entanto, existem diferenças entre o ambiente simulado e o mundo real:
- O simulador é matematicamente ideal e não reproduz ruídos elétricos. Um sensor PIR físico pode gerar instabilidades no sinal, o que exigiria um filtro por software que foi dispensado neste cenário.
