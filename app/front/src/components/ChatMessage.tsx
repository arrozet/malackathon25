/**
 * ChatMessage Component - Renders an individual chat message.
 * 
 * This component displays a message from either the user or the AI assistant,
 * with appropriate styling and accessibility support.
 */

import type { ReactElement } from 'react'
import type { ChatMessage as ChatMessageType } from '../types/chat'

/**
 * Props for the ChatMessage component.
 */
export interface ChatMessageProps {
  /** The message data to display */
  message: ChatMessageType
}

/**
 * Formats a timestamp into a readable time string.
 * 
 * @param timestamp - Date to format
 * @returns Formatted time string (HH:MM)
 */
function formatTime(timestamp?: Date): string {
  if (!timestamp) return ''
  
  const date = timestamp instanceof Date ? timestamp : new Date(timestamp)
  const hours = date.getHours().toString().padStart(2, '0')
  const minutes = date.getMinutes().toString().padStart(2, '0')
  
  return `${hours}:${minutes}`
}

/**
 * ChatMessage component.
 * 
 * Renders a single message with appropriate styling based on the role (user/assistant).
 * Includes timestamp and optional tool usage indicators.
 * 
 * @param props - Component props
 * @returns React element for the chat message
 */
export default function ChatMessage({ message }: ChatMessageProps): ReactElement {
  const isUser = message.role === 'user'
  const isAssistant = message.role === 'assistant'

  return (
    <div 
      className={`chat-message ${isUser ? 'chat-message--user' : 'chat-message--assistant'}`}
      role="article"
      aria-label={`Mensaje de ${isUser ? 'usuario' : 'asistente'}`}
    >
      <div className="chat-message__content">
        {/* Message text */}
        <div className="chat-message__text">
          {message.content}
        </div>

        {/* Footer with timestamp and tools */}
        <div className="chat-message__footer">
          {message.timestamp && (
            <span className="chat-message__time" aria-label="Hora del mensaje">
              {formatTime(message.timestamp)}
            </span>
          )}

          {/* Show tools used by assistant */}
          {isAssistant && message.toolsUsed && message.toolsUsed.length > 0 && (
            <div className="chat-message__tools" aria-label="Herramientas utilizadas">
              {message.toolsUsed.map((tool, index) => (
                <span key={index} className="chat-message__tool-badge">
                  {tool}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

