# 🔧 Guia Completo - Sistema SNMP Web Interface

## 📋 Índice
1. [OIDs Disponíveis para Teste](#oids-disponíveis)
2. [Passo a Passo para Executar](#passo-a-passo)
3. [Verificação de Funcionamento](#verificação)
4. [Troubleshooting](#troubleshooting)

---

## 🎯 OIDs Disponíveis para Teste

### **Grupo 1: Discovery (MIB Base 1.3.6.1.3.2025)**

| OID | Nome | Descrição | Valor Esperado |
|-----|------|-----------|-----------------|
| `1.3.6.1.3.2025.1.1.0` | **discoveryRuns** | Número total de varreduras realizadas | Inteiro (ex: 5) |
| `1.3.6.1.3.2025.1.2.0` | **devicesFound** | Quantidade de dispositivos encontrados | Inteiro (ex: 3) |
| `1.3.6.1.3.2025.1.3.0` | **lastDiscoveryTime** | Tempo da última descoberta em TimeTicks | Inteiro (ex: 1234567) |
| `1.3.6.1.3.2025.3.1.0` | **scanInterval** | Intervalo de varredura em segundos | Inteiro (ex: 60) |
| `1.3.6.1.3.2025.3.2.0` | **logLevel** | Nível de logging (1-5) | Inteiro (ex: 2) |

### **Grupo 2: Tabela de Dispositivos (1.3.6.1.3.2025.2.1.1)**

A tabela contém registros de dispositivos descobertos com as seguintes colunas:

| OID | Coluna | Tipo | Descrição |
|-----|--------|------|-----------|
| `1.3.6.1.3.2025.2.1.1.1.{idx}` | deviceIndex | Integer | Índice do dispositivo (1, 2, 3...) |
| `1.3.6.1.3.2025.2.1.1.2.{idx}` | deviceIp | OctetString | Endereço IP do dispositivo |
| `1.3.6.1.3.2025.2.1.1.3.{idx}` | deviceName | OctetString | Nome/hostname do dispositivo |
| `1.3.6.1.3.2025.2.1.1.4.{idx}` | deviceMac | OctetString | Endereço MAC do dispositivo |
| `1.3.6.1.3.2025.2.1.1.5.{idx}` | responseTime | TimeTicks | Tempo de resposta |
| `1.3.6.1.3.2025.2.1.1.6.{idx}` | lastSeen | TimeTicks | Tempo desde última visualização |

**Exemplos de Tabela:**
- `1.3.6.1.3.2025.2.1.1.1.1` - Índice do dispositivo 1
- `1.3.6.1.3.2025.2.1.1.2.1` - IP do dispositivo 1
- `1.3.6.1.3.2025.2.1.1.2.2` - IP do dispositivo 2
- `1.3.6.1.3.2025.2.1.1.3.1` - Nome do dispositivo 1

### **Grupo 3: OIDs Padrão SNMP (RFC 1213)**

> ⚠️ **Nota**: Estes OIDs podem não estar disponíveis no agente custom. Teste apenas se desejar expandir o agente.

| OID | Descrição |
|-----|-----------|
| `1.3.6.1.2.1.1.1.0` | Descrição do Sistema |
| `1.3.6.1.2.1.1.2.0` | Object ID |
| `1.3.6.1.2.1.1.3.0` | Uptime do Sistema |
| `1.3.6.1.2.1.1.4.0` | Contact |
| `1.3.6.1.2.1.1.5.0` | Nome do Sistema |

---

## 🚀 Passo a Passo para Executar

### **Pré-requisitos**
- Python 3.10+
- Node.js 16+
- npm
- Acesso a terminal/shell

### **Etapa 1: Preparar o Ambiente**

```bash
# 1.1 - Abrir o terminal e navegar para o diretório do projeto
cd "/home/pao/Área de Trabalho/Gerencia de Redes/agent-snmp - Arthur Leitao"

# 1.2 - Verificar se o ambiente virtual Python existe
ls -la .venv/

# 1.3 - Se não existir, criar ambiente virtual
python3 -m venv .venv

# 1.4 - Ativar ambiente virtual (opcional, scripts já usam caminho completo)
source .venv/bin/activate
```

### **Etapa 2: Iniciar o Agente SNMP**

```bash
# 2.1 - Abrir um NOVO terminal e navegar para a pasta do agente
cd "/home/pao/Área de Trabalho/Gerencia de Redes/agent-snmp - Arthur Leitao/agent-snmp"

# 2.2 - Executar o agente SNMP (porta 16100)
"/home/pao/Área de Trabalho/Gerencia de Redes/agent-snmp - Arthur Leitao/.venv/bin/python" discovery_snmp_agent.py

# ✅ Esperado:
# SNMP agent listening on 0.0.0.0:16100 (MIB base 1.3.6.1.3.2025)
```

**⚠️ Deixar este terminal rodando!**

### **Etapa 3: Iniciar o Backend Flask**

```bash
# 3.1 - Abrir um NOVO terminal e navegar para a pasta raiz
cd "/home/pao/Área de Trabalho/Gerencia de Redes/agent-snmp - Arthur Leitao"

# 3.2 - Executar o backend Flask (porta 5000)
".venv/bin/python" snmp_manager.py

# ✅ Esperado:
# * Running on http://127.0.0.1:5000
# * Debugger is active!
```

**⚠️ Deixar este terminal rodando!**

### **Etapa 4: Iniciar o Frontend Vue.js**

```bash
# 4.1 - Abrir um NOVO terminal e navegar para a pasta snmp-web
cd "/home/pao/Área de Trabalho/Gerencia de Redes/agent-snmp - Arthur Leitao/snmp-web"

# 4.2 - Instalar dependências (primeira vez apenas)
npm install

# 4.3 - Executar servidor de desenvolvimento (porta 3000)
npm run dev

# ✅ Esperado:
# ➜  Local:   http://localhost:3000/
```

**⚠️ Deixar este terminal rodando!**

### **Etapa 5: Acessar a Interface**

```bash
# 5.1 - Abrir navegador e acessar:
http://localhost:3000

# 5.2 - A interface SNMP Web deve estar visível com:
# - Campo de entrada para OID
# - Campo de Host (127.0.0.1)
# - Campo de Porta (16100)
# - Campo de Community (public)
# - Botão "Consultar OID"
```

---

## ✅ Verificação de Funcionamento

### **Teste 1: Via curl (Backend + Agente)**

```bash
# Testar comunicação entre Backend e Agente SNMP
curl -s "http://127.0.0.1:5000/api/snmp/1.3.6.1.3.2025.1.1.0"

# ✅ Resposta esperada:
# {
#   "host": "127.0.0.1",
#   "oid": "1.3.6.1.3.2025.1.1.0",
#   "port": 16100,
#   "value": "5"
# }
```

### **Teste 2: Segundo OID via curl**

```bash
curl -s "http://127.0.0.1:5000/api/snmp/1.3.6.1.3.2025.1.2.0"

# ✅ Resposta esperada:
# {
#   "host": "127.0.0.1",
#   "oid": "1.3.6.1.3.2025.1.2.0",
#   "port": 16100,
#   "value": "3"
# }
```

### **Teste 3: Via Interface Web**

1. Acesse http://localhost:3000
2. Digite o OID: `1.3.6.1.3.2025.1.1.0`
3. Clique em "🚀 Consultar OID"
4. Verifique se o resultado aparece com a resposta correta

### **Teste 4: Com OID da Tabela**

1. Digite o OID: `1.3.6.1.3.2025.2.1.1.2.1` (IP do primeiro dispositivo)
2. Clique em "🚀 Consultar OID"
3. A resposta deve exibir o IP

---

## 🔍 Checklist de Funcionamento

Marque conforme conseguir executar cada etapa:

- [ ] Agente SNMP rodando na porta 16100
- [ ] Backend Flask rodando na porta 5000
- [ ] Frontend Vue.js rodando na porta 3000
- [ ] curl retorna JSON com valores SNMP
- [ ] Interface web carrega corretamente
- [ ] Botão "Consultar OID" retorna dados
- [ ] Histórico de consultas é exibido
- [ ] Múltiplos OIDs funcionam corretamente

---

## 🛠️ Troubleshooting

### **Problema: "Porta já em uso"**

```bash
# Encontrar e matar processo na porta
# Porta 16100 (Agente SNMP)
lsof -i :16100 | grep LISTEN
kill -9 <PID>

# Porta 5000 (Flask)
lsof -i :5000 | grep LISTEN
kill -9 <PID>

# Porta 3000 (Vue.js)
lsof -i :3000 | grep LISTEN
kill -9 <PID>
```

### **Problema: "Connection refused" ao acessar http://localhost:3000**

```bash
# Verificar se Vue.js está rodando
ps aux | grep "npm run dev"

# Se não estiver, reiniciar:
cd snmp-web && npm run dev
```

### **Problema: Backend retorna erro 500**

```bash
# Verificar se agente SNMP está rodando
ps aux | grep "discovery_snmp_agent.py"

# Verificar porta 16100
netstat -an | grep 16100

# Se não estiver rodando, reiniciar agente
```

### **Problema: OID retorna "Mock value"**

- O backend estava usando dados simulados
- Execute: `export SNMP_USE_MOCK=false` ou reinicie todos os serviços
- Certifique-se de que o agente SNMP está respondendo

### **Problema: Timeout na requisição**

```bash
# Aumentar timeout no Backend
# Editar snmp_manager.py linha 15:
# Mudar timeout=0.5 para timeout=2
```

---

## 📊 Resumo das Portas

| Serviço | Porta | Host | URL |
|---------|-------|------|-----|
| Agente SNMP | 16100 | 0.0.0.0 | N/A |
| Backend Flask | 5000 | 127.0.0.1 | http://localhost:5000 |
| Frontend Vue.js | 3000 | 127.0.0.1 | http://localhost:3000 |

---

## 🎓 Dicas Avançadas

### **Testar OID com timeout curto (curl)**

```bash
timeout 2 curl -v "http://127.0.0.1:5000/api/snmp/1.3.6.1.3.2025.1.1.0"
```

### **Redirecionar logs para arquivo**

```bash
# Backend
".venv/bin/python" snmp_manager.py > /tmp/flask.log 2>&1 &

# Agente
".venv/bin/python" discovery_snmp_agent.py > /tmp/agent.log 2>&1 &

# Vue.js
npm run dev > /tmp/vite.log 2>&1 &
```

### **Verificar se o agente está respondendo via snmpget**

```bash
# Instalar net-snmp (se disponível)
sudo apt install snmp

# Testar
snmpget -v 2c -c public 127.0.0.1:16100 1.3.6.1.3.2025.1.1.0
```

---

## 📞 Suporte

Se algum serviço não funcionar:

1. Verifique se está na pasta correta
2. Verifique se a porta não está em uso
3. Verifique os logs dos terminais
4. Reinicie todos os serviços
5. Verifique a conectividade (ping localhost)

**Sucesso! 🎉**
