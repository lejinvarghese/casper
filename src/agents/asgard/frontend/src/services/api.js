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
    console.log('🚀 Sending request to backend:', backendData) // Debug log
    const response = await api.post('/request', backendData)
    console.log('📥 Received response from backend:', response.data) // Debug log
    console.log('📥 Steps in response:', response.data.steps) // Debug log
    console.log('📥 Steps type:', typeof response.data.steps) // Debug log
    return response.data
  },

  streamAgentExecution(requestData, onStep, onComplete, onError) {
    const eventSource = new EventSource(`${API_BASE_URL}/stream-request`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        request: requestData.request,
        drone: requestData.agent,
        verbose: true
      })
    })

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'step') {
          onStep(data.step)
        } else if (data.type === 'complete') {
          onComplete(data.result)
          eventSource.close()
        }
      } catch (error) {
        onError(error)
      }
    }

    eventSource.onerror = (error) => {
      onError(error)
      eventSource.close()
    }

    return eventSource
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