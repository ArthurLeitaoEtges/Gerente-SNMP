<template>
  <div class="snmp-info-container">
    <div class="snmp-card">
      <h1>Consultor SNMP</h1>
      <p class="subtitle">Consulte valores de OIDs no agente SNMP local</p>

      <div class="form-group">
        <label for="oid-input">OID:</label>
        <input
          id="oid-input"
          v-model="oid"
          type="text"
          placeholder="Ex: 1.3.6.1.2.1.1.1.0"
          @keyup.enter="querySnmp"
          class="input-field"
        />
        <small class="info-text">
          OID padrão: 1.3.6.1.2.1.1.1.0 (sysDescr)
        </small>
      </div>

      <div class="form-group">
        <label for="host-input">Host (opcional):</label>
        <input
          id="host-input"
          v-model="host"
          type="text"
          placeholder="Ex: 127.0.0.1"
          class="input-field"
        />
      </div>

      <div class="form-group">
        <label for="port-input">Porta (opcional):</label>
        <input
          id="port-input"
          v-model.number="port"
          type="number"
          placeholder="Ex: 16100"
          class="input-field"
        />
      </div>

      <div class="form-group">
        <label for="community-input">Community (opcional):</label>
        <input
          id="community-input"
          v-model="community"
          type="text"
          placeholder="Ex: public"
          class="input-field"
        />
      </div>

      <button @click="querySnmp" :disabled="loading" class="btn-primary">
        <span v-if="!loading"> Consultar OID</span>
        <span v-else>Consultando...</span>
      </button>

      <div v-if="loading" class="spinner"></div>

      <!-- Resultado de sucesso -->
      <div v-if="result && !error" class="result-container success">
        <h2>Resultado</h2>
        <div class="result-item">
          <span class="label">OID:</span>
          <span class="value">{{ result.oid }}</span>
        </div>
        <div class="result-item">
          <span class="label">Valor:</span>
          <span class="value">{{ result.value }}</span>
        </div>
        <div class="result-item">
          <span class="label">Host:</span>
          <span class="value">{{ result.host }}:{{ result.port }}</span>
        </div>
      </div>

      <!-- Resultado de erro -->
      <div v-if="error" class="result-container error">
        <h2>Erro</h2>
        <div class="error-message">{{ error }}</div>
        <div v-if="errorDetails" class="error-details">
          <strong>Detalhes:</strong> {{ errorDetails }}
        </div>
      </div>

      <!-- Histórico -->
      <div v-if="history.length > 0" class="history-container">
        <h3>Histórico de Consultas</h3>
        <ul class="history-list">
          <li v-for="(item, index) in history" :key="index" class="history-item">
            <span class="history-oid">{{ item.oid }}</span>
            <span class="history-status" :class="item.success ? 'success' : 'error'">
              {{ item.success ? '✓' : '✗' }}
            </span>
          </li>
        </ul>
        <button @click="clearHistory" class="btn-secondary">Limpar Histórico</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'SnmpInfo',
  data() {
    return {
      oid: '1.3.6.1.2.1.1.1.0',
      host: '127.0.0.1',
      port: 16100,
      community: 'public',
      result: null,
      error: null,
      errorDetails: null,
      loading: false,
      history: []
    }
  },
  methods: {
    async querySnmp() {
      if (!this.oid.trim()) {
        this.error = 'Por favor, insira um OID válido'
        this.result = null
        return
      }

      this.loading = true
      this.error = null
      this.errorDetails = null
      this.result = null

      try {
        // Construir query params
        let url = `http://localhost:5000/api/snmp/${encodeURIComponent(this.oid)}`
        const params = new URLSearchParams()
        
        if (this.host !== '127.0.0.1') params.append('host', this.host)
        if (this.port !== 16100) params.append('port', this.port)
        if (this.community !== 'public') params.append('community', this.community)

        if (params.toString()) {
          url += '?' + params.toString()
        }

        const response = await axios.get(url)
        
        this.result = response.data
        this.error = null

        // Adicionar ao histórico
        this.history.unshift({
          oid: this.oid,
          success: true,
          timestamp: new Date().toLocaleTimeString('pt-BR')
        })

        if (this.history.length > 10) {
          this.history.pop()
        }
      } catch (err) {
        this.error = 'Erro ao consultar o OID'
        this.result = null

        if (err.response) {
          this.errorDetails = err.response.data?.details || err.response.statusText
        } else if (err.request) {
          this.errorDetails = 'Sem resposta do servidor. Certifique-se de que o backend Flask está rodando em http://localhost:5000'
        } else {
          this.errorDetails = err.message
        }

        // Adicionar ao histórico
        this.history.unshift({
          oid: this.oid,
          success: false,
          timestamp: new Date().toLocaleTimeString('pt-BR')
        })

        if (this.history.length > 10) {
          this.history.pop()
        }
      } finally {
        this.loading = false
      }
    },
    clearHistory() {
      this.history = []
    }
  }
}
</script>

