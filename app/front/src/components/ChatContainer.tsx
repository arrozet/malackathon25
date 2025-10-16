/**
 * ChatContainer Component - Scrollable container for chat messages.
 * 
 * This component manages the message display area with:
 * - Automatic scroll to bottom on new messages
 * - Loading indicator
 * - Empty state
 * - Accessible scrolling region
 */

import { useEffect, useRef, type ReactElement, type ReactNode } from 'react'

/**
 * Props for the ChatContainer component.
 */
export interface ChatContainerProps {
  /** Child elements to render (typically ChatMessage components) */
  children: ReactNode
  /** Whether messages are currently loading */
  isLoading?: boolean
  /** Whether there are any messages */
  isEmpty?: boolean
}

/**
 * ChatContainer component.
 * 
 * Provides a scrollable container for chat messages with automatic
 * scrolling behavior and loading states.
 * 
 * @param props - Component props
 * @returns React element for the chat container
 */
export default function ChatContainer({ 
  children, 
  isLoading = false,
  isEmpty = false
}: ChatContainerProps): ReactElement {
  const containerRef = useRef<HTMLDivElement>(null)

  /**
   * Auto-scroll to bottom when new messages arrive.
   * Uses smooth scrolling for better UX.
   */
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTo({
        top: containerRef.current.scrollHeight,
        behavior: 'smooth'
      })
    }
  }, [children])

  return (
    <div 
      ref={containerRef}
      className="chat-container"
      role="log"
      aria-live="polite"
      aria-label="Historial de conversación"
    >
      {/* Empty state */}
      {isEmpty && !isLoading && (
        <div className="chat-container__empty">
          <div className="chat-container__empty-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
          </div>
          <h3 className="chat-container__empty-title">
            Inicia una conversación con Brain
          </h3>
          <p className="chat-container__empty-description">
            Pregunta sobre los datos de admisiones de salud mental, solicita análisis o visualizaciones.
          </p>
        </div>
      )}

      {/* Messages */}
      {!isEmpty && (
        <div className="chat-container__messages">
          {children}
        </div>
      )}

      {/* Loading indicator */}
      {isLoading && (
        <div className="chat-container__loading" aria-label="Cargando respuesta">
          <div className="chat-message chat-message--assistant">
            <div className="chat-message__content">
              <div className="typing-indicator">
                <span className="typing-indicator__dot"></span>
                <span className="typing-indicator__dot"></span>
                <span className="typing-indicator__dot"></span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

