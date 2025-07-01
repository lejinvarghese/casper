import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Eye, EyeOff, Copy, Check, Crown, ChefHat, Calendar, Palette, Brain, Flame } from 'lucide-react'

const droneIcons = {
  odin: Crown,
  freya: ChefHat,
  saga: Calendar,
  loki: Palette,
  mimir: Brain,
  luci: Flame
}

const formatResponseText = (text) => {
  if (!text) return []
  
  const lines = text.split('\n')
  const formatted = []
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim()
    
    if (!line) {
      formatted.push({ type: 'break' })
      continue
    }
    
    // Headers (lines with ###, ##, or all caps)
    if (line.match(/^#{1,4}\s+/) || line.match(/^[A-Z\s]{3,}:?\s*$/)) {
      formatted.push({
        type: 'header',
        content: line.replace(/^#+\s*/, ''),
        level: (line.match(/^#+/) || [''])[0].length || 1
      })
    }
    // Lists (lines starting with -, *, •, or numbers)
    else if (line.match(/^[-*•]\s+/) || line.match(/^\d+\.\s+/)) {
      formatted.push({
        type: 'list-item',
        content: line.replace(/^[-*•]\s+/, '').replace(/^\d+\.\s+/, ''),
        isNumbered: line.match(/^\d+\./)
      })
    }
    // Bold text (**text** or __text__)
    else if (line.includes('**') || line.includes('__')) {
      formatted.push({
        type: 'text',
        content: line,
        hasBold: true
      })
    }
    // Regular text
    else {
      formatted.push({
        type: 'text',
        content: line
      })
    }
  }
  
  return formatted
}

const FormattedContent = ({ content }) => {
  const formatted = formatResponseText(content)
  
  return (
    <div className="space-y-4">
      {formatted.map((item, index) => {
        switch (item.type) {
          case 'header':
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`
                  ${item.level === 1 ? 'text-xl font-bold' : 'text-lg font-semibold'}
                  text-slate-900 py-3 px-4 rounded-lg
                  bg-gradient-to-r from-rose-50 to-orange-50 
                  border-l-4 border-rose-300
                  shadow-sm
                `}
              >
                {item.content}
              </motion.div>
            )
          
          case 'list-item':
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className="flex items-start space-x-3 py-2 px-4 rounded-lg bg-slate-50 border border-slate-200"
              >
                <span className="inline-block w-2 h-2 bg-rose-400 rounded-full mt-2.5 flex-shrink-0" />
                <span className="text-slate-700 leading-relaxed">
                  {item.content}
                </span>
              </motion.div>
            )
          
          case 'text':
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: index * 0.03 }}
                className="text-slate-700 leading-relaxed px-2"
                dangerouslySetInnerHTML={{
                  __html: item.hasBold 
                    ? item.content.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-slate-900 bg-yellow-100 px-1 rounded">$1</strong>')
                        .replace(/__(.*?)__/g, '<strong class="font-semibold text-slate-900 bg-yellow-100 px-1 rounded">$1</strong>')
                    : item.content
                }}
              />
            )
          
          case 'break':
            return <div key={index} className="h-3" />
          
          default:
            return null
        }
      })}
    </div>
  )
}

const ResponseDisplay = ({ response }) => {
  const [showSteps, setShowSteps] = useState(false)
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(response.result)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  if (!response) return null

  const droneUsed = response.drone_used?.toLowerCase()?.split(' ')[0]
  const DroneIcon = droneIcons[droneUsed] || Brain

  return (
    <motion.div
      className="space-y-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      {/* Response Content with Icon Header */}
      <motion.div
        className="card p-8 bg-gradient-to-br from-white via-rose-50/30 to-orange-50/30 border border-rose-100 relative"
        layout
      >
        {/* Floating Action Buttons */}
        <div className="absolute top-4 right-4 flex items-center space-x-2">
          <motion.button
            onClick={handleCopy}
            className="p-2 rounded-lg bg-white/80 border border-rose-200 hover:bg-rose-50 hover:shadow-md transition-all backdrop-blur-sm"
            whileHover={{ scale: 1.05, y: -1 }}
            whileTap={{ scale: 0.95 }}
          >
            {copied ? (
              <Check className="w-4 h-4 text-green-500" />
            ) : (
              <Copy className="w-4 h-4 text-slate-600" />
            )}
          </motion.button>
          
          {response.steps && (
            <motion.button
              onClick={() => setShowSteps(!showSteps)}
              className={`
                p-2 rounded-lg border transition-all backdrop-blur-sm
                ${showSteps 
                  ? 'bg-gradient-to-r from-rose-400 to-orange-400 text-white border-transparent shadow-lg' 
                  : 'bg-white/80 border-rose-200 hover:bg-rose-50 text-slate-600'
                }
              `}
              whileHover={{ scale: 1.05, y: -1 }}
              whileTap={{ scale: 0.95 }}
            >
              {showSteps ? (
                <EyeOff className="w-4 h-4" />
              ) : (
                <Eye className="w-4 h-4" />
              )}
            </motion.button>
          )}
        </div>

        {/* Icon and Response */}
        <div className="flex items-start space-x-4">
          <div className="p-3 rounded-xl bg-gradient-to-r from-rose-400 to-orange-400 shadow-lg flex-shrink-0">
            <DroneIcon className="w-5 h-5 text-white" />
          </div>
          <div className="flex-1 min-w-0">
            {response.success ? (
              <FormattedContent content={response.result} />
            ) : (
              <div className="text-red-700 bg-red-50 p-4 rounded-xl border border-red-200">
                <span className="font-medium">
                  {response.error || 'An unexpected error occurred'}
                </span>
              </div>
            )}
          </div>
        </div>
      </motion.div>

      {/* Processing Steps */}
      <AnimatePresence>
        {showSteps && response.steps && (
          <motion.div
            className="card p-6 bg-gradient-to-br from-slate-50 to-rose-50/50 border border-rose-100"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
          >
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-2 rounded-lg bg-gradient-to-r from-rose-400 to-orange-400">
                <Eye className="w-4 h-4 text-white" />
              </div>
              <h4 className="font-display text-lg font-semibold text-slate-900">
                Deployment Steps
              </h4>
            </div>
            
            <div className="space-y-3">
              {response.steps.split('\n').map((step, index) => (
                <motion.div
                  key={index}
                  className="flex items-start space-x-4"
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <div className="w-6 h-6 rounded-full bg-gradient-to-r from-rose-400 to-orange-400 flex items-center justify-center text-white text-xs font-bold flex-shrink-0 mt-0.5">
                    {index + 1}
                  </div>
                  <div className="bg-white p-4 rounded-xl flex-1 border border-rose-200 shadow-sm">
                    <code className="text-sm text-slate-700 font-mono">
                      {step}
                    </code>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

export default ResponseDisplay