<style scoped>

/* ===== CONTAINER GERAL ===== */
.snmp-info-container {
  padding: 30px;
  background: #0b0f17;
  min-height: 100vh;
  font-family: "Inter", sans-serif;
}

/* ===== CARD PRINCIPAL ===== */
.snmp-card {
  background: #121826;
  border-radius: 14px;
  padding: 40px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.45);
  border: 1px solid rgba(0, 255, 255, 0.06);
}

/* ===== TÍTULOS ===== */
h1 {
  color: #00db8bff;
  font-size: 30px;
  font-weight: 700;
  margin-bottom: 5px;
  letter-spacing: 0.5px;
}

.subtitle {
  color: #8aa0b4;
  margin-bottom: 35px;
  font-size: 14px;
}

/* ===== FORMS ===== */
.form-group {
  margin-bottom: 22px;
}

label {
  display: block;
  margin-bottom: 8px;
  color: #c7d4e0;
  font-size: 14px;
  font-weight: 600;
}

/* INPUTS estilo NETDATA */
.input-field {
  width: 100%;
  padding: 14px;
  background: #0f1724;
  border: 1px solid #1a2638;
  border-radius: 8px;
  font-size: 14px;
  color: #e0e8f0;
  transition: 0.25s;
}

.input-field:focus {
  outline: none;
  border-color: #00db8bff;
  box-shadow: 0 0 10px rgba(0, 225, 255, 0.4);
}

.info-text {
  margin-top: 5px;
  color: #7c8897;
  font-size: 12px;
}

/* ===== BOTÃO PRIMÁRIO estilo NETDATA ===== */
.btn-primary {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #00db8bff 0%, #00db8bff 100%);
  color: #0b0f17;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: 0.3s;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(0, 255, 210, 0.4);
}

.btn-primary:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* ===== SPINNER ===== */
.spinner {
  border: 4px solid rgba(255, 255, 255, 0.1);
  border-top: 4px solid #00db8bff;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  animation: spin 1s linear infinite;
  margin: 20px auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* ===== RESULTADOS (SUCCESS / ERROR) ===== */
.result-container {
  margin: 25px 0;
  padding: 22px;
  border-radius: 10px;
  border-left: 4px solid;
}

.result-container.success {
  background: rgba(0, 255, 150, 0.05);
  border-left-color: #00ffa3;
}

.result-container.error {
  background: rgba(255, 60, 60, 0.06);
  border-left-color: #ff4f4f;
}

.result-container h2 {
  font-size: 18px;
  margin-bottom: 15px;
}

.result-container.success h2 {
  color: #00ffa3;
}

.result-container.error h2 {
  color: #ff6666;
}

/* Resultado item */
.result-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.result-item:last-child {
  border-bottom: none;
}

.label {
  color: #dce3eb;
  font-weight: 600;
}

.value {
  color: #8aa0b4;
  word-break: break-all;
}

/* ===== ERROS DETALHADOS ===== */
.error-message {
  color: #ff4f4f;
  font-weight: 700;
}

.error-details {
  color: #c9d2df;
  font-size: 14px;
  background: #1a2333;
  padding: 12px;
  border-radius: 6px;
  margin-top: 10px;
}

/* ===== HISTÓRICO ===== */
.history-container {
  margin-top: 35px;
  padding-top: 30px;
  border-top: 1px solid rgba(255, 255, 255, 0.07);
}

.history-container h3 {
  color: #00db8bff;
  margin-bottom: 15px;
  font-size: 17px;
  font-weight: 600;
}

.history-list {
  list-style: none;
  margin-bottom: 15px;
}

.history-item {
  padding: 12px;
  border-radius: 6px;
  background: #0f1724;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #d0d8e3;
  margin-bottom: 8px;
  font-size: 13px;
}

.history-oid {
  color: #00ffa3;
  font-family: "Courier New", monospace;
  flex: 1;
  word-break: break-all;
}

.history-status {
  margin-left: 10px;
  font-weight: 700;
}

.history-status.success {
  color: #00ffa3;
}

.history-status.error {
  color: #ff4f4f;
}

/* ===== BOTÃO SECUNDÁRIO ===== */
.btn-secondary {
  width: 100%;
  padding: 12px;
  background: #1a2333;
  color: #9fb5cc;
  border: 1px solid #233044;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: 0.2s;
}

.btn-secondary:hover {
  background: #243044;
  border-color: #2e4057;
}

/* ===== RESPONSIVO ===== */
@media (max-width: 600px) {
  .snmp-card {
    padding: 22px;
  }

  h1 {
    font-size: 26px;
  }
}

</style>
