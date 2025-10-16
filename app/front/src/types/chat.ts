/**
 * Type definitions for AI Chat functionality.
 * 
 * These types mirror the backend schemas for chat interactions
 * with the Brain AI assistant.
 */

/**
 * Represents a single message in the chat conversation.
 */
export interface ChatMessage {
  /** Role of the message sender: 'user' or 'assistant' */
  role: 'user' | 'assistant'
  /** Content of the message */
  content: string
  /** Timestamp when the message was created (client-side) */
  timestamp?: Date
  /** Tools used by the assistant for this message (if applicable) */
  toolsUsed?: string[]
}

/**
 * Request payload for sending a chat message to the AI.
 */
export interface ChatRequest {
  /** User's message to send */
  message: string
  /** Optional conversation history */
  chatHistory?: ChatMessage[]
}

/**
 * Response payload from the AI chat endpoint.
 */
export interface ChatResponse {
  /** AI assistant's response message */
  response: string
  /** List of tools used to generate the response */
  tool_calls?: string[]
  /** Detailed intermediate steps (for debugging) */
  intermediate_steps?: IntermediateStep[]
}

/**
 * Intermediate step taken by the AI agent.
 */
export interface IntermediateStep {
  /** Tool name used */
  tool: string
  /** Input provided to the tool */
  tool_input: string | Record<string, unknown>
  /** Output from the tool */
  output: string
}

