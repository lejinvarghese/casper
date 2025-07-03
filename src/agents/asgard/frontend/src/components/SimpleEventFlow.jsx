import React from 'react'
import { motion } from 'framer-motion'
import { Crown, ChefHat, Calendar, Palette, Brain, Flame, Zap, ArrowDown } from 'lucide-react'

const droneIcons = {
  odin: Crown,
  freya: ChefHat,
  saga: Calendar,
  loki: Palette,
  mimir: Brain,
  luci: Flame
}

const SimpleEventFlow = ({ steps = [], currentStep = 0 }) => {
  console.log('SimpleEventFlow received steps:', steps)
  
  if (!steps || steps.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-semibold text-gray-900 mb-3">Event Flow</h3>
        <p className="text-gray-500 text-sm">No steps to display</p>
      </div>
    )
  }

  return (
    <motion.div
      className="bg-white rounded-xl border border-gray-200 p-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <h3 className="font-semibold text-gray-900 mb-6 flex items-center">
        <Zap className="w-5 h-5 mr-2 text-blue-600" />
        Event Flow ({steps.length} steps)
      </h3>
      
      <div className="space-y-4">
        {steps.map((step, index) => {
          // Parse drone name from step - handle multiple formats
          const droneMatch = step.match(/-> Drone: (\w+)/) || step.match(/Drone: (\w+)/)
          const toolMatch = step.match(/-> Tool: (\w+)/) || step.match(/Tool: (\w+)/)
          const droneName = droneMatch ? droneMatch[1] : null
          const toolName = toolMatch ? toolMatch[1] : null
          
          // Extract step type
          const stepType = step.includes('ActionStep') ? 'Action' : 
                          step.includes('ToolCallingStep') ? 'Tool Call' : 'Step'
          
          const Icon = droneName ? droneIcons[droneName] || Brain : Zap
          const isActive = index < currentStep
          const isCurrent = index === currentStep - 1
          
          return (
            <motion.div
              key={index}
              className={`flex items-center space-x-4 p-4 rounded-lg border-2 ${
                isCurrent 
                  ? 'border-blue-400 bg-blue-50' 
                  : isActive 
                  ? 'border-green-400 bg-green-50'
                  : 'border-gray-200 bg-gray-50'
              }`}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              {/* Step Number */}
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                isCurrent 
                  ? 'bg-blue-500 text-white' 
                  : isActive 
                  ? 'bg-green-500 text-white'
                  : 'bg-gray-300 text-gray-600'
              }`}>
                {index + 1}
              </div>
              
              {/* Icon */}
              <div className={`p-2 rounded-lg ${
                droneName ? 'bg-purple-100' : 'bg-gray-100'
              }`}>
                <Icon className={`w-5 h-5 ${
                  droneName ? 'text-purple-600' : 'text-gray-600'
                }`} />
              </div>
              
              {/* Step Details */}
              <div className="flex-1">
                <div className="text-sm font-medium text-gray-900">
                  {stepType}
                </div>
                <div className="text-xs text-gray-600 mt-1">
                  {step}
                </div>
                {droneName && (
                  <div className="flex items-center space-x-1 mt-2">
                    <span className="text-xs font-medium text-purple-600">
                      🤖 {droneName.charAt(0).toUpperCase() + droneName.slice(1)}
                    </span>
                    {toolName && (
                      <span className="text-xs text-orange-600">
                        • 🔧 {toolName}
                      </span>
                    )}
                  </div>
                )}
                {toolName && !droneName && (
                  <div className="text-xs text-orange-600 mt-2">
                    🔧 {toolName}
                  </div>
                )}
              </div>
              
              {/* Arrow */}
              {index < steps.length - 1 && (
                <ArrowDown className="w-4 h-4 text-gray-400" />
              )}
            </motion.div>
          )
        })}
      </div>
    </motion.div>
  )
}

export default SimpleEventFlow