import React from 'react'
import { motion } from 'framer-motion'
import { Crown, ChefHat, Calendar, Palette, Brain, Flame } from 'lucide-react'

const agentIcons = {
  odin: Crown,
  freya: ChefHat,
  saga: Calendar,
  loki: Palette,
  mimir: Brain,
  luci: Flame
}

const agentColors = {
  odin: 'text-agents-odin bg-agents-odin/10 border-agents-odin/20',
  freya: 'text-agents-freya bg-agents-freya/10 border-agents-freya/20',
  saga: 'text-agents-saga bg-agents-saga/10 border-agents-saga/20',
  loki: 'text-agents-loki bg-agents-loki/10 border-agents-loki/20',
  mimir: 'text-agents-mimir bg-agents-mimir/10 border-agents-mimir/20',
  luci: 'text-agents-luci bg-agents-luci/10 border-agents-luci/20'
}

const AgentInterface = ({ agents, selectedAgent, onAgentSelect }) => {
  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card-professional p-6"
      >
        <h2 className="heading-dynamic text-xl mb-6">
          Drone Collective
        </h2>
        
        <div className="space-y-3">
          {Object.entries(agents).map(([key, description]) => {
            const IconComponent = agentIcons[key] || Brain
            const isSelected = selectedAgent === key
            const colorClass = agentColors[key] || agentColors.odin
            
            return (
              <motion.button
                key={key}
                onClick={() => onAgentSelect(key)}
                className={`
                  w-full p-4 rounded-xl transition-all duration-300 border
                  ${isSelected 
                    ? 'bg-primary-50 border-primary-200 shadow-sm' 
                    : 'bg-white/60 border-neutral-200/60 hover:border-neutral-300/60 hover:bg-white'
                  }
                `}
                whileHover={{ scale: 1.01, y: -1 }}
                whileTap={{ scale: 0.99 }}
                layout
                style={{ backdropFilter: 'blur(10px)' }}
              >
                <div className="flex items-center space-x-4">
                  <div className={`
                    p-3 rounded-xl transition-all duration-200 relative
                    ${isSelected 
                      ? 'bg-white shadow-sm' 
                      : 'bg-neutral-100/60'
                    }
                  `}>
                    <IconComponent className={`w-5 h-5 ${
                      isSelected 
                        ? 'text-primary-600' 
                        : 'text-neutral-600'
                    }`} />
                    {isSelected && (
                      <div className="absolute -top-1 -right-1 w-3 h-3 bg-accent-500 rounded-full animate-pulse border-2 border-white"></div>
                    )}
                  </div>
                  <div className="text-left flex-1 relative group">
                    <div className={`font-semibold capitalize ${
                      isSelected ? 'text-neutral-900' : 'text-neutral-700'
                    }`} style={{ letterSpacing: '-0.01em' }}>
                      {key}
                    </div>
                    <div className={`text-sm font-medium ${
                      isSelected ? 'text-neutral-600' : 'text-neutral-500'
                    } break-words leading-tight`} style={{ letterSpacing: '-0.005em' }}>
                      {description}
                    </div>
                    
                    {/* Hover tooltip for full description */}
                    <div className="absolute left-0 top-full mt-2 px-3 py-2 bg-neutral-900 text-white text-sm rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-50 max-w-xs whitespace-normal">
                      {description}
                      <div className="absolute bottom-full left-4 w-0 h-0 border-l-4 border-r-4 border-b-4 border-transparent border-b-neutral-900"></div>
                    </div>
                  </div>
                </div>
              </motion.button>
            )
          })}
        </div>
      </motion.div>

    </div>
  )
}

export default AgentInterface