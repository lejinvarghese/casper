import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Sparkles, Brain, Cpu, Zap } from 'lucide-react'
import ConfigPanel from './components/ConfigPanel'
import TabNavigation from './components/TabNavigation'
import CustomInteractions from './components/CustomInteractions'
import AmbientIntelligenceTab from './components/AmbientIntelligenceTab'
import { apiService } from './services/api'
import { automationService } from './services/automation'

function App() {
  const [agents, setAgents] = useState({})
  const [selectedAgent, setSelectedAgent] = useState(null)
  const [request, setRequest] = useState('')
  const [response, setResponse] = useState(null)
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('interact')
  const [config, setConfig] = useState({
    theme: 'asgard',
    verbose: false
  })

  useEffect(() => {
    loadAgents()
  }, [])

  const loadAgents = async () => {
    try {
      const data = await apiService.getAgents()
      setAgents(data.drones)
    } catch (error) {
      console.error('Failed to load agents:', error)
    }
  }

  const handleRequest = async (requestData) => {
    setLoading(true)
    try {
      const result = await apiService.submitRequest({
        request: requestData.request,
        agent: requestData.agent,
        verbose: config.verbose
      })
      setResponse(result)
      return result  // Return the result for CustomInteractions
    } catch (error) {
      const errorResponse = { 
        success: false, 
        error: error.message || 'Request failed' 
      }
      setResponse(errorResponse)
      return errorResponse  // Return error response
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-neutral-25 minimal-pattern relative overflow-hidden">
      {/* Subtle Professional Background */}
      <div className="fixed inset-0 pointer-events-none">
        {/* Minimal geometric elements */}
        <div className="absolute top-1/4 right-1/4 w-64 h-64 opacity-[0.02]">
          <svg viewBox="0 0 200 200" className="w-full h-full text-neutral-600">
            <circle cx="100" cy="100" r="80" fill="none" stroke="currentColor" strokeWidth="1"/>
            <circle cx="100" cy="100" r="40" fill="none" stroke="currentColor" strokeWidth="0.5"/>
            <line x1="60" y1="100" x2="140" y2="100" stroke="currentColor" strokeWidth="0.5"/>
            <line x1="100" y1="60" x2="100" y2="140" stroke="currentColor" strokeWidth="0.5"/>
          </svg>
        </div>
        
        <div className="absolute bottom-1/4 left-1/4 w-48 h-48 opacity-[0.015] rotate-45">
          <svg viewBox="0 0 200 200" className="w-full h-full text-neutral-600">
            <rect x="50" y="50" width="100" height="100" fill="none" stroke="currentColor" strokeWidth="1"/>
            <rect x="75" y="75" width="50" height="50" fill="none" stroke="currentColor" strokeWidth="0.5"/>
          </svg>
        </div>
      </div>

      {/* Header */}
      <motion.header 
        className="relative z-10 p-8"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <motion.div
                className="p-3 surface-professional rounded-2xl shadow-sm"
                whileHover={{ scale: 1.02, y: -1 }}
                whileTap={{ scale: 0.98 }}
              >
                <Zap className="w-7 h-7 text-primary-600" />
              </motion.div>
              <div>
                <h1 className="font-display text-3xl text-neutral-900 font-bold">
                  Asgard
                </h1>
                <p className="text-professional-muted text-sm">
                  Neural Command Center
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-6">
              <TabNavigation activeTab={activeTab} onTabChange={setActiveTab} />
              <ConfigPanel config={config} onConfigChange={setConfig} />
            </div>
          </div>
        </div>
      </motion.header>

      {/* Main Content */}
      <main className="relative z-10 max-w-7xl mx-auto px-6 pb-12">
        <AnimatePresence mode="wait">
          {activeTab === 'interact' && (
            <motion.div
              key="interact"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.4 }}
            >
              <CustomInteractions
                agents={agents}
                selectedAgent={selectedAgent}
                onAgentSelect={setSelectedAgent}
                onSubmit={handleRequest}
                response={response}
                loading={loading}
              />
            </motion.div>
          )}
          
          {activeTab === 'ambient' && (
            <motion.div
              key="ambient"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.4 }}
            >
              <AmbientIntelligenceTab automationService={automationService} />
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  )
}

export default App