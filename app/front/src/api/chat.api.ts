/**
 * Chat API Service - Handles communication with the AI chat endpoints.
 * 
 * This service provides functions to interact with the Brain AI assistant,
 * following the established API service pattern with centralized error handling.
 */

import { get, post } from './client'
import type { ChatRequest, ChatResponse } from '../types/chat'

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

