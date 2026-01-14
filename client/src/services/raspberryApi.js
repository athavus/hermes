import axios from 'axios';

// Detecta automaticamente o hostname atual (funciona mesmo mudando de rede/IP)
// Esta função detecta o hostname do navegador e usa a porta 8000 para a API
// Exemplo: se você acessa http://192.168.130.9:5173, a API será http://192.168.130.9:8000
// Se mudar para outra rede com IP 192.168.1.50, automaticamente usará http://192.168.1.50:8000
const getApiBaseURL = () => {
  // Agora usamos um proxy do Vite para evitar TODOS os problemas de CORS e IP
  // As requisições que começam com /api (definidas nos serviços abaixo) 
  // serão redirecionadas automaticamente para o backend pelo Vite
  if (typeof window !== 'undefined') {
    return ''; // Caminho relativo (mesmo host da interface)
  }
  return 'http://127.0.0.1:8000'; // Fallback fora do browser
};

// Configuração base da API
const api = axios.create({
  baseURL: getApiBaseURL(),
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Cria um cliente axios para um host específico (ex.: 192.168.130.166)
const apiForHost = (hostWithOptionalPort) => {
  const base = hostWithOptionalPort.startsWith('http')
    ? hostWithOptionalPort
    : `http://${hostWithOptionalPort}`;
  // Garante porta 8000 quando nenhuma porta foi informada
  let url;
  try {
    const u = new URL(base);
    if (!u.port) {
      u.port = '8000';
    }
    url = u.toString().replace(/\/$/, '');
  } catch (e) {
    url = base; // fallback
  }
  const instance = axios.create({
    baseURL: url,
    timeout: 10000,
    headers: { 'Content-Type': 'application/json' }
  });
  instance.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response) console.error('Erro na API (host override):', error.response.data);
      else if (error.request) console.error('Erro de rede (host override):', error.request);
      return Promise.reject(error);
    }
  );
  return instance;
};

// Interceptor para tratamento de erros
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      console.error('Erro na API:', error.response.data);
    } else if (error.request) {
      console.error('Erro de rede:', error.request);
    }
    return Promise.reject(error);
  }
);

// ============= SERVIÇOS DE STATUS DOS DISPOSITIVOS =============
export const deviceService = {
  // Buscar status de todos os dispositivos
  getAllDevices: async () => {
    const response = await api.get('/api/devices/status');
    return response.data;
  },

  // Buscar status de um dispositivo específico
  getDevice: async (raspberryId) => {
    const response = await api.get(`/api/devices/${raspberryId}/status`);
    return response.data;
  },

  // Buscar histórico de status de um dispositivo
  getDeviceHistory: async (raspberryId, hours = 24) => {
    const response = await api.get(`/api/devices/${raspberryId}/status/history`, {
      params: { hours }
    });
    return response.data;
  }
};

// ============= SERVIÇOS DE DADOS EM TEMPO REAL =============
export const realtimeService = {
  // Buscar dados em tempo real
  getData: async (limit = 50) => {
    const response = await api.get('/api/data/realtime', {
      params: { limit }
    });
    return response.data;
  },

  // Enviar dados manualmente (para testes/debug)
  postData: async (data) => {
    const response = await api.post('/api/data', data);
    return response.data;
  }
};

// ============= EXPORT =============
export const exportService = {
  downloadDatabaseZip: async () => {
    const response = await api.get('/api/export/db.zip', { responseType: 'blob' });
    return response.data; // Blob (zip)
  }
};

// ============= SERVIÇOS DE HEALTH CHECK =============
export const healthService = {
  // Root endpoint (info da API)
  getRoot: async () => {
    const response = await api.get('/');
    return response.data;
  },

  // Health check completo
  checkHealth: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  // Estatísticas
  getStats: async () => {
    const response = await api.get('/api/stats');
    return response.data;
  }
};

export default api;


