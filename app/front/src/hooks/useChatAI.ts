/**
 * Custom hook for managing AI chat interactions.
 * 
 * This hook encapsulates all chat-related business logic including:
 * - Message history management
 * - Sending messages and receiving responses
 * - Loading and error states
 * - Automatic cleanup on unmount
 * 
 * Following Clean Architecture principles, this hook acts as the Logic Layer
 * that components can use without knowing implementation details.
 */

import { useState, useCallback, useRef, useEffect } from 'react'
import { sendChatMessageStream } from '../api/chat.api'
import type { ChatMessage, ThinkingStep } from '../types/chat'

/**
 * Hook return type defining the chat interface.
 */
export interface UseChatAIReturn {
  /** Array of chat messages (user and assistant) */
  messages: ChatMessage[]
  /** Current thinking steps (progress indicators) */
  thinkingSteps: ThinkingStep[]
  /** Whether a message is currently being sent */
  isLoading: boolean
  /** Error message if the last request failed */
  error: string | null
  /** Send a new message to the AI assistant */
  sendMessage: (message: string) => Promise<void>
  /** Clear all messages and reset the conversation */
  clearChat: () => void
}

/**
 * Custom hook for AI chat functionality.
 * 
 * @returns Chat interface with messages, state, and actions
 * 
 * @example
 * ```typescript
 * const { messages, isLoading, error, sendMessage, clearChat } = useChatAI();
 * 
 * // Send a message
 * await sendMessage("¿Cuántos episodios hay en 2023?");
 * 
 * // Clear conversation
 * clearChat();
 * ```
 */
export function useChatAI(): UseChatAIReturn {
  // State for message history
  const [messages, setMessages] = useState<ChatMessage[]>([])
  
  // State for thinking steps (progress indicators)
  const [thinkingSteps, setThinkingSteps] = useState<ThinkingStep[]>([])
  
  // Loading state
  const [isLoading, setIsLoading] = useState(false)
  
  // Error state
  const [error, setError] = useState<string | null>(null)
  
  // AbortController ref to cancel requests on unmount
  const abortControllerRef = useRef<AbortController | null>(null)
  
  // Counter for generating unique step IDs
  const stepIdCounter = useRef(0)

  /**
   * Cleanup on unmount.
   * Aborts any pending requests to prevent memory leaks.
   */
  useEffect(() => {
    return () => {
      // Cancel any pending request
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
    }
  }, [])

  /**
   * Sends a message to the AI assistant using streaming.
   * 
   * This function:
   * 1. Adds user message to history
   * 2. Sends request to backend with full conversation history
   * 3. Receives real-time thinking progress updates
   * 4. Adds assistant response to history when complete
   * 5. Handles errors gracefully
   * 
   * @param message - User's message text
   */
  const sendMessage = useCallback(async (message: string) => {
    // Validate input
    if (!message.trim()) {
      return
    }

    // Clear previous errors and thinking steps
    setError(null)
    setThinkingSteps([])
    setIsLoading(true)

    // Cancel any previous pending request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }

    // Create new AbortController for this request
    const abortController = new AbortController()
    abortControllerRef.current = abortController

    // Create user message
    const userMessage: ChatMessage = {
      role: 'user',
      content: message.trim(),
      timestamp: new Date()
    }

    // Optimistically add user message to UI
    setMessages(prev => [...prev, userMessage])

    try {
      // Send request with streaming
      await sendChatMessageStream(
        {
          message: message.trim(),
          chatHistory: messages  // Include previous messages for context
        },
        (event) => {
          // Handle each thinking event
          const stepId = `step-${++stepIdCounter.current}`
          
          if (event.type === 'complete') {
            // Final response received
            const assistantMessage: ChatMessage = {
              role: 'assistant',
              content: event.response || 'No se recibió respuesta.',
              timestamp: new Date(),
              toolsUsed: event.tools_used
            }

            // Add assistant response to messages
            setMessages(prev => [...prev, assistantMessage])
            
            // Mark all thinking steps as inactive
            setThinkingSteps(prev => 
              prev.map(step => ({ ...step, isActive: false }))
            )
            
            setIsLoading(false)
            
          } else if (event.type === 'error') {
            // Error occurred
            setError(event.message)
            
            const errorMessage: ChatMessage = {
              role: 'assistant',
              content: event.message,
              timestamp: new Date()
            }
            
            setMessages(prev => [...prev, errorMessage])
            setThinkingSteps([])
            setIsLoading(false)
            
          } else {
            // Progress event - add thinking step
            const newStep: ThinkingStep = {
              id: stepId,
              type: event.type,
              message: event.message,
              timestamp: new Date(),
              isActive: true
            }
            
            setThinkingSteps(prev => {
              // Mark previous step as inactive
              const updated = prev.map(step => ({ ...step, isActive: false }))
              // Add new active step
              return [...updated, newStep]
            })
          }
        },
        abortController.signal  // Pass abort signal
      )

    } catch (err) {
      // Ignore abort errors (they're expected when component unmounts)
      if (err instanceof Error && err.name === 'AbortError') {
        return
      }

      // Handle other errors
      const errorMessage = err instanceof Error ? err.message : 'Error al comunicarse con el asistente'
      setError(errorMessage)

      // Add error message to chat
      const errorAssistantMessage: ChatMessage = {
        role: 'assistant',
        content: `Lo siento, ocurrió un error: ${errorMessage}. Por favor, intenta de nuevo.`,
        timestamp: new Date()
      }
      
      setMessages(prev => [...prev, errorAssistantMessage])
      setThinkingSteps([])
      setIsLoading(false)
    }
  }, [messages])

  /**
   * Clears all messages and resets the conversation.
   */
  const clearChat = useCallback(() => {
    setMessages([])
    setThinkingSteps([])
    setError(null)
  }, [])

  return {
    messages,
    thinkingSteps,
    isLoading,
    error,
    sendMessage,
    clearChat
  }
}

