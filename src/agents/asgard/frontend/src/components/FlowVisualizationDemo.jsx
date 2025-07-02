import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Play, Pause } from 'lucide-react'
import AgentFlowVisualization from './AgentFlowVisualization'

const demoSteps = [
  "Step 1: ActionStep -> Drone: odin",
  "Step 2: ToolCallingStep -> Tool: get_current_time", 
  "Step 3: ActionStep -> Drone: freya",
  "Step 4: ToolCallingStep -> Tool: get_search_tool",
  "Step 5: ActionStep -> Drone: saga", 
  "Step 6: ToolCallingStep -> Tool: search_local_events",
  "Step 7: ActionStep -> Drone: loki",
  "Step 8: ToolCallingStep -> Tool: create_artwork",
  "Step 9: ActionStep -> Drone: mimir",
  "Step 10: FinalStep -> Complete mission synthesis"
]

const FlowVisualizationDemo = () => {
  const [isRunning, setIsRunning] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)
  const [steps, setSteps] = useState([])

  const startDemo = () => {
    setIsRunning(true)
    setCurrentStep(0)
    setSteps(demoSteps)
    
    // Simulate step progression
    demoSteps.forEach((_, idx) => {
      setTimeout(() => {
        setCurrentStep(idx + 1)
        if (idx === demoSteps.length - 1) {
          setTimeout(() => setIsRunning(false), 1000)
        }
      }, (idx + 1) * 1200)
    })
  }

  const resetDemo = () => {
    setIsRunning(false)
    setCurrentStep(0)
    setSteps([])
  }

  return (
    <div className="space-y-6">
      <motion.div
        className="card-professional p-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="heading-dynamic text-lg">
            Agent Flow Visualization Demo
          </h3>
          <div className="flex space-x-2">
            <motion.button
              onClick={startDemo}
              disabled={isRunning}
              className="btn-professional flex items-center space-x-2 disabled:opacity-50"
              whileHover={{ scale: isRunning ? 1 : 1.02 }}
              whileTap={{ scale: isRunning ? 1 : 0.98 }}
            >
              <Play className="w-4 h-4" />
              <span>Start Demo</span>
            </motion.button>
            <motion.button
              onClick={resetDemo}
              className="btn-professional-secondary flex items-center space-x-2"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <Pause className="w-4 h-4" />
              <span>Reset</span>
            </motion.button>
          </div>
        </div>
        
        <p className="text-professional-muted text-sm mb-4">
          This demonstrates how the drone swarm coordinates to execute complex requests. 
          Watch as Odin commands specialized drones (Freya, Saga, Loki, Mimir) and their tools.
        </p>
      </motion.div>

      <AgentFlowVisualization
        isStreaming={isRunning}
        steps={steps}
        currentStep={currentStep}
      />
    </div>
  )
}

export default FlowVisualizationDemo