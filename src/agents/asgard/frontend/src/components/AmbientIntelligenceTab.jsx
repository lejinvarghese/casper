import React from 'react'
import { motion } from 'framer-motion'
import AmbientIntelligence from './AmbientIntelligence'
import AutomationDetails from './AutomationDetails'

const AmbientIntelligenceTab = ({ automationService }) => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      {/* Live Status */}
      <motion.div
        className="lg:col-span-1"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
      >
        <AmbientIntelligence automationService={automationService} />
      </motion.div>

      {/* Detailed Automation Management */}
      <motion.div
        className="lg:col-span-2"
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.6, delay: 0.4 }}
      >
        <AutomationDetails automationService={automationService} />
      </motion.div>
    </div>
  )
}

export default AmbientIntelligenceTab