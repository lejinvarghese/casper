import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Sparkles, Brain, Cpu, Zap } from 'lucide-react'
import AgentInterface from './components/AgentInterface'
import RequestPanel from './components/RequestPanel'
import ResponseDisplay from './components/ResponseDisplay'
import ConfigPanel from './components/ConfigPanel'
import { apiService } from './services/api'

function App() {
  const [agents, setAgents] = useState({})
  const [selectedAgent, setSelectedAgent] = useState(null)
  const [request, setRequest] = useState('')
  const [response, setResponse] = useState(null)
  const [loading, setLoading] = useState(false)
  const [config, setConfig] = useState({
    theme: 'citadel',
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
    } catch (error) {
      setResponse({ 
        success: false, 
        error: error.message || 'Request failed' 
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-purple-50/20 relative overflow-hidden">
      {/* Asgard Citadel Background */}
      <div className="fixed inset-0 pointer-events-none">
        {/* Diamond Tower Silhouette - Responsive */}
        <div className="absolute bottom-0 right-0 w-48 h-48 sm:w-64 sm:h-64 lg:w-80 lg:h-80 xl:w-96 xl:h-96 opacity-8 lg:opacity-10">
          <svg viewBox="0 0 200 300" className="w-full h-full text-slate-600">
            <defs>
              <linearGradient id="towerGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="currentColor" stopOpacity="0.3" />
                <stop offset="50%" stopColor="currentColor" stopOpacity="0.1" />
                <stop offset="100%" stopColor="currentColor" stopOpacity="0.05" />
              </linearGradient>
            </defs>
            {/* Main tower body */}
            <polygon 
              points="100,50 120,80 120,250 80,250 80,80" 
              fill="url(#towerGradient)"
              stroke="currentColor" 
              strokeWidth="0.5"
              opacity="0.6"
            />
            {/* Diamond top */}
            <polygon 
              points="100,20 85,50 115,50" 
              fill="url(#towerGradient)"
              stroke="currentColor" 
              strokeWidth="0.5"
              opacity="0.8"
            />
            {/* Tower details */}
            <rect x="85" y="100" width="30" height="4" fill="currentColor" opacity="0.3" />
            <rect x="85" y="130" width="30" height="4" fill="currentColor" opacity="0.3" />
            <rect x="85" y="160" width="30" height="4" fill="currentColor" opacity="0.3" />
            <rect x="85" y="190" width="30" height="4" fill="currentColor" opacity="0.3" />
          </svg>
        </div>
        
        {/* Floating crystalline elements - Responsive positioning */}
        <motion.div
          className="absolute top-10 right-16 w-4 h-4 sm:top-20 sm:right-32 sm:w-6 sm:h-6 lg:w-8 lg:h-8"
          animate={{
            y: [0, -20, 0],
            rotate: [0, 180, 360],
            scale: [1, 1.1, 1],
          }}
          transition={{
            duration: 12,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        >
          <svg viewBox="0 0 24 24" className="w-full h-full text-blue-300/30 lg:text-blue-300/40">
            <polygon points="12,2 22,12 12,22 2,12" fill="currentColor" />
          </svg>
        </motion.div>
        
        <motion.div
          className="absolute bottom-16 left-16 w-3 h-3 sm:bottom-32 sm:left-32 sm:w-4 sm:h-4 lg:w-6 lg:h-6"
          animate={{
            y: [0, 15, 0],
            rotate: [360, 180, 0],
            scale: [1, 0.9, 1],
          }}
          transition={{
            duration: 15,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        >
          <svg viewBox="0 0 24 24" className="w-full h-full text-purple-300/30 lg:text-purple-300/40">
            <polygon points="12,2 22,12 12,22 2,12" fill="currentColor" />
          </svg>
        </motion.div>
        
        <motion.div
          className="absolute top-20 left-8 w-3 h-3 sm:top-40 sm:left-20 sm:w-4 sm:h-4"
          animate={{
            y: [0, -10, 0],
            rotate: [0, 90, 180],
            scale: [1, 1.2, 1],
          }}
          transition={{
            duration: 18,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        >
          <svg viewBox="0 0 24 24" className="w-full h-full text-rose-300/30 lg:text-rose-300/40">
            <polygon points="12,2 22,12 12,22 2,12" fill="currentColor" />
          </svg>
        </motion.div>

        {/* Subtle light rays - Responsive */}
        <div className="absolute top-0 right-0 w-full h-full">
          <div className="absolute top-10 right-10 w-0.5 h-16 sm:top-20 sm:right-20 sm:w-1 sm:h-32 bg-gradient-to-b from-blue-200/15 to-transparent rotate-12 blur-sm"></div>
          <div className="absolute top-20 right-16 w-0.5 h-12 sm:top-40 sm:right-32 sm:w-1 sm:h-24 bg-gradient-to-b from-purple-200/15 to-transparent rotate-45 blur-sm"></div>
          <div className="absolute top-30 right-12 w-0.5 h-10 sm:top-60 sm:right-24 sm:w-1 sm:h-20 bg-gradient-to-b from-rose-200/15 to-transparent rotate-75 blur-sm"></div>
        </div>
      </div>

      {/* Header */}
      <motion.header 
        className="relative z-10 p-6"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <motion.div
              className="p-3 bg-white border border-neutral-200 rounded-2xl shadow-sm"
              whileHover={{ scale: 1.05, y: -2 }}
              whileTap={{ scale: 0.95 }}
            >
              <Zap className="w-8 h-8 text-agents-odin" />
            </motion.div>
            <div>
              <h1 className="font-display text-3xl text-neutral-900 font-bold">
                Asgard Citadel
              </h1>
              <p className="text-neutral-500 text-sm font-medium">
                Drone Swarm Command
              </p>
            </div>
          </div>
          
          <ConfigPanel config={config} onConfigChange={setConfig} />
        </div>
      </motion.header>

      {/* Main Content */}
      <main className="relative z-10 max-w-7xl mx-auto px-6 pb-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Agent Selection */}
          <motion.div
            className="lg:col-span-1"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <AgentInterface
              agents={agents}
              selectedAgent={selectedAgent}
              onAgentSelect={setSelectedAgent}
            />
          </motion.div>

          {/* Request & Response */}
          <div className="lg:col-span-2 space-y-6">
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
            >
              <RequestPanel
                selectedAgent={selectedAgent}
                onSubmit={handleRequest}
                loading={loading}
              />
            </motion.div>

            <AnimatePresence>
              {response && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.4 }}
                >
                  <ResponseDisplay response={response} />
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </main>
    </div>
  )
}

export default App