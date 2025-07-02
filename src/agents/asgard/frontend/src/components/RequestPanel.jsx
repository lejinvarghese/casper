import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Send, Sparkles, Loader2, Crown, ChefHat, Calendar, Palette, Brain, Flame } from 'lucide-react'

const RequestPanel = ({ selectedAgent, onSubmit, onAgentSelect, loading }) => {
  const [request, setRequest] = useState('')
  const [preset, setPreset] = useState('')

  const droneIcons = {
    odin: Crown,
    freya: ChefHat,
    saga: Calendar,
    loki: Palette,
    mimir: Brain,
    luci: Flame
  }

  const presets = [
    { text: 'Plan a perfect day in Toronto', agent: 'saga' },
    { text: 'Create a seasonal feast with Ontario ingredients', agent: 'freya' },
    { text: 'Design surreal artwork that breaks reality', agent: 'loki' },
    { text: 'Guide me toward my long-term cosmic purpose', agent: 'mimir' },
    { text: 'Suggest something deliciously mischievous', agent: 'luci' },
    { text: 'Coordinate the full swarm for complex planning', agent: 'odin' }
  ]

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!request.trim()) return
    
    onSubmit({
      request: request.trim(),
      agent: selectedAgent
    })
  }

  const handlePresetSelect = (preset) => {
    setRequest(preset.text)
    setPreset(preset.text)
    // First select the corresponding agent
    if (onAgentSelect && preset.agent) {
      onAgentSelect(preset.agent)
    }
    // Also submit the request with the appropriate agent
    onSubmit({
      request: preset.text,
      agent: preset.agent
    })
  }

  return (
    <div className="space-y-6">
      {/* Request Input */}
      <motion.div
        className="card-professional p-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="relative">
            <textarea
              value={request}
              onChange={(e) => setRequest(e.target.value)}
              placeholder="What would you like assistance with today?"
              className="w-full h-32 input-professional resize-none text-sm"
              rows={4}
            />
            {request && (
              <motion.div
                className="absolute bottom-4 right-4"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
              >
                <Sparkles className="w-4 h-4 text-primary-500" />
              </motion.div>
            )}
          </div>

          <div className="flex justify-end">
            <motion.button
              type="submit"
              disabled={!request.trim() || loading}
              className="btn-professional disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              whileHover={{ scale: loading ? 1 : 1.01, y: loading ? 0 : -1 }}
              whileTap={{ scale: loading ? 1 : 0.99 }}
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Processing</span>
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  <span>Execute</span>
                </>
              )}
            </motion.button>
          </div>
        </form>
      </motion.div>

      {/* Quick Presets */}
      <motion.div
        className="card-professional p-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <h3 className="heading-dynamic text-lg mb-4">
          Quick Suggestions
        </h3>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {presets.map((preset, index) => {
            const DroneIcon = droneIcons[preset.agent] || Brain
            const isSelected = selectedAgent === preset.agent
            return (
              <motion.button
                key={index}
                onClick={() => handlePresetSelect(preset)}
                className={`
                  p-4 text-left rounded-xl transition-all duration-200 text-sm font-medium border relative
                  ${isSelected 
                    ? 'bg-accent-50 border-accent-200 text-accent-800' 
                    : 'bg-white/60 border-neutral-200/60 hover:border-neutral-300/60 hover:bg-white text-neutral-700'
                  }
                `}
                whileHover={{ scale: 1.01, y: -1 }}
                whileTap={{ scale: 0.99 }}
                style={{ backdropFilter: 'blur(10px)' }}
              >
                <div className="flex items-start space-x-3">
                  <div className={`p-1.5 rounded-lg flex-shrink-0 ${
                    isSelected ? 'bg-accent-200' : 'bg-neutral-200/60'
                  }`}>
                    <DroneIcon className={`w-3 h-3 ${
                      isSelected ? 'text-accent-700' : 'text-neutral-600'
                    }`} />
                  </div>
                  <div className="flex-1">
                    <span className="block text-professional" style={{ letterSpacing: '-0.01em' }}>
                      {preset.text}
                    </span>
                    <span className={`text-xs capitalize mt-1 block font-medium ${
                      isSelected ? 'text-accent-600' : 'text-neutral-500'
                    }`} style={{ letterSpacing: '-0.005em' }}>
                      via {preset.agent}
                    </span>
                  </div>
                </div>
                {isSelected && (
                  <div className="absolute top-2 right-2 w-2 h-2 bg-accent-500 rounded-full animate-pulse"></div>
                )}
              </motion.button>
            )
          })}
        </div>
      </motion.div>
    </div>
  )
}

export default RequestPanel