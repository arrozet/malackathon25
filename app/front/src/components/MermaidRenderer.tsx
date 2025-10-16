/**
 * MermaidRenderer Component - Renders Mermaid diagrams.
 * 
 * This component takes Mermaid diagram code and renders it as an SVG diagram.
 * It uses the mermaid library to parse and render the diagrams with proper
 * error handling and accessibility features.
 */

import { useEffect, useRef, useState, type ReactElement } from 'react'
import mermaid from 'mermaid'

/**
 * Props for the MermaidRenderer component.
 */
export interface MermaidRendererProps {
  /** Mermaid diagram code to render */
  chart: string
  /** Optional unique ID for the diagram (auto-generated if not provided) */
  id?: string
}

// Initialize mermaid with configuration (only once)
let mermaidInitialized = false

function initializeMermaid() {
  if (!mermaidInitialized) {
    mermaid.initialize({
      startOnLoad: false,
      theme: 'dark',
      themeVariables: {
        primaryColor: '#7C3AED',
        primaryTextColor: '#E5E7EB',
        primaryBorderColor: '#A855F7',
        lineColor: '#A855F7',
        secondaryColor: '#6D28D9',
        tertiaryColor: '#5B21B6',
        background: '#0D0C1D',
        mainBkg: '#1F1E2E',
        secondBkg: '#2D2C3D',
        textColor: '#E5E7EB',
        border1: '#A855F7',
        border2: '#7C3AED',
        arrowheadColor: '#A855F7',
        fontFamily: 'Inter, system-ui, sans-serif',
      },
      flowchart: {
        curve: 'basis',
        padding: 20,
      },
      sequence: {
        actorMargin: 50,
        boxMargin: 10,
        boxTextMargin: 5,
        noteMargin: 10,
        messageMargin: 35,
      },
      securityLevel: 'loose', // Allow more flexibility
      suppressErrors: false, // Show errors for debugging
    })
    mermaidInitialized = true
    console.log('Mermaid v10 initialized with Brain theme')
  }
}

/**
 * MermaidRenderer component.
 * 
 * Renders Mermaid diagram code as an interactive SVG diagram.
 * Handles errors gracefully and provides accessibility features.
 * 
 * @param props - Component props
 * @returns React element for the rendered diagram
 */
export default function MermaidRenderer({ chart, id }: MermaidRendererProps): ReactElement {
  const containerRef = useRef<HTMLDivElement>(null)
  const [svg, setSvg] = useState<string>('')
  const [error, setError] = useState<string | null>(null)
  
  // Generate unique ID for this diagram
  const diagramId = useRef(id || `mermaid-${Math.random().toString(36).substr(2, 9)}`).current

  useEffect(() => {
    let cancelled = false
    let timeoutId: NodeJS.Timeout | null = null

    const renderDiagram = async () => {
      if (!chart) {
        return
      }

      try {
        // Clear previous content
        if (!cancelled) {
          setSvg('')
          setError(null)
        }

        console.log('Rendering Mermaid diagram:', chart.substring(0, 100))

        // Ensure mermaid is initialized
        initializeMermaid()

        // Add timeout to detect hanging renders
        timeoutId = setTimeout(() => {
          if (!cancelled) {
            console.error('Mermaid render timeout')
            setError('Timeout: El diagrama tardó demasiado en renderizar')
          }
        }, 10000) // 10 second timeout

        // Render the diagram
        const { svg: renderedSvg } = await mermaid.render(diagramId, chart)
        
        // Clear timeout if render succeeded
        if (timeoutId) {
          clearTimeout(timeoutId)
          timeoutId = null
        }
        
        if (!cancelled) {
          console.log('Mermaid render successful, SVG length:', renderedSvg.length)
          setSvg(renderedSvg)
        }
      } catch (err) {
        if (!cancelled) {
          console.error('Mermaid rendering error:', err)
          const errorMessage = err instanceof Error ? err.message : 'Error al renderizar el diagrama'
          setError(errorMessage)
        }
      }
    }

    renderDiagram()

    // Cleanup function
    return () => {
      cancelled = true
      if (timeoutId) {
        clearTimeout(timeoutId)
      }
    }
  }, [chart, diagramId])

  // Show error state
  if (error) {
    return (
      <div className="mermaid-error" role="alert">
        <div className="mermaid-error__icon" aria-hidden="true">
          ⚠️
        </div>
        <div className="mermaid-error__content">
          <p className="mermaid-error__title">Error al renderizar el diagrama</p>
          <p className="mermaid-error__message">{error}</p>
          <details className="mermaid-error__details">
            <summary>Ver código del diagrama</summary>
            <pre className="mermaid-error__code">
              <code>{chart}</code>
            </pre>
          </details>
        </div>
      </div>
    )
  }

  // Show loading state
  if (!svg) {
    return (
      <div className="mermaid-loading" role="status" aria-label="Cargando diagrama">
        <div className="mermaid-loading__spinner" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="10" strokeWidth="2" opacity="0.25" />
            <path d="M12 2a10 10 0 0 1 10 10" strokeWidth="2" strokeLinecap="round" />
          </svg>
        </div>
        <span className="mermaid-loading__text">Generando diagrama...</span>
      </div>
    )
  }

  // Render the diagram
  return (
    <div 
      ref={containerRef}
      className="mermaid-diagram"
      role="img"
      aria-label="Diagrama Mermaid"
    >
      <div 
        className="mermaid-diagram__content"
        dangerouslySetInnerHTML={{ __html: svg }}
      />
    </div>
  )
}

