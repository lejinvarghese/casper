import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Brain, Zap, ChefHat, Calendar, Palette, Lightbulb, Play, CheckCircle, Clock } from 'lucide-react'

const droneIcons = {
  odin: Brain,
  commander: Brain,
  freya: ChefHat,
  chef: ChefHat,
  saga: Calendar,
  planner: Calendar,
  loki: Palette,
  artist: Palette,
  mimir: Lightbulb,
  philosopher: Lightbulb,
  luci: Zap,
  devil: Zap
}

const droneColors = {
  odin: 'text-blue-600 bg-blue-50 border-blue-200',
  freya: 'text-orange-600 bg-orange-50 border-orange-200',
  saga: 'text-green-600 bg-green-50 border-green-200',
  loki: 'text-purple-600 bg-purple-50 border-purple-200',
  mimir: 'text-indigo-600 bg-indigo-50 border-indigo-200',
  luci: 'text-red-600 bg-red-50 border-red-200'
}

const DroneNode = ({ drone, status, step, tools }) => {
  const Icon = droneIcons[drone] || Brain
  const colors = droneColors[drone] || 'text-gray-600 bg-gray-50 border-gray-200'
  
  const statusIcon = {
    idle: null,
    active: <Play className="w-3 h-3 text-blue-500" />,
    complete: <CheckCircle className="w-3 h-3 text-green-500" />
  }

  return (
    <motion.div
      className={`relative p-4 rounded-xl border-2 ${colors} shadow-sm`}
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      whileHover={{ scale: 1.05 }}
      transition={{ duration: 0.3 }}
    >
      <div className="flex items-center space-x-2 mb-2">
        <Icon className="w-5 h-5" />
        <span className="font-semibold capitalize">{drone}</span>
        {statusIcon[status]}
      </div>
      
      {step && (
        <motion.div
          className="text-xs opacity-75 mb-1"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          Step {step}
        </motion.div>
      )}
      
      {tools && tools.length > 0 && (
        <motion.div
          className="flex flex-wrap gap-1"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          {tools.map((tool, idx) => (
            <span
              key={idx}
              className="px-2 py-1 text-xs bg-white rounded-md border shadow-sm"
            >
              {tool}
            </span>
          ))}
        </motion.div>
      )}

      {status === 'active' && (
        <motion.div
          className="absolute -inset-1 rounded-xl border-2 border-blue-400"
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 1.5, repeat: Infinity }}
        />
      )}
    </motion.div>
  )
}

const FlowConnection = ({ from, to, active }) => (
  <motion.div
    className="relative"
    initial={{ opacity: 0 }}
    animate={{ opacity: active ? 1 : 0.3 }}
    transition={{ duration: 0.5 }}
  >
    <svg className="absolute top-1/2 left-full w-16 h-2 -translate-y-1/2">
      <motion.line
        x1="0"
        y1="4"
        x2="64"
        y2="4"
        stroke={active ? "#3B82F6" : "#E5E7EB"}
        strokeWidth="2"
        strokeDasharray={active ? "5,5" : "none"}
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 0.8 }}
      />
      <motion.polygon
        points="60,1 64,4 60,7"
        fill={active ? "#3B82F6" : "#E5E7EB"}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
      />
    </svg>
  </motion.div>
)

const ExecutionLog = ({ steps, currentStep }) => (
  <motion.div
    className="bg-white rounded-xl border border-gray-200 p-4 max-h-64 overflow-y-auto"
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
  >
    <h3 className="font-semibold text-gray-900 mb-3 flex items-center">
      <Clock className="w-4 h-4 mr-2" />
      Execution Log
    </h3>
    <div className="space-y-2">
      {steps.map((step, idx) => (
        <motion.div
          key={idx}
          className={`p-2 rounded-lg text-sm ${
            idx === currentStep
              ? 'bg-blue-50 border-l-4 border-blue-400'
              : idx < currentStep
              ? 'bg-green-50 border-l-4 border-green-400'
              : 'bg-gray-50 border-l-4 border-gray-200'
          }`}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: idx * 0.1 }}
        >
          <div className="font-medium">{step.type}</div>
          {step.drone && (
            <div className="text-gray-600">Drone: {step.drone}</div>
          )}
          {step.tools && step.tools.length > 0 && (
            <div className="text-gray-600">Tools: {step.tools.join(', ')}</div>
          )}
        </motion.div>
      ))}
    </div>
  </motion.div>
)

export default function AgentFlowVisualization({ isStreaming, steps = [], currentStep = 0 }) {
  const [droneStates, setDroneStates] = useState({})
  const [executionLog, setExecutionLog] = useState([])

  useEffect(() => {
    if (steps.length > 0) {
      const parsedSteps = steps.map((step, idx) => {
        const droneMatch = step.match(/Drone: (.+?)(?:\s|$)/)
        const toolMatch = step.match(/Tool: (.+?)(?:\s|$)/)
        
        return {
          id: idx,
          type: step.split(':')[1]?.split('->')[0]?.trim() || 'Action',
          drone: droneMatch ? droneMatch[1].trim() : null,
          tools: toolMatch ? toolMatch[1].split(',').map(t => t.trim()) : []
        }
      })
      
      setExecutionLog(parsedSteps)
      
      // Update drone states
      const newStates = {}
      parsedSteps.forEach((step, idx) => {
        if (step.drone) {
          newStates[step.drone] = {
            status: idx < currentStep ? 'complete' : idx === currentStep ? 'active' : 'idle',
            step: idx + 1,
            tools: step.tools
          }
        }
      })
      setDroneStates(newStates)
    }
  }, [steps, currentStep])

  const activeDrones = Object.keys(droneStates)
  const uniqueDrones = [...new Set(activeDrones)]

  return (
    <div className="space-y-6">
      {/* Flow Visualization */}
      <motion.div
        className="bg-white rounded-xl border border-gray-200 p-6"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        <h3 className="font-semibold text-gray-900 mb-4 flex items-center">
          <Zap className="w-5 h-5 mr-2 text-blue-600" />
          Agent Flow
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <AnimatePresence>
            {uniqueDrones.map((drone) => {
              const state = droneStates[drone] || { status: 'idle' }
              return (
                <DroneNode
                  key={drone}
                  drone={drone}
                  status={state.status}
                  step={state.step}
                  tools={state.tools}
                />
              )
            })}
          </AnimatePresence>
        </div>
        
        {isStreaming && (
          <motion.div
            className="mt-4 flex items-center justify-center space-x-2 text-blue-600"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <motion.div
              className="w-2 h-2 bg-blue-600 rounded-full"
              animate={{ scale: [1, 1.5, 1] }}
              transition={{ duration: 1, repeat: Infinity }}
            />
            <span className="text-sm font-medium">Executing...</span>
          </motion.div>
        )}
      </motion.div>

      {/* Execution Log */}
      {executionLog.length > 0 && (
        <ExecutionLog steps={executionLog} currentStep={currentStep} />
      )}
    </div>
  )
}