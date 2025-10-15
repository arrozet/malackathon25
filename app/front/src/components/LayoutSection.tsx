/**
 * Componentes de sección para estructurar el scroll modular de la SPA.
 * @param id - Identificador único que habilita el scroll anclado.
 * @param title - Título principal de la sección.
 * @param description - Texto descriptivo que contextualiza la sección.
 * @param children - Contenido específico de la sección.
 * @returns Estructura semántica para una sección de la SPA.
 */
export default function LayoutSection({
  id,
  title,
  description,
  children,
}: {
  id: string
  title: string
  description: string
  children: React.ReactNode
}) {
  // Presentamos cada bloque como una sección con identificadores para navegación.
  return (
    <section id={id} className="section" aria-labelledby={`${id}-title`}>
      <div className="section__inner">
        <header className="section__header">
          <h2 id={`${id}-title`}>{title}</h2>
          <p>{description}</p>
        </header>
        <div className="section__content">{children}</div>
      </div>
    </section>
  )
}
