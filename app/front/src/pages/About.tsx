/**
 * About Page - Company and product information.
 * 
 * This page provides detailed information about Dr. Artificial company
 * and Brain product, accessible from the footer.
 */

import { type ReactElement } from 'react'
import BrainIcon from '../components/BrainIcon'
import '../styles/About.css'

/**
 * About page component displaying company and product information.
 * 
 * @returns React element with about page content
 */
export default function About(): ReactElement {
  return (
    <div className="about-page">
      {/* Navigation back to home */}
      <header className="about-header">
        <a href="/" className="back-link">
          ← Volver al inicio
        </a>
      </header>

      <main className="about-main">
        {/* Hero section */}
        <section className="about-hero">
          <div className="about-hero-icon">
            <BrainIcon className="hero-brain-icon" />
          </div>
          <h1>Acerca de nosotros</h1>
          <p className="about-tagline">
            Inteligencia artificial al servicio de la salud mental
          </p>
        </section>

        {/* Company info */}
        <section className="about-section">
          <div className="about-card">
            <h2>Dr. Artificial</h2>
            <p>
              Somos <strong>Dr. Artificial</strong>, una compañía especializada en soluciones de
              inteligencia artificial aplicadas al sector sanitario. Nuestro objetivo es transformar
              la manera en que los profesionales de la salud mental acceden, analizan y utilizan los
              datos clínicos para mejorar la atención al paciente.
            </p>
            <p>
              Creemos en el poder de los datos para transformar vidas. Por eso desarrollamos
              herramientas que facilitan la investigación clínica, aceleran el descubrimiento de
              patrones significativos y ayudan a los equipos médicos a tomar decisiones más
              informadas.
            </p>
          </div>

          <div className="about-card">
            <h2>Brain: Tu compañera de investigación</h2>
            <p>
              <strong>Brain</strong> es nuestro producto estrella: una plataforma inteligente diseñada
              para investigadores y profesionales clínicos que trabajan con datos de admisiones de salud
              mental. Brain centraliza la ingesta de datos, acelera el análisis exploratorio y presenta
              insights accionables de forma clara y visual.
            </p>
            <p>
              La plataforma combina potentes capacidades de filtrado y visualización con una interfaz
              minimalista y enfocada, permitiendo a los investigadores concentrarse en lo que realmente
              importa: encontrar patrones que mejoren la atención al paciente.
            </p>
          </div>

          <div className="about-card">
            <h2>Tecnología de vanguardia</h2>
            <p>
              Brain está construido con tecnologías modernas y escalables:
            </p>
            <ul className="tech-list">
              <li>
                <strong>React + TypeScript + Vite</strong> para una experiencia de usuario fluida,
                tipo-segura y con tiempos de carga mínimos
              </li>
              <li>
                <strong>FastAPI</strong> para un backend robusto, performante y con documentación
                automática OpenAPI
              </li>
              <li>
                <strong>Oracle Autonomous Database 23ai</strong> para garantizar seguridad, escalabilidad
                y cumplimiento normativo en el manejo de datos sensibles de salud
              </li>
              <li>
                <strong>Docker + CI/CD</strong> para despliegues consistentes, reproducibles y automatizados
              </li>
            </ul>
          </div>

          <div className="about-card">
            <h2>Nuestra misión</h2>
            <p>
              Democratizar el acceso a herramientas avanzadas de análisis de datos para profesionales
              de la salud mental. Queremos que cada investigador, sin importar su nivel técnico, pueda
              explorar datos complejos y extraer conocimiento valioso que mejore la vida de los pacientes.
            </p>
          </div>

          <div className="about-card about-card--highlight">
            <h2>Contáctanos</h2>
            <p>
              ¿Interesado en Brain o en nuestras otras soluciones? Visítanos en{' '}
              <a 
                href="https://dr-artificial.com" 
                target="_blank" 
                rel="noopener noreferrer"
                className="about-link"
              >
                dr-artificial.com
              </a>
            </p>
            <p className="contact-note">
              Brain y nuestras demás soluciones están al servicio de equipos médicos y de
              investigación que buscan aprovechar el poder de los datos para salvar vidas.
            </p>
          </div>
        </section>

        {/* Hackathon credit */}
        <section className="about-credit">
          <p>
            <small>
              Brain fue desarrollado como parte del <strong>II Malackathon 2025</strong>, un evento
              centrado en la innovación tecnológica aplicada a la salud mental.
            </small>
          </p>
        </section>
      </main>

      {/* Footer */}
      <footer className="about-footer">
        <small>
          © 2025 Dr. Artificial · Todos los derechos reservados
        </small>
      </footer>
    </div>
  )
}

