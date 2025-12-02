===========================
Discovery SNMP Agent
===========================

Agente SNMP para monitoramento de dispositivos descobertos na rede.
Exibe informações da ferramenta de autodescoberta via DISCOVERY-MIB.

---------------------------
Como executar
---------------------------

1. Instale a biblioteca snmp-agent:

    pip install snmp-agent

2. Execute o agente (porta padrão 16100 para testes locais):

    python3 discovery_snmp_agent.py

O programa fica rodando em loop, escutando requisições SNMP.

3. Para consultar os valores via SNMP, use snmpwalk:

    snmpwalk -v2c -c public 127.0.0.1 1.3.6.1.3.2025

---------------------------
OIDs
---------------------------

Base da MIB: 1.3.6.1.3.2025 (experimental)

1.3.6.1.3.2025.1.1.0  - Counter32  - discoveryRuns: Número de execuções da varredura
1.3.6.1.3.2025.1.2.0  - Gauge32    - devicesFound: Número atual de dispositivos descobertos
1.3.6.1.3.2025.1.3.0  - TimeTicks  - lastDiscoveryTime: Tempo desde a última varredura (centésimos de segundo)

Tabela de dispositivos (discoveryTable)
Cada dispositivo descoberto é representado por uma linha da tabela:

.2.1.1.1.<index> - INTEGER   - deviceIndex (índice do dispositivo)
.2.1.1.2.<index> - STRING    - deviceIp (endereço IPv4)
.2.1.1.3.<index> - STRING    - deviceName (nome do dispositivo, "-" se não disponível)
.2.1.1.4.<index> - STRING    - deviceMac (endereço MAC)
.2.1.1.5.<index> - TimeTicks - responseTime (tempo de resposta na varredura)
.2.1.1.6.<index> - TimeTicks - lastSeen (tempo desde que o dispositivo foi visto pela última vez)

Exemplo de saída:
iso.3.6.1.3.2025.2.1.1.2.1 = STRING: "172.27.170.105"
iso.3.6.1.3.2025.2.1.1.4.1 = STRING: "12:ef:31:94:c5:86"
iso.3.6.1.3.2025.2.1.1.6.1 = Timeticks: (103142275) 11 days, 22:30:22.75

Configuração do agente:

.3.1.0 - INTEGER - scanInterval: intervalo entre varreduras automáticas (segundos)
.3.2.0 - INTEGER - logLevel: nível de log (0=off, 1=erro, 2=info, 3=debug)

Exemplo:
iso.3.6.1.3.2025.3.1.0 = INTEGER: 60  # scan a cada 60s
iso.3.6.1.3.2025.3.2.0 = INTEGER: 2   # nível de log info

---------------------------
Observações
---------------------------

- O agente fica travado em "SNMP agent listening on 0.0.0.0:16100" porque ele escuta requisições SNMP continuamente.
- Para testes, use snmpwalk ou snmpget contra o host local.
- Cada dispositivo descoberto na rede é exposto na tabela .2.1.1 com índice incremental.
- O arquivo last_seen.txt armazena informações de IP, MAC, vendor e timestamp da primeira detecção.