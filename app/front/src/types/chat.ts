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

/**
 * Progress event types from the streaming AI endpoint.
 */
export type ThinkingEventType = 
  | 'thinking'          // General thinking/analysis
  | 'routing'           // Routing decision made
  | 'specialist_start'  // Specialist started working
  | 'specialist_complete' // Specialist completed
  | 'synthesizing'      // Final synthesis
  | 'complete'          // Response complete
  | 'error'             // Error occurred

/**
 * Progress event from the streaming chat endpoint.
 */
export interface ThinkingEvent {
  /** Type of event */
  type: ThinkingEventType
  /** Human-readable message about the current step */
  message: string
  /** Specialist name (for specialist_* events) */
  specialist?: string
  /** List of specialists being consulted (for routing event) */
  specialists?: string[]
  /** Final response (for complete event) */
  response?: string
  /** Tools used (for complete event) */
  tools_used?: string[]
  /** Whether errors occurred (for complete event) */
  has_errors?: boolean
}

/**
 * Thinking chain entry displayed in the UI.
 */
export interface ThinkingStep {
  /** Unique ID for this step */
  id: string
  /** Type of step */
  type: ThinkingEventType
  /** Display message */
  message: string
  /** Timestamp when the step was created */
  timestamp: Date
  /** Whether this step is currently active/in-progress */
  isActive: boolean
}

