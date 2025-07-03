import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Clock, Zap, Play, Pause, Settings, RotateCcw, 
  Brain, ChefHat, Calendar, Palette, Crown, Flame,
  Sun, Sunset, Moon, Coffee, Briefcase, Lightbulb,
  CheckCircle, XCircle, AlertCircle, Info
} from 'lucide-react'

const droneIcons = {
  odin: Crown,
  freya: ChefHat,
  saga: Calendar,
  loki: Palette,
  mimir: Brain,
  luci: Flame
}

const timeSegmentIcons = {
  early_morning: Coffee,
  morning: Sun,
  workday: Briefcase,
  evening: Sunset,
  night: Moon
}

const automationDescriptions = {
  morning_energy: {
    purpose: "Dawn Protocol: Biorhythm synchronization and metabolic ignition",
    details: "Freya initiates neural chemistry optimization through weather-adaptive nutrition synthesis. Calculates hydration matrices, rapid-deployment sustenance configurations, and circadian energy alignment protocols.",
    triggers: ["Dawn phase resonance (7-9 AM)", "20-hour recharge cycle"],
    benefits: ["Sustained bio-energy", "Atmospheric nutrition sync", "Seasonal molecular adaptation"]
  },
  day_overview: {
    purpose: "Tactical Grid: Strategic temporal coordination and flow optimization",
    details: "Saga deploys comprehensive day-state analysis using atmospheric data fusion, productivity cascade mapping, and temporal efficiency algorithms. Generates adaptive workflow sequences.",
    triggers: ["Dawn phase resonance (7-9 AM)", "20-hour recharge cycle"],
    benefits: ["Optimized neural throughput", "Weather-sync planning", "Balanced existence protocols"]
  },
  midday_optimization: {
    purpose: "Solar Apex: Mid-cycle performance amplification and focus crystallization",
    details: "Saga executes real-time cognitive recalibration, break-state optimization, and afternoon energy flux management. Counters post-consumption energy decay through focus restoration algorithms.",
    triggers: ["Solar cycle active phase (9 AM - 5 PM)", "6-hour refresh interval"],
    benefits: ["Sustained cognitive luminosity", "Optimized neural breaks", "Enhanced mental crystallization"]
  },
  evening_wind_down: {
    purpose: "Twilight Synthesis: Recovery optimization and next-cycle preparation",
    details: "Freya orchestrates evening nourishment sequences, neural relaxation protocols, and sleep-state preparation rituals. Optimizes tonight's restoration and tomorrow's energy matrices.",
    triggers: ["Twilight phase (5-9 PM)", "20-hour recharge cycle"],
    benefits: ["Enhanced sleep architecture", "Next-cycle energy prep", "Stress dissolution"]
  },
  creative_spark: {
    purpose: "Chaos Catalyst: Artistic vision amplification and innovation synthesis",
    details: "Loki deploys creative disruption patterns, artistic challenge matrices, and innovation catalyst sequences aligned with seasonal energy and temporal context. Activates creative neural pathways.",
    triggers: ["Evening or Solar phases", "48-hour creative cooldown"],
    benefits: ["Enhanced creative flux", "Seasonal inspiration synthesis", "Artistic skill evolution"]
  },
  wisdom_reflection: {
    purpose: "Deep Current: Consciousness exploration and growth vector analysis",
    details: "Mimir channels philosophical resonance streams, insight amplification protocols, and growth trajectory mapping for continuous consciousness evolution and mindful existence.",
    triggers: ["Twilight phase (5-9 PM)", "20-hour recharge cycle"],
    benefits: ["Consciousness expansion", "Mindful reflection synthesis", "Growth vector optimization"]
  },
  weekend_adventure: {
    purpose: "Chaos Vector: Spontaneous reality disruption and urban exploration",
    details: "Luci generates spontaneous adventure algorithms, urban exploration sequences, and reality-bending weekend protocols specifically calibrated for Toronto's energy grid. Weekend-only activation.",
    triggers: ["Weekend energy phases", "48-hour chaos cooldown"],
    benefits: ["Existence-work balance", "Urban grid exploration", "Spontaneous reality shifts"]
  }
}

