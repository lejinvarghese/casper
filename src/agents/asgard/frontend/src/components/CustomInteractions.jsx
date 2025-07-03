import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import AgentInterface from './AgentInterface'
import RequestPanel from './RequestPanel'
import ResponseDisplay from './ResponseDisplay'
import SimpleEventFlow from './SimpleEventFlow'

const CustomInteractions = ({ 
  agents, 
  selectedAgent, 
  onAgentSelect, 
  onSubmit, 
  response, 
  loading 
}) => {
  const [flowSteps, setFlowSteps] = useState([])
  const [currentStep, setCurrentStep] = useState(0)
  const [isStreaming, setIsStreaming] = useState(false)

  const handleStreamingRequest = async (requestData) => {
    setIsStreaming(true)
    setFlowSteps([])
    setCurrentStep(0)

    try {
      const result = await onSubmit(requestData)
      
      // Parse steps from response if available
      console.log('🔍 Full result object:', result)
      console.log('🔍 Result.steps exists?', !!result?.steps)
      console.log('🔍 Result.steps value:', result?.steps)
      
      if (result && result.steps) {
        console.log('🔍 Raw steps from API:', result.steps)
        const steps = result.steps.split('\n').filter(step => step.trim())
        console.log('🔍 Parsed steps array:', steps)
        console.log('🔍 Number of steps:', steps.length)
        setFlowSteps(steps)
        
        // Simulate step progression for visualization
        steps.forEach((_, idx) => {
          setTimeout(() => setCurrentStep(idx + 1), (idx + 1) * 800)
        })
      } else {
        console.log('🔍 No steps found in result. Full result:', JSON.stringify(result, null, 2))
      }
      
      return result
    } catch (error) {
      console.error('Streaming request failed:', error)
      throw error
    } finally {
      setTimeout(() => setIsStreaming(false), 4000)
    }
  }

  return (
    <div className="space-y-8">
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
          onAgentSelect={onAgentSelect}
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
            onSubmit={handleStreamingRequest}
            onAgentSelect={onAgentSelect}
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

      {/* Agent Flow Visualization */}
      {(flowSteps.length > 0 || isStreaming) && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <SimpleEventFlow
            steps={flowSteps}
            currentStep={currentStep}
          />
        </motion.div>
      )}
    </div>
  )
}

export default CustomInteractions