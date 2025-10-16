/**
 * Chat API Service - Handles communication with the AI chat endpoints.
 * 
 * This service provides functions to interact with the Brain AI assistant,
 * following the established API service pattern with centralized error handling.
 */

import { get, post } from './client'
import type { ChatRequest, ChatResponse, ThinkingEvent } from '../types/chat'

/**
 * Sends a chat message to the AI assistant.
 * 
 * @param request - Chat request containing message and optional history
 * @param signal - Optional AbortSignal for request cancellation
 * @returns Promise resolving to the AI's response
 * @throws {APIError} If the request fails
 * 
 * @example
 * ```typescript
 * const response = await sendChatMessage({
 *   message: "¿Cuántos episodios hay en 2023?",
 *   chatHistory: []
 * });
 * ```
 */
export async function sendChatMessage(
  request: ChatRequest,
  signal?: AbortSignal
): Promise<ChatResponse> {
  const payload = {
    message: request.message,
    chat_history: request.chatHistory?.map(msg => ({
      role: msg.role,
      content: msg.content
    })) ?? []
  }

  return post<ChatResponse>('/ai/chat', payload, signal)
}

/**
 * Sends a chat message and receives streaming progress events.
 * 
 * This function consumes a Server-Sent Events (SSE) stream from the backend
 * that provides real-time feedback about the multi-agent thinking process.
 * 
 * @param request - Chat request containing message and optional history
 * @param onEvent - Callback invoked for each progress event
 * @param signal - Optional AbortSignal for request cancellation
 * @returns Promise that resolves when the stream completes
 * @throws {APIError} If the request fails
 * 
 * @example
 * ```typescript
 * await sendChatMessageStream(
 *   {
 *     message: "¿Cuántos episodios hay en 2023?",
 *     chatHistory: []
 *   },
 *   (event) => {
 *     console.log(event.type, event.message);
 *     if (event.type === 'complete') {
 *       console.log('Response:', event.response);
 *     }
 *   }
 * );
 * ```
 */
export async function sendChatMessageStream(
  request: ChatRequest,
  onEvent: (event: ThinkingEvent) => void,
  signal?: AbortSignal
): Promise<void> {
  const payload = {
    message: request.message,
    chat_history: request.chatHistory?.map(msg => ({
      role: msg.role,
      content: msg.content
    })) ?? []
  }

  const response = await fetch('/api/ai/chat/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
    signal
  })

  if (!response.ok) {
    const errorText = await response.text()
    throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`)
  }

  if (!response.body) {
    throw new Error('Response body is null')
  }

  // Read the stream
  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  try {
    while (true) {
      const { done, value } = await reader.read()
      
      if (done) {
        break
      }

      // Decode the chunk and add to buffer
      buffer += decoder.decode(value, { stream: true })

      // Process complete SSE events (format: "data: {json}\n\n")
      const lines = buffer.split('\n\n')
      
      // Keep the last incomplete line in the buffer
      buffer = lines.pop() || ''

      // Process complete events
      for (const line of lines) {
        if (line.trim().startsWith('data: ')) {
          const jsonStr = line.trim().substring(6) // Remove "data: " prefix
          
          try {
            const event: ThinkingEvent = JSON.parse(jsonStr)
            onEvent(event)
          } catch (e) {
            console.error('Failed to parse SSE event:', jsonStr, e)
          }
        }
      }
    }
  } finally {
    reader.releaseLock()
  }
}

/**
 * Checks the health status of the AI service.
 * 
 * @param signal - Optional AbortSignal for request cancellation
 * @returns Promise resolving to the health status
 * @throws {APIError} If the health check fails
 */
export async function checkAIHealth(signal?: AbortSignal): Promise<{
  status: string
  components: Record<string, boolean>
  error?: string
}> {
  return get('/ai/health', undefined, signal)
}