const AutomationDetails = ({ automationService }) => {
  const [automations, setAutomations] = useState([])
  const [selectedAutomation, setSelectedAutomation] = useState(null)
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadAutomationData()
  }, [])

  const loadAutomationData = async () => {
    try {
      console.log('Loading automation details...')
      const statusData = await automationService.getStatus()
      console.log('Automation details status:', statusData)
      setStatus(statusData)
      
      // Create automation list with details
      const automationList = Object.keys(automationDescriptions).map(id => ({
        id,
        ...automationDescriptions[id],
        enabled: true, // Default, will be updated from status
        lastTriggered: null
      }))
      
      setAutomations(automationList)
    } catch (error) {
      console.error('Failed to load automation data:', error)
      
      // Set fallback data so we can see the automation details
      setStatus({
        context: { time_segment: 'workday', is_weekend: false },
        background_running: false,
        pending_count: 0,
        enabled_automations: 7,
        total_automations: 7,
        pending_automations: []
      })
      
      // Show automations even if backend is down
      const automationList = Object.keys(automationDescriptions).map(id => ({
        id,
        ...automationDescriptions[id],
        enabled: true,
        lastTriggered: null
      }))
      
      setAutomations(automationList)
    } finally {
      setLoading(false)
    }
  }

  const toggleAutomation = async (automationId, enabled) => {
    try {
      await automationService.toggle(automationId, enabled)
      await loadAutomationData()
    } catch (error) {
      console.error('Failed to toggle automation:', error)
    }
  }

  const triggerAutomation = async (automationId) => {
    try {
      await automationService.trigger(automationId)
      await loadAutomationData()
    } catch (error) {
      console.error('Failed to trigger automation:', error)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin">
          <Lightbulb className="w-6 h-6 text-rose-500" />
        </div>
        <span className="ml-3 text-neutral-600">Loading resonance grid...</span>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* System Status */}
      {status && (
        <motion.div
          className="card p-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-display text-xl font-semibold text-neutral-900">
              Resonance Grid
            </h2>
            <div className="flex items-center space-x-2">
              {status.background_running ? (
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-sm text-green-700 font-medium">Active</span>
                </div>
              ) : (
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                  <span className="text-sm text-red-700 font-medium">Inactive</span>
                </div>
              )}
            </div>
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="text-center p-3 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{status.total_automations}</div>
              <div className="text-sm text-blue-700">Total Resonances</div>
            </div>
            <div className="text-center p-3 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{status.enabled_automations}</div>
              <div className="text-sm text-green-700">Active Streams</div>
            </div>
            <div className="text-center p-3 bg-amber-50 rounded-lg">
              <div className="text-2xl font-bold text-amber-600">{status.pending_count}</div>
              <div className="text-sm text-amber-700">Ready to Deploy</div>
            </div>
          </div>

          {status.context && (
            <div className="mt-4 p-3 bg-neutral-50 rounded-lg">
              <div className="flex items-center space-x-2">
                <Clock className="w-4 h-4 text-neutral-600" />
                <span className="text-sm font-medium text-neutral-700">Current Context:</span>
                <span className="text-sm text-neutral-600 capitalize">
                  {status.context.time_segment?.replace('_', ' ')} • {status.context.is_weekend ? 'Weekend' : 'Weekday'}
                </span>
              </div>
            </div>
          )}
        </motion.div>
      )}

      {/* Automation List */}
      <div className="grid gap-4">
        {automations.map((automation, index) => {
          const DroneIcon = droneIcons[automation.id?.includes('freya') ? 'freya' : 
                                      automation.id?.includes('saga') ? 'saga' :
                                      automation.id?.includes('loki') ? 'loki' :
                                      automation.id?.includes('mimir') ? 'mimir' :
                                      automation.id?.includes('luci') ? 'luci' : 'odin']
          
          const automationName = automation.id?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) || 'Unknown'
          
          return (
            <motion.div
              key={automation.id}
              className="card p-6 hover:shadow-md transition-shadow cursor-pointer"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              onClick={() => setSelectedAutomation(selectedAutomation === automation.id ? null : automation.id)}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-4 flex-1">
                  <div className="p-3 bg-rose-50 rounded-xl">
                    <DroneIcon className="w-5 h-5 text-rose-600" />
                  </div>
                  
                  <div className="flex-1">
                    <h3 className="font-semibold text-neutral-900 mb-2">{automationName}</h3>
                    <p className="text-neutral-600 text-sm leading-relaxed mb-3">
                      {automation.purpose}
                    </p>
                    
                    <div className="flex items-center space-x-4 text-xs text-neutral-500">
                      <div className="flex items-center space-x-1">
                        <Clock className="w-3 h-3" />
                        <span>Triggers: {automation.triggers?.[0] || 'Various times'}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <RotateCcw className="w-3 h-3" />
                        <span>Cooldown: {automation.triggers?.[1] || 'Variable'}</span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      triggerAutomation(automation.id)
                    }}
                    className="p-2 hover:bg-green-100 rounded-lg transition-colors"
                    title="Trigger now"
                  >
                    <Play className="w-4 h-4 text-green-600" />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      toggleAutomation(automation.id, !automation.enabled)
                    }}
                    className={`p-2 rounded-lg transition-colors ${
                      automation.enabled 
                        ? 'hover:bg-red-100 text-red-600' 
                        : 'hover:bg-green-100 text-green-600'
                    }`}
                    title={automation.enabled ? 'Disable' : 'Enable'}
                  >
                    {automation.enabled ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {/* Expanded Details */}
              <AnimatePresence>
                {selectedAutomation === automation.id && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="mt-4 pt-4 border-t border-neutral-200"
                  >
                    <div className="grid gap-4">
                      <div>
                        <h4 className="font-medium text-neutral-800 mb-2 flex items-center space-x-2">
                          <Info className="w-4 h-4 text-blue-500" />
                          <span>How it works</span>
                        </h4>
                        <p className="text-sm text-neutral-600 leading-relaxed">
                          {automation.details}
                        </p>
                      </div>
                      
                      <div>
                        <h4 className="font-medium text-neutral-800 mb-2 flex items-center space-x-2">
                          <Zap className="w-4 h-4 text-amber-500" />
                          <span>Benefits</span>
                        </h4>
                        <ul className="space-y-1">
                          {automation.benefits?.map((benefit, idx) => (
                            <li key={idx} className="flex items-center space-x-2 text-sm text-neutral-600">
                              <CheckCircle className="w-3 h-3 text-green-500 flex-shrink-0" />
                              <span>{benefit}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                      
                      <div>
                        <h4 className="font-medium text-neutral-800 mb-2 flex items-center space-x-2">
                          <Clock className="w-4 h-4 text-purple-500" />
                          <span>Trigger Conditions</span>
                        </h4>
                        <ul className="space-y-1">
                          {automation.triggers?.map((trigger, idx) => (
                            <li key={idx} className="flex items-center space-x-2 text-sm text-neutral-600">
                              <AlertCircle className="w-3 h-3 text-purple-500 flex-shrink-0" />
                              <span>{trigger}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}

export default AutomationDetails