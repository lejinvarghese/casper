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

const renderMarkdown = (text) => {
  if (!text) return ''
  
  let html = text
    // Headers
    .replace(/^### (.*$)/gim, '<h3 class="text-lg font-semibold text-slate-900 mt-6 mb-3">$1</h3>')
    .replace(/^## (.*$)/gim, '<h2 class="text-xl font-bold text-slate-900 mt-6 mb-4">$1</h2>')
    .replace(/^# (.*$)/gim, '<h1 class="text-2xl font-bold text-slate-900 mt-6 mb-4">$1</h1>')
    
    // Images - detect URLs that are images and render them
    .replace(/(https?:\/\/[^\s]+\.(?:jpg|jpeg|png|gif|webp|svg))/gi, '<div class="my-6"><img src="$1" alt="Generated artwork" class="max-w-full h-auto rounded-lg shadow-lg border border-slate-200" loading="lazy" /></div>')
    
    // Artwork creation messages with URLs - handle various formats
    .replace(/🎨 \[.*?\]\((https?:\/\/[^\)]+)\)/gi, '<div class="my-6 p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl border border-purple-200"><div class="flex items-center space-x-2 mb-3"><span class="text-2xl">🎨</span><span class="font-semibold text-slate-900">Artwork Created</span></div><img src="$1" alt="Generated artwork" class="max-w-full h-auto rounded-lg shadow-lg border border-slate-200" loading="lazy" /><div class="mt-3 text-sm text-slate-600"><a href="$1" target="_blank" rel="noopener noreferrer" class="text-purple-600 hover:text-purple-800 underline">View full size</a></div></div>')
    .replace(/🎨 Artwork created: (https?:\/\/[^\s]+)/gi, '<div class="my-6 p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl border border-purple-200"><div class="flex items-center space-x-2 mb-3"><span class="text-2xl">🎨</span><span class="font-semibold text-slate-900">Artwork Created</span></div><img src="$1" alt="Generated artwork" class="max-w-full h-auto rounded-lg shadow-lg border border-slate-200" loading="lazy" /><div class="mt-3 text-sm text-slate-600"><a href="$1" target="_blank" rel="noopener noreferrer" class="text-purple-600 hover:text-purple-800 underline">View full size</a></div></div>')
    
    // Bold text
    .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-slate-900">$1</strong>')
    .replace(/__(.*?)__/g, '<strong class="font-semibold text-slate-900">$1</strong>')
    
    // Italic text
    .replace(/\*(.*?)\*/g, '<em class="italic text-slate-800">$1</em>')
    .replace(/_(.*?)_/g, '<em class="italic text-slate-800">$1</em>')

  // Handle lists properly
  const lines = html.split('\n')
  const processedLines = []
  let inList = false
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim()
    
    if (line.match(/^[-*•]\s+/)) {
      const content = line.replace(/^[-*•]\s+/, '')
      if (!inList) {
        processedLines.push('<ul class="list-disc list-inside space-y-2 mb-4 ml-4 text-slate-700">')
        inList = true
      }
      processedLines.push(`<li class="leading-relaxed">${content}</li>`)
    } else {
      if (inList) {
        processedLines.push('</ul>')
        inList = false
      }
      if (line) {
        processedLines.push(`<p class="mb-4 leading-relaxed text-slate-700">${line}</p>`)
      } else {
        processedLines.push('<div class="h-2"></div>')
      }
    }
  }
  
  if (inList) {
    processedLines.push('</ul>')
  }
  
  return processedLines.join('')
}

const FormattedContent = ({ content }) => {
  const formattedHtml = renderMarkdown(content)
  
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
      className="prose prose-slate max-w-none"
      dangerouslySetInnerHTML={{ __html: formattedHtml }}
    />
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