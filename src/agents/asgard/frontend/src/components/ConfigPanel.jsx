import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Settings, X, Palette, Volume2, VolumeX } from 'lucide-react'

const ConfigPanel = ({ config, onConfigChange }) => {
  const [isOpen, setIsOpen] = useState(false)

  const themes = [
    { id: 'modern', name: 'Modern', colors: ['#ffffff', '#f5f5f5'] },
    { id: 'minimal', name: 'Minimal', colors: ['#fafafa', '#e5e5e5'] },
    { id: 'warm', name: 'Warm', colors: ['#fef3c7', '#fed7aa'] },
    { id: 'cool', name: 'Cool', colors: ['#e0f2fe', '#dcfce7'] }
  ]

  const handleConfigChange = (key, value) => {
    onConfigChange({ ...config, [key]: value })
  }

  return (
    <>
      <motion.button
        onClick={() => setIsOpen(true)}
        className="p-3 card card-hover"
        whileHover={{ scale: 1.05, y: -2 }}
        whileTap={{ scale: 0.95 }}
      >
        <Settings className="w-5 h-5 text-neutral-600" />
      </motion.button>

      <AnimatePresence>
        {isOpen && (
          <>
            <motion.div
              className="fixed inset-0 bg-black/20 backdrop-blur-sm z-50"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsOpen(false)}
            />
            
            <motion.div
              className="fixed right-6 top-6 bottom-6 w-80 card p-6 z-50 overflow-y-auto shadow-xl"
              initial={{ opacity: 0, x: 100 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 100 }}
              transition={{ type: "spring", damping: 25, stiffness: 300 }}
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="font-display text-xl font-semibold text-neutral-900">
                  Settings
                </h2>
                <motion.button
                  onClick={() => setIsOpen(false)}
                  className="p-2 hover:bg-neutral-100 rounded-lg transition-colors"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <X className="w-5 h-5 text-neutral-600" />
                </motion.button>
              </div>

              <div className="space-y-6">
                {/* Theme Selection */}
                <div>
                  <h3 className="text-sm font-medium text-neutral-700 mb-3">
                    Visual Theme
                  </h3>
                  <div className="space-y-2">
                    {themes.map((theme) => (
                      <motion.button
                        key={theme.id}
                        onClick={() => handleConfigChange('theme', theme.id)}
                        className={`
                          w-full p-3 rounded-xl transition-all duration-200 flex items-center justify-between border
                          ${config.theme === theme.id 
                            ? 'bg-agents-odin/10 border-agents-odin/30 text-agents-odin' 
                            : 'bg-neutral-50 border-neutral-200 hover:border-neutral-300 hover:bg-neutral-100 text-neutral-700'
                          }
                        `}
                        whileHover={{ scale: 1.02, y: -1 }}
                        whileTap={{ scale: 0.98 }}
                      >
                        <span className="text-sm font-medium">
                          {theme.name}
                        </span>
                        <div className="flex space-x-1">
                          {theme.colors.map((color, index) => (
                            <div
                              key={index}
                              className="w-4 h-4 rounded-full border border-neutral-200"
                              style={{ backgroundColor: color }}
                            />
                          ))}
                        </div>
                      </motion.button>
                    ))}
                  </div>
                </div>

                {/* Verbose Mode */}
                <div>
                  <h3 className="text-sm font-medium text-neutral-700 mb-3">
                    Processing Mode
                  </h3>
                  <motion.button
                    onClick={() => handleConfigChange('verbose', !config.verbose)}
                    className={`
                      w-full p-3 rounded-xl transition-all duration-200 flex items-center justify-between border
                      ${config.verbose
                        ? 'bg-green-50 border-green-200 text-green-700' 
                        : 'bg-neutral-50 border-neutral-200 hover:border-neutral-300 hover:bg-neutral-100 text-neutral-700'
                      }
                    `}
                    whileHover={{ scale: 1.02, y: -1 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <span className="text-sm font-medium">
                      Verbose Mode
                    </span>
                    <div className="flex items-center space-x-2">
                      {config.verbose ? (
                        <Volume2 className="w-4 h-4 text-green-600" />
                      ) : (
                        <VolumeX className="w-4 h-4 text-neutral-500" />
                      )}
                    </div>
                  </motion.button>
                  <p className="text-xs text-neutral-500 mt-2">
                    Show detailed deployment steps and drone coordination
                  </p>
                </div>

                {/* Quick Actions */}
                <div>
                  <h3 className="text-sm font-medium text-neutral-700 mb-3">
                    Quick Actions
                  </h3>
                  <div className="space-y-2">
                    <motion.button
                      className="w-full p-3 bg-neutral-50 border border-neutral-200 rounded-xl hover:bg-neutral-100 hover:border-neutral-300 transition-all text-left"
                      whileHover={{ scale: 1.02, y: -1 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <span className="text-sm text-neutral-700 font-medium">Reset Session</span>
                    </motion.button>
                    <motion.button
                      className="w-full p-3 bg-neutral-50 border border-neutral-200 rounded-xl hover:bg-neutral-100 hover:border-neutral-300 transition-all text-left"
                      whileHover={{ scale: 1.02, y: -1 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <span className="text-sm text-neutral-700 font-medium">Export History</span>
                    </motion.button>
                  </div>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  )
}

export default ConfigPanel