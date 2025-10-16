/**
 * Tool Icons - Maps tool names to Font Awesome icons.
 * 
 * This module provides a mapping between backend tool names and their
 * visual representation using Font Awesome icons.
 */

import { type ReactElement } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { 
  faDatabase, 
  faGlobe, 
  faCode, 
  faChartLine,
  faDiagramProject,
  faBrain,
  faSearch,
  faTable,
  faWrench
} from '@fortawesome/free-solid-svg-icons'

/**
 * Tool metadata including icon and display name.
 */
export interface ToolInfo {
  /** Font Awesome icon component */
  icon: ReactElement
  /** Human-readable display name */
  name: string
  /** Color for the icon (Brain theme purple shades) */
  color: string
}

/**
 * Maps tool names to their icon representation.
 * 
 * @param toolName - Backend tool name (e.g., "oracle_rag", "internet_search")
 * @returns Tool information including icon and display name
 */
export function getToolInfo(toolName: string): ToolInfo {
  // Normalize tool name (handle variations)
  const normalized = toolName.toLowerCase().trim()
  
  // Map tools to icons
  const toolMap: Record<string, ToolInfo> = {
    // Database tools
    'oracle_rag': {
      icon: <FontAwesomeIcon icon={faDatabase} />,
      name: 'Base de Datos',
      color: '#7C3AED'
    },
    'oracle_database_query': {
      icon: <FontAwesomeIcon icon={faDatabase} />,
      name: 'Consulta SQL',
      color: '#7C3AED'
    },
    'database': {
      icon: <FontAwesomeIcon icon={faDatabase} />,
      name: 'Base de Datos',
      color: '#7C3AED'
    },
    
    // Internet search
    'internet_search': {
      icon: <FontAwesomeIcon icon={faGlobe} />,
      name: 'Búsqueda Web',
      color: '#A855F7'
    },
    'search': {
      icon: <FontAwesomeIcon icon={faSearch} />,
      name: 'Búsqueda',
      color: '#A855F7'
    },
    
    // Code execution
    'python_executor': {
      icon: <FontAwesomeIcon icon={faCode} />,
      name: 'Análisis Python',
      color: '#C4B5FD'
    },
    'python': {
      icon: <FontAwesomeIcon icon={faCode} />,
      name: 'Python',
      color: '#C4B5FD'
    },
    'code_execution': {
      icon: <FontAwesomeIcon icon={faCode} />,
      name: 'Ejecución de Código',
      color: '#C4B5FD'
    },
    
    // Data analysis
    'data_analysis': {
      icon: <FontAwesomeIcon icon={faChartLine} />,
      name: 'Análisis de Datos',
      color: '#9333EA'
    },
    'statistics': {
      icon: <FontAwesomeIcon icon={faChartLine} />,
      name: 'Estadísticas',
      color: '#9333EA'
    },
    
    // Diagrams
    'mermaid': {
      icon: <FontAwesomeIcon icon={faDiagramProject} />,
      name: 'Generación de Diagramas',
      color: '#7C3AED'
    },
    'mermaid_diagram': {
      icon: <FontAwesomeIcon icon={faDiagramProject} />,
      name: 'Diagrama',
      color: '#7C3AED'
    },
    'diagram': {
      icon: <FontAwesomeIcon icon={faDiagramProject} />,
      name: 'Diagrama',
      color: '#7C3AED'
    },
    
    // AI reasoning
    'reasoning': {
      icon: <FontAwesomeIcon icon={faBrain} />,
      name: 'Razonamiento IA',
      color: '#A855F7'
    },
    'ai': {
      icon: <FontAwesomeIcon icon={faBrain} />,
      name: 'IA',
      color: '#A855F7'
    },
  }
  
  // Return mapped tool or default
  return toolMap[normalized] || {
    icon: <FontAwesomeIcon icon={faWrench} />,
    name: toolName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
    color: '#9CA3AF'
  }
}

