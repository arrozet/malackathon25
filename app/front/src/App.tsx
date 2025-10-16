/**
 * App Component - Main application component for Brain.
 * 
 * This component renders the complete Brain experience as a single-page application
 * with modular sections and dynamic data from mental health admissions.
 */

import { useMemo } from 'react'
import type { ReactElement } from 'react'
import BrainIcon from './components/BrainIcon'
import LayoutSection from './components/LayoutSection'
import DataExplorer from './pages/DataExplorer'
import { useInsights } from './hooks'
import { NAV_ITEMS } from './utils/constants'
import { formatDateTime } from './utils/formatting'
import './App.css'

/**
 * Main App component that orchestrates the Brain UI.
 * 
 * Uses the useInsights hook to fetch analytical data and renders
 * a multi-section interface including insights, data exploration,
 * and roadmap sections.
 * 
 * @returns React element for the complete Brain application
 */
function App(): ReactElement {
  // Fetch insights using custom hook (handles loading, error, cleanup)
  const { insights, loading, error } = useInsights()

  /**
   * Memoized connection badge component.
   * Shows database connection status based on insights data.
   */
  const connectionBadge = useMemo(() => {
    if (!insights) {
      return null
    }

    return insights.database_connected ? (
      <span className="badge badge--ok">Oracle conectado</span>
    ) : (
      <span className="badge badge--warn">Oracle pendiente</span>
    )
  }, [insights])

  // Extract highlight phrases with fallback to empty array
  const highlightPhrases = insights?.highlight_phrases ?? []

  return (
    <div className="page">
      {/* Top navigation bar */}
      <header className="top-bar">
        <span className="brand" aria-label="Brain, tu compañera de investigación">
          Brain<span className="brand__spark" />
        </span>
        <nav className="nav" aria-label="Secciones principales de Brain">
          {NAV_ITEMS.map((item) => (
            <a key={item.id} href={`#${item.id}`} className="nav__link">
              {item.label}
            </a>
          ))}
        </nav>
      </header>

      {/* Main content area */}
      <main className="content">
        {/* Hero section with Brain icon and highlights */}
        <section className="hero" id="vision">
          <div className="hero__visual" aria-hidden="true">
            <BrainIcon className="hero__icon" />
            <div className="hero__glow" />
          </div>
          <div className="hero__content">
            <div className="hero__badge-row">
              <span className="badge">Brain · Investigación clínica</span>
              {connectionBadge}
            </div>
            <h1>Insights iniciales sobre admisiones de salud mental</h1>
            <p className="hero__subtitle">
              Brain es la compañera artificial para investigadores de salud mental. Centraliza la
              ingesta de datos, acelera la segmentación y presenta heurísticas accionables para
              comités clínicos.
            </p>
            <div className="hero__highlight-stack" aria-live="polite">
              {highlightPhrases.length > 0 ? (
                highlightPhrases.map((phrase) => (
                  <span key={phrase} className="highlight-pill">
                    {phrase}
                  </span>
                ))
              ) : (
                <span className="highlight-pill highlight-pill--placeholder">
                  Conecta tu dataset para generar titulares inmediatos.
                </span>
              )}
            </div>
          </div>
        </section>

        {/* Insights section with metrics cards */}
        <LayoutSection
          id="insights"
          title="Insights clave"
          description="Explora métricas resumidas por dimensión analítica. Cada tarjeta agrupa indicadores calculados a partir de registros de admisiones anonimizadas."
        >
          {loading && <p className="status">Cargando insights...</p>}

          {error && !loading && <p className="status status--error">{error}</p>}

          {insights && !loading && !error && (
            <section className="grid" aria-label="Resúmenes por dimensión analítica">
              {insights.metric_sections.map((section) => (
                <article
                  key={section.title}
                  className="card"
                  aria-labelledby={`section-${section.title}`}
                >
                  <div className="card__header">
                    <h3 id={`section-${section.title}`}>{section.title}</h3>
                    <span className="card__period">{insights.sample_period}</span>
                  </div>
                  <ul className="card__metric-list">
                    {section.metrics.map((metric) => (
                      <li key={metric.title} className="card__metric-item">
                        <p className="metric__title">{metric.title}</p>
                        <p className="metric__value">{metric.value}</p>
                        <p className="metric__description">{metric.description}</p>
                      </li>
                    ))}
                  </ul>
                </article>
              ))}
            </section>
          )}
        </LayoutSection>

        {/* Data explorer section */}
        <LayoutSection
          id="explorer"
          title="Exploración interactiva de datos"
          description="Herramientas de análisis visual con filtrado dinámico para profundizar en las admisiones de salud mental."
        >
          <DataExplorer />
        </LayoutSection>

        {/* Roadmap section */}
        <LayoutSection
          id="roadmap"
          title="Próxima iteración"
          description="Trazamos la hoja de ruta para llegar a la versión evaluable por el jurado del Malackathon."
        >
          <ul className="roadmap">
            <li>
              <strong>Conexión segura Oracle:</strong> Implementar wallet OCI y rotación de
              credenciales en despliegues Docker.
            </li>
            <li>
              <strong>Panel comparativo:</strong> Añadir gráficos longitudinales de readmisiones y
              segmentación por unidades clínicas.
            </li>
            <li>
              <strong>Alertas personalizadas:</strong> Definir reglas de negocio exportables para
              equipos multidisciplinares.
            </li>
          </ul>
        </LayoutSection>
      </main>

      {/* Footer */}
      <footer className="footer">
        <small>
          Prototipo Malackathon 2025 · Generado{' '}
          {insights ? formatDateTime(insights.generated_at) : 'sin conexión'}
        </small>
      </footer>
    </div>
  )
}

export default App
