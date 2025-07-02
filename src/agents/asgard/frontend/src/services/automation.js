/**
 * Automation Service
 * Handles API calls for the ambient intelligence system
 */

const API_BASE = 'http://localhost:8000'

class AutomationService {
  async getStatus() {
    const response = await fetch(`${API_BASE}/automations/status`)
    if (!response.ok) {
      throw new Error(`Failed to get automation status: ${response.statusText}`)
    }
    return response.json()
  }

  async getRecent(hours = 24) {
    const response = await fetch(`${API_BASE}/automations/recent?hours=${hours}`)
    if (!response.ok) {
      throw new Error(`Failed to get recent automations: ${response.statusText}`)
    }
    return response.json()
  }

  async toggle(automationId, enabled) {
    const response = await fetch(`${API_BASE}/automations/${automationId}/toggle?enabled=${enabled}`, {
      method: 'POST'
    })
    if (!response.ok) {
      throw new Error(`Failed to toggle automation: ${response.statusText}`)
    }
    return response.json()
  }

  async trigger(automationId) {
    const response = await fetch(`${API_BASE}/automations/${automationId}/trigger`, {
      method: 'POST'
    })
    if (!response.ok) {
      throw new Error(`Failed to trigger automation: ${response.statusText}`)
    }
    return response.json()
  }

  async getDetails(automationId) {
    const response = await fetch(`${API_BASE}/automations/${automationId}`)
    if (!response.ok) {
      throw new Error(`Failed to get automation details: ${response.statusText}`)
    }
    return response.json()
  }
}

export const automationService = new AutomationService()