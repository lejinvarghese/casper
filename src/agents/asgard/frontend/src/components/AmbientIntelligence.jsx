import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Clock, Zap, Play, Pause, Settings, 
  Brain, ChefHat, Calendar, Palette, Crown, Flame,
  Activity, CheckCircle, AlertCircle, Sparkles
} from 'lucide-react'

const droneIcons = {
  odin: Crown,
  freya: ChefHat,
  saga: Calendar,
  loki: Palette,
  mimir: Brain,
  luci: Flame
}

const timeSegmentColors = {
  early_morning: 'from-amber-400/20 to-orange-400/20',
  morning: 'from-blue-400/20 to-cyan-400/20', 
  workday: 'from-green-400/20 to-emerald-400/20',
  evening: 'from-purple-400/20 to-pink-400/20',
  night: 'from-indigo-400/20 to-blue-600/20'
}

const AmbientIntelligence = ({ automationService }) => {
  const [status, setStatus] = useState(null)
  const [recentAutomations, setRecentAutomations] = useState([])
  const [expanded, setExpanded] = useState(false)
  const [loading, setLoading] = useState(true)
  const [expandedAutomation, setExpandedAutomation] = useState(null)

  useEffect(() => {
    loadAutomationStatus()
    const interval = setInterval(loadAutomationStatus, 60000) // Update every minute
    return () => clearInterval(interval)
  }, [])

  const loadAutomationStatus = async () => {
    try {
      console.log('Loading automation status...')
      const statusData = await automationService.getStatus()
      console.log('Status data received:', statusData)
      setStatus(statusData)
      
      const recentData = await automationService.getRecent(24)
      console.log('Recent data received:', recentData)
      console.log('Recent automations array:', recentData.automations)
      if (recentData.automations && recentData.automations.length > 0) {
        console.log('First automation details:', recentData.automations[0])
      }
      setRecentAutomations(recentData.automations || [])
    } catch (error) {
      console.error('Failed to load automation status:', error)
      // Set some fallback data so we can see the UI
      setStatus({
        context: { time_segment: 'workday', is_weekend: false },
        background_running: false,
        pending_count: 0,
        enabled_automations: 0,
        total_automations: 7,
        pending_automations: []
      })
    } finally {
      setLoading(false)
    }
  }

  const toggleAutomation = async (automationId, enabled) => {
    try {
      await automationService.toggle(automationId, enabled)
      await loadAutomationStatus()
    } catch (error) {
      console.error('Failed to toggle automation:', error)
    }
  }

  const triggerAutomation = async (automationId) => {
    try {
      await automationService.trigger(automationId)
      await loadAutomationStatus()
    } catch (error) {
      console.error('Failed to trigger automation:', error)
    }
  }

  if (loading) {
    return (
      <motion.div 
        className="card-professional p-6"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        <div className="flex items-center space-x-3">
          <div className="animate-spin">
            <Sparkles className="w-5 h-5 text-primary-500" />
          </div>
          <div className="text-professional-muted">Loading neural harmonics...</div>
        </div>
      </motion.div>
    )
  }

  if (!status) {
    return null
  }

  const currentSegment = status.context?.time_segment || 'workday'
  const gradientClass = timeSegmentColors[currentSegment] || timeSegmentColors.workday

  return (
    <motion.div
      className="space-y-4"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      {/* Ambient Status Header */}
      <motion.div
        className="card-professional p-5 border-primary-200/40"
        whileHover={{ scale: 1.005 }}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="relative">
              <div className="p-2 bg-white/90 rounded-xl shadow-sm">
                <Activity className="w-5 h-5 text-primary-600" />
              </div>
              {status.background_running && (
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-accent-500 rounded-full animate-pulse"></div>
              )}
            </div>
            <div>
              <h3 className="heading-dynamic text-base">Harmonics</h3>
              <p className="text-professional-muted text-sm capitalize">
                {status.context?.time_segment?.replace('_', ' ')} • {status.enabled_automations} active resonance
              </p>
            </div>
          </div>
          
          <button
            onClick={() => setExpanded(!expanded)}
            className="p-2 hover:bg-white/60 rounded-lg transition-colors"
          >
            <Settings className="w-4 h-4 text-neutral-600" />
          </button>
        </div>

        {/* Context Timeline */}
        <div className="mt-4 flex items-center space-x-2">
          <Clock className="w-4 h-4 text-neutral-500" />
          <div className="flex-1 bg-neutral-200/50 rounded-full h-2 overflow-hidden">
            <div 
              className="h-full bg-accent-400 rounded-full transition-all duration-1000"
              style={{ 
                width: `${((new Date().getHours() + new Date().getMinutes() / 60) / 24) * 100}%` 
              }}
            />
          </div>
          <span className="text-xs text-professional-muted font-medium tabular-nums">
            {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>
      </motion.div>

      {/* Pending Automations */}
      <AnimatePresence>
        {status.pending_count > 0 && (
          <motion.div
            className="card p-4 border-amber-200 bg-amber-50/50"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            <div className="flex items-center space-x-2 mb-3">
              <Zap className="w-4 h-4 text-amber-600" />
              <span className="font-medium text-amber-800">
                {status.pending_count} automation{status.pending_count !== 1 ? 's' : ''} ready
              </span>
            </div>
            
            <div className="space-y-2">
              {status.pending_automations?.map((automation) => {
                const DroneIcon = droneIcons[automation.drone] || Brain
                return (
                  <div key={automation.id} className="flex items-center justify-between p-2 bg-white rounded-lg">
                    <div className="flex items-center space-x-3">
                      <DroneIcon className="w-4 h-4 text-neutral-600" />
                      <span className="text-sm font-medium text-neutral-800">{automation.name}</span>
                    </div>
                    <button
                      onClick={() => triggerAutomation(automation.id)}
                      className="p-1 hover:bg-amber-100 rounded transition-colors"
                    >
                      <Play className="w-3 h-3 text-amber-600" />
                    </button>
                  </div>
                )
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Recent Activity - Expanded and Prominent */}
      {recentAutomations.length > 0 && (
        <motion.div
          className="card p-6 border-blue-200/40 bg-gradient-to-br from-blue-50/30 to-indigo-50/20"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <h4 className="font-semibold text-lg text-slate-800 mb-4 flex items-center space-x-2">
            <CheckCircle className="w-5 h-5 text-slate-600" />
            <span>Recent Activity</span>
          </h4>
          
          <div className="space-y-3">
            {recentAutomations.slice(0, 5).map((automation, index) => {
              const DroneIcon = droneIcons[automation.drone] || Brain
              const timeAgo = new Date() - new Date(automation.executed_at)
              const hoursAgo = Math.floor(timeAgo / (1000 * 60 * 60))
              
              return (
                <div key={automation.automation_id}>
                  <motion.div
                    className={`border rounded-lg p-4 hover:shadow-sm transition-all cursor-pointer ${
                      automation.success 
                        ? 'border-blue-200 bg-gradient-to-br from-blue-50/50 to-white hover:from-blue-100/50' 
                        : 'border-red-200 bg-gradient-to-br from-red-50/50 to-white hover:from-red-100/50'
                    }`}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    onClick={() => setExpandedAutomation(
                      expandedAutomation === automation.automation_id ? null : automation.automation_id
                    )}
                  >
                    <div className="flex items-start space-x-3">
                      <div className={`p-2 rounded-lg ${
                        automation.success ? 'bg-blue-100' : 'bg-red-100'
                      }`}>
                        <DroneIcon className={`w-4 h-4 ${
                          automation.success ? 'text-blue-600' : 'text-red-600'
                        }`} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between mb-2">
                          <p className={`text-sm font-semibold ${
                            automation.success ? 'text-blue-900' : 'text-red-900'
                          }`}>
                            {automation.automation_name}
                          </p>
                          <div className="flex items-center space-x-2">
                            <p className="text-xs text-neutral-500">
                              {hoursAgo > 0 ? `${hoursAgo}h ago` : 'Recently'}
                            </p>
                            {automation.success ? (
                              <CheckCircle className="w-4 h-4 text-blue-500 flex-shrink-0" />
                            ) : (
                              <AlertCircle className="w-4 h-4 text-red-500 flex-shrink-0" />
                            )}
                          </div>
                        </div>
                        {automation.result && (
                          <p className={`text-sm leading-relaxed ${
                            automation.success ? 'text-blue-800' : 'text-red-800'
                          }`}>
                            {typeof automation.result === 'string' ? automation.result.substring(0, 200) + (automation.result.length > 200 ? '...' : '') : 'Result available'}
                          </p>
                        )}
                      </div>
                    </div>
                  </motion.div>
                  
                  {/* Expanded result view */}
                  <AnimatePresence>
                    {expandedAutomation === automation.automation_id && (
                      <motion.div
                        className={`mt-3 p-4 rounded-lg border ${
                          automation.success 
                            ? 'bg-indigo-50 border-indigo-300' 
                            : 'bg-rose-50 border-rose-300'
                        }`}
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                      >
                        <p className={`text-sm whitespace-pre-wrap max-h-48 overflow-y-auto leading-relaxed ${
                          automation.success ? 'text-indigo-900' : 'text-rose-900'
                        }`}>
                          {automation.result || 'No result available'}
                        </p>
                        {automation.error && (
                          <div className="mt-3 p-3 bg-red-100 rounded border-l-4 border-red-300">
                            <p className="text-sm font-medium text-red-800 mb-1">Error:</p>
                            <p className="text-sm text-red-700">{automation.error}</p>
                          </div>
                        )}
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              )
            })}
          </div>
        </motion.div>
      )}

      {/* Next Automation Preview */}
      {status.next_automation && (
        <motion.div
          className="card p-4 border-blue-200 bg-blue-50/30"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
        >
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Clock className="w-4 h-4 text-blue-600" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-blue-900">
                Next: {status.next_automation.name}
              </p>
              <p className="text-xs text-blue-600">
                {status.next_automation.time_until?.includes('-') ? 'Overdue' : `In ${status.next_automation.time_until?.split('.')[0]}`}
              </p>
            </div>
          </div>
        </motion.div>
      )}
    </motion.div>
  )
}

export default AmbientIntelligence