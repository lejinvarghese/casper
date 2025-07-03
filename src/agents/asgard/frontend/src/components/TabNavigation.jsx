import React from 'react'
import { motion } from 'framer-motion'
import { MessageSquare, Sparkles, Settings } from 'lucide-react'

const tabs = [
  { id: 'interact', label: 'Interact', icon: MessageSquare },
  { id: 'ambient', label: 'Harmonics', icon: Sparkles },
]

const TabNavigation = ({ activeTab, onTabChange }) => {
  return (
    <motion.div 
      className="flex space-x-1 p-1 surface-professional rounded-xl"
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      {tabs.map((tab) => {
        const IconComponent = tab.icon
        const isActive = activeTab === tab.id
        
        return (
          <motion.button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`
              relative flex items-center space-x-2 px-4 py-2.5 rounded-lg font-semibold transition-all duration-200
              ${isActive 
                ? 'text-neutral-900 bg-white shadow-sm' 
                : 'text-neutral-600 hover:text-neutral-800 hover:bg-white/60'
              }
            `}
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.99 }}
            layout
            style={{ letterSpacing: '-0.01em' }}
          >
            <IconComponent className="w-4 h-4" />
            <span className="text-sm">{tab.label}</span>
            
            {isActive && (
              <motion.div
                className="absolute bottom-0 left-1/2 w-1 h-1 bg-primary-600 rounded-full"
                layoutId="activeTab"
                initial={false}
                style={{ transform: 'translateX(-50%)' }}
              />
            )}
          </motion.button>
        )
      })}
    </motion.div>
  )
}

export default TabNavigation