import { useEffect, useMemo, useState } from 'react'
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

const API_BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

function App() {
  const [insights, setInsights] = useState<InsightSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

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

  return (
    <div className="page">
      <header className="hero">
        <div className="hero__badge-row">
          <span className="badge">Brain · Investigación clínica</span>
          {connectionBadge}
        </div>
        <h1>Insights iniciales sobre admisiones de salud mental</h1>
        <p className="hero__subtitle">
          Esta vista previa permite validar flujos de datos y la experiencia visual antes de conectar la base de datos Oracle definitiva.
        </p>
        {insights && (
          <div className="hero__highlights">
            {insights.highlight_phrases.map((phrase) => (
              <span key={phrase} className="highlight-pill">
                {phrase}
              </span>
            ))}
          </div>
        )}
      </header>

      <main className="content">
        {loading && <p className="status">Cargando insights...</p>}

        {error && !loading && <p className="status status--error">{error}</p>}

        {insights && !loading && !error && (
          <section className="grid" aria-label="Resúmenes por dimensión analítica">
            {insights.metric_sections.map((section) => (
              <article key={section.title} className="card" aria-labelledby={`section-${section.title}`}>
                <div className="card__header">
                  <h2 id={`section-${section.title}`}>{section.title}</h2>
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
