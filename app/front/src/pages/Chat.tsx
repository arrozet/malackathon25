/**
 * Chat Page - AI Assistant chat interface.
 * 
 * This page provides a ChatGPT-like interface for interacting with the Brain AI assistant.
 * Users can ask questions about mental health admissions data and receive AI-powered responses.
 * 
 * Architecture:
 * - Uses useChatAI hook for business logic (Logic Layer)
 * - Composes ChatContainer, ChatMessage, and ChatInput components (Presentation Layer)
 * - Follows Clean Architecture with clear separation of concerns
 */

import type { ReactElement } from 'react'
import { useChatAI } from '../hooks'
import ChatContainer from '../components/ChatContainer'
import ChatMessage from '../components/ChatMessage'
import ChatInput from '../components/ChatInput'
import BrainIcon from '../components/BrainIcon'
import '../styles/Chat.css'

/**
 * Chat page component.
 * 
 * Provides a complete chat interface with:
 * - Message history display
 * - Message input
 * - Loading states
 * - Error handling
 * - Clear conversation option
 * 
 * @returns React element for the chat page
 */
export default function Chat(): ReactElement {
  // Use custom hook for chat logic (encapsulates all business logic)
  const { messages, isLoading, error, sendMessage, clearChat } = useChatAI()

  return (
    <div className="chat-page">
      {/* Header */}
      <header className="chat-header">
        <div className="chat-header__brand">
          <a href="/" className="chat-header__back" aria-label="Volver al inicio">
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              aria-hidden="true"
            >
              <path d="M19 12H5M12 19l-7-7 7-7" />
            </svg>
          </a>
          <BrainIcon className="chat-header__icon" />
          <div className="chat-header__text">
            <h1 className="chat-header__title">Brain AI Assistant</h1>
            <p className="chat-header__subtitle">
              Tu compañera de investigación en salud mental
            </p>
          </div>
        </div>

        {/* Actions */}
        <div className="chat-header__actions">
          {messages.length > 0 && (
            <button
              onClick={clearChat}
              className="chat-header__clear-button"
              aria-label="Limpiar conversación"
            >
              <svg
                className="chat-header__clear-icon"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                aria-hidden="true"
              >
                <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
              </svg>
              Limpiar chat
            </button>
          )}
        </div>
      </header>

      {/* Main chat area */}
      <main className="chat-main">
        {/* Messages container with auto-scroll */}
        <ChatContainer 
          isLoading={isLoading} 
          isEmpty={messages.length === 0}
        >
          {messages.map((message, index) => (
            <ChatMessage key={index} message={message} />
          ))}
        </ChatContainer>

        {/* Error display (if any) */}
        {error && (
          <div className="chat-error" role="alert" aria-live="assertive">
            <span className="chat-error__icon" aria-hidden="true">⚠</span>
            <span className="chat-error__text">{error}</span>
          </div>
        )}

        {/* Input area */}
        <div className="chat-input-wrapper">
          <ChatInput
            onSendMessage={sendMessage}
            disabled={isLoading}
            placeholder="Pregunta sobre admisiones, análisis, visualizaciones..."
          />
        </div>
      </main>

      {/* Footer with usage hints */}
      <footer className="chat-footer">
        <p className="chat-footer__hint">
          <strong>Ejemplos:</strong> "¿Cuántos episodios hay en 2023?", "Analiza la distribución por género", 
          "Genera un diagrama del proceso de admisión"
        </p>
        <p className="chat-footer__disclaimer">
          Brain utiliza IA para responder. Verifica información crítica con los datos originales.
        </p>
      </footer>
    </div>
  )
}

