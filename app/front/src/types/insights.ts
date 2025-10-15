/**
 * Representa un indicador individual dentro de una sección de insights.
 * @property title - Título corto y descriptivo del indicador.
 * @property value - Valor principal que se mostrará al usuario.
 * @property description - Explicación contextual del indicador para los investigadores.
 */
export type InsightMetric = {
  title: string
  value: string
  description: string
}

/**
 * Agrupa múltiples indicadores bajo una misma dimensión analítica.
 * @property title - Nombre de la sección o dimensión analizada.
 * @property metrics - Colección de indicadores relacionados.
 */
export type InsightSection = {
  title: string
  metrics: InsightMetric[]
}

/**
 * Resumen completo de los insights devueltos por el backend.
 * @property generated_at - Marca temporal de generación de los datos.
 * @property sample_period - Periodo de muestreo de los datos analizados.
 * @property highlight_phrases - Frases clave para mostrar como destacados.
 * @property metric_sections - Secciones con los indicadores estructurados.
 * @property database_connected - Indicador de conexión con Oracle Autonomous Database.
 */
export type InsightSummary = {
  generated_at: string
  sample_period: string
  highlight_phrases: string[]
  metric_sections: InsightSection[]
  database_connected: boolean
}
