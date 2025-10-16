/**
 * ThinkingChain Component - Displays AI thinking progress in real-time.
 * 
 * This component shows a step-by-step visualization of the multi-agent system's
 * thinking process, similar to ChatGPT's chain of thought display.
 */

import type { ReactElement } from 'react'
import type { ThinkingStep } from '../types/chat'

/**
 * Props for the ThinkingChain component.
 */
export interface ThinkingChainProps {
  /** Array of thinking steps to display */
  steps: ThinkingStep[]
  /** Whether the AI is currently processing (shows pulsing animation) */
  isThinking?: boolean
}

/**
 * ThinkingChain component.
 * 
 * Renders a vertical timeline of thinking steps with icons, messages,
 * and animations to indicate progress.
 * 
 * @param props - Component props
 * @returns React element for the thinking chain
 */
export default function ThinkingChain({ steps, isThinking = false }: ThinkingChainProps): ReactElement | null {
  // Don't render anything if no steps
  if (steps.length === 0 && !isThinking) {
    return null
  }

  return (
    <div 
      className="thinking-chain"
      role="status"
      aria-live="polite"
      aria-label="Progreso del asistente"
    >
      <div className="thinking-chain__container">
        {steps.map((step, index) => (
          <div 
            key={step.id}
            className={`thinking-chain__step ${step.isActive ? 'thinking-chain__step--active' : 'thinking-chain__step--complete'}`}
          >
            {/* Timeline connector */}
            {index > 0 && <div className="thinking-chain__connector" />}
            
            {/* Step icon */}
            <div className="thinking-chain__icon">
              {getStepIcon(step.type, step.isActive)}
            </div>
            
            {/* Step message */}
            <div className="thinking-chain__message">
              {step.message}
            </div>
          </div>
        ))}
        
        {/* Pulsing indicator when thinking */}
        {isThinking && steps.length > 0 && (
          <div className="thinking-chain__pulse">
            <div className="thinking-chain__pulse-dot" />
            <div className="thinking-chain__pulse-dot" />
            <div className="thinking-chain__pulse-dot" />
          </div>
        )}
      </div>
    </div>
  )
}

/**
 * Returns the appropriate icon for a thinking step.
 * 
 * @param type - Type of thinking step
 * @param isActive - Whether the step is currently active
 * @returns SVG icon element
 */
function getStepIcon(type: string, isActive: boolean): ReactElement {
  const iconClass = isActive ? 'thinking-chain__icon-svg--active' : 'thinking-chain__icon-svg'
  
  switch (type) {
    case 'thinking':
      return (
        <svg className={iconClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
      )
    
    case 'routing':
      return (
        <svg className={iconClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
        </svg>
      )
    
    case 'specialist_start':
    case 'specialist_complete':
      return (
        <svg className={iconClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
      )
    
    case 'synthesizing':
      return (
        <svg className={iconClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
        </svg>
      )
    
    case 'complete':
      return (
        <svg className={iconClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      )
    
    case 'error':
      return (
        <svg className={iconClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      )
    
    default:
      return (
        <svg className={iconClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <circle cx="12" cy="12" r="10" strokeWidth={2} />
        </svg>
      )
  }
}

