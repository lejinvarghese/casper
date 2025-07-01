import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const apiService = {
  async getAgents() {
    const response = await api.get('/drones')
    return response.data
  },

  async submitRequest(requestData) {
    // Map frontend 'agent' to backend 'drone' parameter
    const backendData = {
      request: requestData.request,
      drone: requestData.agent,
      verbose: requestData.verbose || false
    }
    console.log('Sending request to backend:', backendData) // Debug log
    const response = await api.post('/request', backendData)
    return response.data
  },

  async configure(config) {
    const response = await api.post('/configure', config)
    return response.data
  },

  async healthCheck() {
    const response = await api.get('/health')
    return response.data
  }
}

export default api