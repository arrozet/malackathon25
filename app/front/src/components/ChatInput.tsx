/**
 * ChatInput Component - Input field for sending chat messages.
 * 
 * This component provides an accessible input interface with:
 * - Enter key submission
 * - Disabled state during loading
 * - Clear visual feedback
 * - Keyboard accessibility
 */

import { useState, useRef, type ReactElement, type FormEvent, type KeyboardEvent } from 'react'

/**
 * Props for the ChatInput component.
 */
export interface ChatInputProps {
  /** Callback when a message is submitted */
  onSendMessage: (message: string) => void
  /** Whether the input should be disabled (e.g., while loading) */
  disabled?: boolean
  /** Placeholder text for the input */
  placeholder?: string
}

/**
 * ChatInput component.
 * 
 * Provides a text input with submit button for sending messages.
 * Supports both button click and Enter key submission.
 * 
 * @param props - Component props
 * @returns React element for the chat input
 */
export default function ChatInput({ 
  onSendMessage, 
  disabled = false,
  placeholder = 'Escribe tu pregunta...'
}: ChatInputProps): ReactElement {
  const [inputValue, setInputValue] = useState('')
  const inputRef = useRef<HTMLTextAreaElement>(null)

  /**
   * Handles form submission.
   * Prevents default, sends message, and clears input.
   */
  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    
    const trimmedValue = inputValue.trim()
    if (!trimmedValue || disabled) return

    onSendMessage(trimmedValue)
    setInputValue('')
    
    // Focus back on input after sending
    inputRef.current?.focus()
  }

  /**
   * Handles keyboard events in the textarea.
   * Submits on Enter (without Shift).
   */
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e as unknown as FormEvent)
    }
  }

  return (
    <form className="chat-input" onSubmit={handleSubmit}>
      <div className="chat-input__wrapper">
        <textarea
          ref={inputRef}
          className="chat-input__field"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          rows={1}
          aria-label="Campo de mensaje"
          aria-describedby="chat-input-hint"
        />
        
        <button
          type="submit"
          className="chat-input__button"
          disabled={disabled || !inputValue.trim()}
          aria-label="Enviar mensaje"
        >
          <svg
            className="chat-input__icon"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            aria-hidden="true"
          >
            <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
          </svg>
        </button>
      </div>
      
      <span id="chat-input-hint" className="chat-input__hint">
        Presiona Enter para enviar, Shift+Enter para nueva línea
      </span>
    </form>
  )
}

