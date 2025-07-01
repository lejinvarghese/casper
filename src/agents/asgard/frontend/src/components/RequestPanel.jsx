import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Send, Sparkles, Loader2 } from 'lucide-react'

const RequestPanel = ({ selectedAgent, onSubmit, loading }) => {
  const [request, setRequest] = useState('')
  const [preset, setPreset] = useState('')

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
        className="card p-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="relative">
            <textarea
              value={request}
              onChange={(e) => setRequest(e.target.value)}
              placeholder="What would you like assistance with today?"
              className="w-full h-32 input-modern resize-none"
              rows={4}
            />
            {request && (
              <motion.div
                className="absolute bottom-4 right-4"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
              >
                <Sparkles className="w-4 h-4 text-agents-odin" />
              </motion.div>
            )}
          </div>

          <div className="flex justify-end">
            <motion.button
              type="submit"
              disabled={!request.trim() || loading}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              whileHover={{ scale: loading ? 1 : 1.02, y: loading ? 0 : -1 }}
              whileTap={{ scale: loading ? 1 : 0.98 }}
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
        className="card p-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <h3 className="font-display text-lg font-medium text-neutral-900 mb-4">
          Quick Suggestions
        </h3>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {presets.map((preset, index) => (
            <motion.button
              key={index}
              onClick={() => handlePresetSelect(preset)}
              className={`
                p-4 text-left rounded-xl transition-all duration-200 text-sm font-medium border relative
                ${preset.text === request 
                  ? 'bg-agents-odin/10 border-agents-odin/30 text-agents-odin' 
                  : 'bg-neutral-50 border-neutral-200 hover:border-neutral-300 hover:bg-neutral-100 text-neutral-700'
                }
              `}
              whileHover={{ scale: 1.02, y: -1 }}
              whileTap={{ scale: 0.98 }}
            >
              <div className="flex items-start justify-between">
                <span className="flex-1">{preset.text}</span>
                {preset.agent && (
                  <span className="text-xs text-neutral-500 ml-2 capitalize">
                    {preset.agent}
                  </span>
                )}
              </div>
            </motion.button>
          ))}
        </div>
      </motion.div>
    </div>
  )
}

export default RequestPanel