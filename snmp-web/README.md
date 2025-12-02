# SNMP Web Interface

Aplicação Vue.js 3 para consultar OIDs do agente SNMP local através da API Flask.

## ⚙️ Instalação

```bash
npm install
```

## 🚀 Desenvolvimento

Certifique-se de que o backend Flask está rodando em `http://localhost:5000`:

```bash
# Terminal 1: Executar o backend Flask
cd ..
python snmp_manager.py

# Terminal 2: Executar o servidor de desenvolvimento Vue
npm run dev
```

O servidor estará disponível em `http://localhost:3000`

## 🏗️ Build para Produção

```bash
npm run build
```

Os arquivos compilados estarão em `dist/`

## 📋 Funcionalidades

- ✅ Consulta de OIDs SNMP
- ✅ Configuração de Host, Porta e Community
- ✅ Interface intuitiva e responsiva
- ✅ Histórico de consultas (últimas 10)
- ✅ Tratamento de erros com mensagens descritivas
- ✅ Design moderno com gradientes

## 🔍 Como Usar

1. Insira um OID válido (ex: `1.3.6.1.2.1.1.1.0`)
2. Opcionalmente, customize host, porta e community
3. Clique em "🚀 Consultar OID"
4. O resultado será exibido imediatamente

## 📚 OIDs Comuns

- `1.3.6.1.2.1.1.1.0` - Descrição do Sistema
- `1.3.6.1.2.1.1.2.0` - Object ID
- `1.3.6.1.2.1.1.3.0` - Uptime
- `1.3.6.1.2.1.1.4.0` - Contact
- `1.3.6.1.2.1.1.5.0` - Name

## 🔗 Dependências

- **Vue.js 3** - Framework progressivo
- **Vite** - Build tool moderno
- **Axios** - Cliente HTTP
