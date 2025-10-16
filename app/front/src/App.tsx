import { useEffect, useMemo, useState } from 'react'
import type { ReactElement } from 'react'
import BrainIcon from './components/BrainIcon'
import LayoutSection from './components/LayoutSection'
import DataExplorer from './pages/DataExplorer'
import './App.css'

type InsightMetric = {
  title: string
  value: string
  description: string
}

type InsightSection = {
  title: string
  metrics: InsightMetric[]
}

type InsightSummary = {
  generated_at: string
  sample_period: string
  highlight_phrases: string[]
  metric_sections: InsightSection[]
  database_connected: boolean
}

// Use relative path for API calls (works through nginx proxy)
// This way it works from any origin (localhost, IP, domain, etc.)
const API_BASE_URL = '/api'

const NAV_ITEMS = [
  { id: 'vision', label: 'Visión general' },
  { id: 'insights', label: 'Insights clave' },
  { id: 'explorer', label: 'Exploración de datos' },
  { id: 'roadmap', label: 'Proyección' },
]

/**
 * Renderiza la experiencia Brain como una SPA con secciones modulares y datos dinámicos de selección clínica.
 * @returns ReactElement principal de la interfaz Brain que encapsula toda la experiencia.
 */
function App(): ReactElement {
  const [insights, setInsights] = useState<InsightSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Recuperamos los insights del backend de FastAPI, controlando abortos para evitar asignaciones en componentes desmontados.
  useEffect(() => {
    const controller = new AbortController()

    async function fetchInsights() {
      try {
        const response = await fetch(`${API_BASE_URL}/insights`, {
          signal: controller.signal,
        })

        if (!response.ok) {
          throw new Error(`Error ${response.status}: ${response.statusText}`)
        }

        const data: InsightSummary = await response.json()
        setInsights(data)
        setError(null)
      } catch (fetchError) {
        if ((fetchError as Error).name === 'AbortError') {
          return
        }
        setError('No se pudo conectar con el backend. Verifica que el servicio FastAPI esté activo.')
      } finally {
        setLoading(false)
      }
    }

    fetchInsights()

    return () => controller.abort()
  }, [])

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

  const highlightPhrases = insights?.highlight_phrases ?? []

  return (
    <div className="page">
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

      <main className="content">
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
              Brain es la compañera artificial para investigadores de salud mental. Centraliza la ingesta de datos, acelera la segmentación y presenta heurísticas accionables para comités clínicos.
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
                <article key={section.title} className="card" aria-labelledby={`section-${section.title}`}>
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

        <LayoutSection
          id="explorer"
          title="Exploración interactiva de datos"
          description="Herramientas de análisis visual con filtrado dinámico para profundizar en las admisiones de salud mental."
        >
          <DataExplorer />
        </LayoutSection>

        <LayoutSection
          id="roadmap"
          title="Próxima iteración"
          description="Trazamos la hoja de ruta para llegar a la versión evaluable por el jurado del Malackathon."
        >
          <ul className="roadmap">
            <li>
              <strong>Conexión segura Oracle:</strong> Implementar wallet OCI y rotación de credenciales en despliegues Docker.
            </li>
            <li>
              <strong>Panel comparativo:</strong> Añadir gráficos longitudinales de readmisiones y segmentación por unidades clínicas.
            </li>
            <li>
              <strong>Alertas personalizadas:</strong> Definir reglas de negocio exportables para equipos multidisciplinares.
            </li>
          </ul>
        </LayoutSection>
      </main>

      <footer className="footer">
        <small>
          Prototipo Malackathon 2025 · Generado{' '}
          {insights ? new Date(insights.generated_at).toLocaleString() : 'sin conexión'}
        </small>
      </footer>
    </div>
  )
}

export default App
