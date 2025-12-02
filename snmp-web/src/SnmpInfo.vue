<template>
  <div class="snmp-info-container">
    <div class="snmp-card">
      <h1>🔍 Consultor SNMP</h1>
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
        <span v-if="!loading">🚀 Consultar OID</span>
        <span v-else>⏳ Consultando...</span>
      </button>

      <div v-if="loading" class="spinner"></div>

      <!-- Resultado de sucesso -->
      <div v-if="result && !error" class="result-container success">
        <h2>✅ Resultado</h2>
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
        <h2>❌ Erro</h2>
        <div class="error-message">{{ error }}</div>
        <div v-if="errorDetails" class="error-details">
          <strong>Detalhes:</strong> {{ errorDetails }}
        </div>
      </div>

      <!-- Histórico -->
      <div v-if="history.length > 0" class="history-container">
        <h3>📋 Histórico de Consultas</h3>
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
.snmp-info-container {
  padding: 20px;
}

.snmp-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  padding: 40px;
}

h1 {
  color: #667eea;
  margin-bottom: 10px;
  font-size: 28px;
}

.subtitle {
  color: #666;
  margin-bottom: 30px;
  font-size: 14px;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  color: #333;
  font-weight: 600;
  font-size: 14px;
}

.input-field {
  width: 100%;
  padding: 12px;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.3s ease;
}

.input-field:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.info-text {
  display: block;
  margin-top: 5px;
  color: #999;
  font-size: 12px;
}

.btn-primary {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 20px;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  animation: spin 1s linear infinite;
  margin: 20px auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.result-container {
  margin: 20px 0;
  padding: 20px;
  border-radius: 8px;
  border-left: 4px solid;
}

.result-container.success {
  background: #f0fdf4;
  border-left-color: #22c55e;
}

.result-container.error {
  background: #fef2f2;
  border-left-color: #ef4444;
}

.result-container h2 {
  font-size: 18px;
  margin-bottom: 15px;
}

.result-container.success h2 {
  color: #22c55e;
}

.result-container.error h2 {
  color: #ef4444;
}

.result-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.result-item:last-child {
  border-bottom: none;
}

.label {
  font-weight: 600;
  color: #333;
}

.value {
  color: #666;
  word-break: break-all;
}

.error-message {
  color: #dc2626;
  font-weight: 600;
  margin-bottom: 10px;
}

.error-details {
  color: #666;
  font-size: 14px;
  background: rgba(0, 0, 0, 0.05);
  padding: 10px;
  border-radius: 4px;
  margin-top: 10px;
}

.history-container {
  margin-top: 30px;
  padding-top: 30px;
  border-top: 2px solid #e0e0e0;
}

.history-container h3 {
  color: #333;
  margin-bottom: 15px;
  font-size: 16px;
}

.history-list {
  list-style: none;
  margin-bottom: 15px;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: #f9f9f9;
  border-radius: 4px;
  margin-bottom: 8px;
  font-size: 13px;
}

.history-oid {
  color: #667eea;
  font-family: 'Courier New', monospace;
  flex: 1;
  word-break: break-all;
}

.history-status {
  margin-left: 10px;
  font-weight: 600;
}

.history-status.success {
  color: #22c55e;
}

.history-status.error {
  color: #ef4444;
}

.btn-secondary {
  width: 100%;
  padding: 10px;
  background: #e0e0e0;
  color: #333;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-secondary:hover {
  background: #d0d0d0;
}

@media (max-width: 600px) {
  .snmp-card {
    padding: 20px;
  }

  h1 {
    font-size: 24px;
  }
}
</style>
