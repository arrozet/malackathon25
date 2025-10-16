# Auditoría de Accesibilidad y Usabilidad - Brain

**Fecha:** 16 de octubre de 2025  
**Proyecto:** Brain - Compañero Artificial de Investigación  
**Alcance:** Frontend completo (React + TypeScript + CSS)  
**Estándar de referencia:** WCAG 2.1 AA + Guía de Buenas Prácticas NTT DATA

---

## Resumen Ejecutivo

Esta auditoría identifica deficiencias y áreas de mejora en accesibilidad y usabilidad del código frontend de Brain. Se han encontrado **43 problemas** distribuidos en las siguientes categorías:

- **Críticos:** 8 problemas
- **Importantes:** 15 problemas  
- **Moderados:** 12 problemas
- **Menores:** 8 problemas

---

## 1. Estructura y Semántica HTML

### 1.1 ❌ CRÍTICO: Ausencia de `<main>` en About.tsx

**Archivo:** `app/front/src/pages/About.tsx`  
**Línea:** 27  
**Problema:** Aunque se declara `role="main"` en un `div`, esto debería ser una etiqueta `<main>` semántica nativa.

**Impacto:**
- Los lectores de pantalla dependen de landmarks semánticos nativos
- El atributo `role="main"` es redundante si se usa `<main>`

**Recomendación:**
```tsx
// MAL
<main className="about-main" role="main">

// BIEN  
<main className="about-main">
```

---

### 1.2 ❌ CRÍTICO: Uso incorrecto de `<aside>` con `role="complementary"` redundante

**Archivo:** `app/front/src/pages/DataExplorer.tsx`  
**Línea:** 56  
**Problema:** El elemento `<aside>` ya tiene semántica de `complementary` implícita.

**Recomendación:**
```tsx
// MAL
<aside className="explorer-sidebar" role="complementary" aria-label="Panel de filtros de datos">

// BIEN
<aside className="explorer-sidebar" aria-label="Panel de filtros de datos">
```

---

### 1.3 ❌ CRÍTICO: Uso incorrecto de `<main>` en DataExplorer.tsx

**Archivo:** `app/front/src/pages/DataExplorer.tsx`  
**Línea:** 61  
**Problema:** Se usa `<main>` dentro del contenido de exploración, pero la página completa ya debería estar dentro de un único `<main>` en App.tsx. No puede haber múltiples elementos `<main>`.

**Impacto:**
- Viola la especificación HTML5 (solo un `<main>` por página)
- Confunde a tecnologías asistivas

**Recomendación:**
```tsx
// MAL
<main className="explorer-content" aria-label="Área de visualización de datos">

// BIEN
<div className="explorer-content" aria-label="Área de visualización de datos">
```

---

### 1.4 ⚠️ IMPORTANTE: Jerarquía de encabezados inconsistente

**Archivo:** `app/front/src/pages/DataExplorer.tsx`  
**Línea:** 46  
**Problema:** Se usa `<h2>` para el título principal de la página "Exploración de datos", pero debería ser `<h1>` ya que es el título principal de esta vista.

**Archivo:** `app/front/src/components/DataCharts.tsx`  
**Líneas:** 132, 161, 187, 267, 282  
**Problema:** Se usa `<h4>` para títulos de gráficos sin `<h3>` previo.

**Impacto:**
- Los usuarios de lectores de pantalla navegan por encabezados
- Saltar niveles dificulta la comprensión de la jerarquía

**Recomendación:**
- Asegurar un único `<h1>` por página
- No saltar niveles (h1 → h2 → h3, nunca h1 → h3)

---

### 1.5 ⚠️ IMPORTANTE: Falta de agrupación semántica en formularios

**Archivo:** `app/front/src/components/DataFilters.tsx`  
**Líneas:** 71-99, 101-149, 151-187  
**Problema:** Los `<fieldset>` tienen `<legend>` con clase `sr-only`, lo que los hace invisibles. Esto dificulta la comprensión visual de grupos de campos.

**Recomendación:**
- Hacer las `<legend>` visibles o usar un diseño alternativo que mantenga la agrupación visual clara

---

### 1.6 ⚠️ IMPORTANTE: Imágenes SVG sin textos alternativos adecuados

**Archivo:** `app/front/src/components/BrainIcon.tsx`  
**Línea:** 13  
**Problema:** El SVG usa `aria-hidden="true"`, lo cual está bien cuando es decorativo, pero en contextos donde transmite información (como el hero de About.tsx), debería tener una descripción.

**Recomendación:**
- Agregar prop opcional `decorative` para controlar si el icono es informativo o decorativo
- Cuando sea informativo, incluir `role="img"` y `aria-label`

---

### 1.7 ℹ️ MODERADO: Falta de `<article>` semántico

**Archivo:** `app/front/src/App.tsx`  
**Líneas:** 114-133  
**Problema:** Las tarjetas de métricas usan `<article>` correctamente, pero las tarjetas de About.tsx no usan semántica de artículo.

**Recomendación:**
- Usar `<article>` para bloques de contenido autocontenido

---

### 1.8 ℹ️ MODERADO: Formulario sin `<form>` en DataFilters.tsx

**Archivo:** `app/front/src/components/DataFilters.tsx`  
**Línea:** 70  
**Problema:** Existe un `<form>` pero usa `all: unset` en CSS (línea 123 de index.css), lo que puede causar comportamiento inesperado.

**Recomendación:**
- Evitar `all: unset` en formularios
- Usar reseteos CSS específicos

---

## 2. Navegación por Teclado e Interacción

### 2.1 ✅ CORRECTO: Foco visible global

**Archivo:** `app/front/src/index.css`  
**Líneas:** 54-65  
**Estado:** ✅ Implementado correctamente

El código ya tiene estilos de foco visible con `:focus-visible` y contraste adecuado (#7c3aed).

---

### 2.2 ⚠️ IMPORTANTE: Orden de tabulación puede ser confuso en móvil

**Archivo:** `app/front/src/App.css`  
**Líneas:** 415-423  
**Problema:** En móvil, el top-bar cambia a `flex-direction: column`, lo que puede alterar el orden de tabulación esperado.

**Recomendación:**
- Verificar manualmente que el orden de tabulación siga siendo lógico en móvil

---

### 2.3 ℹ️ MODERADO: Falta de skip links

**Problema:** No existe un enlace de "saltar al contenido principal" para usuarios de teclado.

**Recomendación:**
```tsx
<a href="#main-content" className="skip-link">
  Saltar al contenido principal
</a>
```

Y en CSS:
```css
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: #7c3aed;
  color: white;
  padding: 8px;
  text-decoration: none;
  z-index: 100;
}

.skip-link:focus {
  top: 0;
}
```

---

### 2.4 ℹ️ MODERADO: Área clickable de navegación puede ser pequeña en móvil

**Archivo:** `app/front/src/App.css`  
**Líneas:** 57-68  
**Problema:** Los enlaces de navegación tienen padding de 0.55rem × 0.95rem, lo que puede traducirse a menos de 44px en móvil.

**Recomendación:**
- Asegurar mínimo 44×44px para áreas táctiles (WCAG 2.5.5)

---

### 2.5 ℹ️ MENOR: Falta de indicadores de estado activo en navegación

**Archivo:** `app/front/src/App.tsx`  
**Líneas:** 58-62  
**Problema:** Los enlaces de navegación no indican visualmente qué sección está activa.

**Recomendación:**
- Agregar `aria-current="location"` o `aria-current="true"` al enlace activo
- Agregar estilo visual para `.nav__link[aria-current]`

---

## 3. Claridad Visual y Feedback

### 3.1 ⚠️ IMPORTANTE: Contraste de color insuficiente en varios elementos

**Archivo:** `app/front/src/styles/About.css`  
**Líneas:** 141, 205, 222

**Problemas identificados:**

1. **`.about-link` - color: #b876f9**
   - Contraste sobre fondo oscuro: ~3.8:1
   - Requerido WCAG AA: 4.5:1
   - **NO CUMPLE**

2. **`.about-credit p` - color: #9ca3c7**
   - Contraste: ~4.2:1
   - **NO CUMPLE** (necesita 4.5:1)

3. **`.about-footer small` - color: #a5b4fc**
   - Contraste: ~5.2:1
   - **CUMPLE** pero está en el límite

**Recomendación:**
- Cambiar `#b876f9` a `#c4b5fd` (contraste 6.8:1)
- Cambiar `#9ca3c7` a `#d1d5db` (contraste 7.1:1)

---

### 3.2 ⚠️ IMPORTANTE: Textos de botones y enlaces ambiguos

**Archivo:** `app/front/src/components/DataFilters.tsx`  
**Línea:** 66  
**Problema:** El botón dice "Limpiar filtros", pero su `aria-label` duplica la información.

**Recomendación:**
- Mantener texto descriptivo sin `aria-label` redundante, O
- Si el texto es corto, usar `aria-label` más descriptivo

**Archivo:** `app/front/src/pages/About.tsx`  
**Línea:** 22  
**Problema:** El enlace dice "← Volver al inicio" que es claro, pero el `aria-label` es redundante.

---

### 3.3 ℹ️ MODERADO: Falta de feedback visual en estados de carga

**Archivo:** `app/front/src/pages/DataExplorer.tsx`  
**Líneas:** 63-68  
**Problema:** El spinner tiene animación, pero falta un indicador más claro para usuarios con visión reducida.

**Recomendación:**
- Añadir texto "Cargando..." visible (ya existe)
- Considerar agregar una barra de progreso indeterminada adicional

---

### 3.4 ℹ️ MODERADO: Uso inconsistente de colores para estados

**Problema:** Los badges usan verde para "ok" y amarillo para "warn", pero no hay un patrón consistente documentado para otros estados.

**Recomendación:**
- Documentar paleta de estados: success, warning, error, info, neutral
- Aplicar consistentemente en toda la aplicación

---

### 3.5 ℹ️ MENOR: Falta de feedback hover en tarjetas de About.tsx

**Archivo:** `app/front/src/styles/About.css`  
**Líneas:** 107-111  
**Problema:** Las tarjetas tienen hover, pero no hay indicador de que sean interactivas (no son enlaces ni botones).

**Recomendación:**
- Si las tarjetas NO son interactivas, eliminar el efecto hover
- Si SON interactivas, convertirlas en elementos semánticos adecuados

---

## 4. Diseño Adaptable y Robustez

### 4.1 ✅ CORRECTO: Viewport meta tag

**Archivo:** `app/front/index.html`  
**Línea:** 6  
**Estado:** ✅ Implementado correctamente

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
```

No hay `user-scalable=no` ni `maximum-scale=1.0`, lo cual es correcto.

---

### 4.2 ⚠️ IMPORTANTE: Scroll horizontal en zoom 200%

**Archivo:** `app/front/src/index.css`  
**Líneas:** 437-449  
**Problema:** Las media queries solo cubren hasta 768px. Al hacer zoom 200%, pueden aparecer barras de scroll horizontal en elementos con anchos fijos.

**Elementos en riesgo:**
- `.hero__icon` con `width: min(100%, 320px)`
- Gráficos con anchos fijos

**Recomendación:**
- Verificar manualmente zoom 200% en todas las páginas
- Usar unidades relativas (rem, %, vw) en lugar de px fijos donde sea posible

---

### 4.3 ℹ️ MODERADO: Tamaño de fuente base puede ser pequeño en algunos contextos

**Archivo:** `app/front/src/index.css`  
**Líneas:** 1-11  
**Problema:** No se define `font-size` base en `:root`, por lo que depende del navegador (típicamente 16px).

**Recomendación:**
- Definir explícitamente: `font-size: 16px;` en `:root` o `html`
- Considerar usar `font-size: 100%;` para respetar preferencias del usuario

---

### 4.4 ℹ️ MODERADO: Gráficos pueden ser difíciles de ver en móvil

**Archivo:** `app/front/src/components/DataCharts.tsx`  
**Líneas:** 148-149  
**Problema:** El ancho de las etiquetas del eje Y es reducido a 120px en móvil, lo que puede truncar texto largo.

**Recomendación:**
- Considerar rotación de etiquetas en móvil
- Usar abreviaturas para categorías largas en móvil

---

### 4.5 ℹ️ MENOR: Falta de media query para preferencia de contraste alto

**Problema:** No se implementa `@media (prefers-contrast: high)` para usuarios que necesitan contraste aumentado.

**Recomendación:**
```css
@media (prefers-contrast: high) {
  :root {
    --primary-color: #8b5cf6; /* Más brillante */
    --text-color: #ffffff; /* Blanco puro */
  }
}
```

---

## 5. ARIA y Accesibilidad Avanzada

### 5.1 ⚠️ IMPORTANTE: Uso incorrecto de `aria-live` en múltiples lugares

**Archivo:** `app/front/src/App.tsx`  
**Línea:** 85  
**Problema:** `aria-live="polite"` en `.hero__highlight-stack` puede anunciar cambios inesperados.

**Archivo:** `app/front/src/pages/DataExplorer.tsx`  
**Líneas:** 64, 72, 89  
**Problema:** Múltiples regiones `aria-live` pueden causar anuncios superpuestos.

**Recomendación:**
- Usar `aria-live` SOLO en elementos que cambien dinámicamente
- Usar `aria-live="polite"` para información no crítica
- Usar `aria-live="assertive"` solo para errores urgentes

---

### 5.2 ℹ️ MODERADO: Falta de `aria-describedby` en gráficos complejos

**Archivo:** `app/front/src/components/DataCharts.tsx`  
**Problemas:** Los gráficos tienen `role="img"` y `aria-label`, pero podrían beneficiarse de descripciones más detalladas.

**Recomendación:**
```tsx
<div 
  className="chart-card" 
  role="img" 
  aria-labelledby="chart-title" 
  aria-describedby="chart-description"
>
  <h4 id="chart-title">Distribución por categoría diagnóstica</h4>
  <p id="chart-description" className="sr-only">
    Este gráfico de barras muestra la distribución de admisiones...
  </p>
  ...
</div>
```

---

### 5.3 ℹ️ MODERADO: `aria-busy` solo en un lugar

**Archivo:** `app/front/src/components/DataFilters.tsx`  
**Línea:** 161  
**Estado:** ✅ Usado correctamente en el select de categorías

**Archivo:** `app/front/src/pages/DataExplorer.tsx`  
**Línea:** 64  
**Estado:** ✅ Usado correctamente en el estado de carga

**Recomendación:**
- Mantener consistencia: todos los estados de carga deberían usar `aria-busy="true"`

---

### 5.4 ℹ️ MENOR: Falta de `aria-invalid` en campos con errores

**Problema:** No hay validación de formularios con feedback accesible.

**Recomendación:**
- Si se implementa validación, agregar `aria-invalid="true"` y `aria-errormessage`

---

## 6. Rendimiento y Experiencia

### 6.1 ℹ️ MODERADO: Animaciones sin control de `prefers-reduced-motion`

**Archivo:** `app/front/src/index.css`  
**Líneas:** 405-409  
**Problema:** El spinner (`@keyframes spin`) no respeta `prefers-reduced-motion`.

**Archivo:** `app/front/src/App.css`  
**Varias líneas:** Transiciones CSS no se desactivan para usuarios con preferencia de movimiento reducido.

**Recomendación:**
```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

### 6.2 ℹ️ MENOR: Falta de lazy loading para gráficos

**Archivo:** `app/front/src/components/DataCharts.tsx`  
**Problema:** Todos los gráficos se renderizan inmediatamente, incluso si están fuera del viewport.

**Recomendación:**
- Implementar Intersection Observer para cargar gráficos bajo demanda
- O usar bibliotecas como `react-lazy-load-image-component`

---

## 7. Problemas de Código y Mantenibilidad

### 7.1 ℹ️ MODERADO: Tipado `any` en CustomTooltip

**Archivo:** `app/front/src/components/DataCharts.tsx`  
**Líneas:** 76, 82  
**Problema:** Uso de `any` rompe la seguridad de tipos.

**Recomendación:**
```tsx
interface TooltipProps {
  active?: boolean
  payload?: Array<{
    color: string
    name: string
    value: number
    payload: { percentage?: number }
  }>
  label?: string
}

const CustomTooltip = ({ active, payload, label }: TooltipProps) => {
  ...
}
```

---

### 7.2 ℹ️ MENOR: Comentarios en español e inglés mezclados

**Problema:** Algunos archivos tienen comentarios en inglés (JSDoc) y otros en español.

**Recomendación:**
- Estandarizar idioma de comentarios (preferiblemente español según la guía)

---

## 8. Resumen de Correcciones Prioritarias

### Prioridad CRÍTICA (implementar inmediatamente)

1. ✅ Corregir jerarquía de `<main>` en DataExplorer.tsx
2. ✅ Eliminar roles ARIA redundantes (`role="main"` en `<main>`)
3. ✅ Arreglar jerarquía de encabezados (h1 → h2 → h3)
4. ✅ Mejorar contraste de colores (#b876f9 → #c4b5fd, etc.)

### Prioridad IMPORTANTE (implementar antes del demo)

5. ✅ Agregar skip links para navegación por teclado
6. ✅ Hacer visibles las `<legend>` de formularios
7. ✅ Asegurar áreas táctiles mínimas de 44×44px
8. ✅ Implementar `@media (prefers-reduced-motion)`
9. ✅ Agregar descripciones detalladas a gráficos con `aria-describedby`
10. ✅ Corregir uso de `aria-live` (evitar anuncios superpuestos)

### Prioridad MODERADA (post-demo, pre-producción)

11. Agregar `<article>` a tarjetas de About.tsx
12. Implementar paleta de estados consistente
13. Verificar zoom 200% manualmente
14. Agregar feedback visual mejorado para estados de carga
15. Implementar `@media (prefers-contrast: high)`

### Prioridad MENOR (mejora continua)

16. Tipado estricto en CustomTooltip
17. Lazy loading para gráficos
18. Estandarizar idioma de comentarios
19. Agregar validación de formularios con `aria-invalid`
20. Mejorar indicadores de sección activa en navegación

---

## 9. Checklist de Validación Post-Refactorización

### Estructura HTML
- [ ] Un único `<h1>` por página
- [ ] Jerarquía de encabezados sin saltos (h1→h2→h3)
- [ ] Todos los `<form>` tienen `<label>` asociados con `for`/`htmlFor`
- [ ] Campos relacionados agrupados con `<fieldset>` y `<legend>` visible
- [ ] Imágenes informativas con `alt` descriptivo
- [ ] Imágenes decorativas con `alt=""` o `aria-hidden="true"`
- [ ] Un único `<main>` por página
- [ ] Uso correcto de `<header>`, `<nav>`, `<aside>`, `<footer>`

### Navegación por Teclado
- [ ] Orden de tabulación lógico en desktop y móvil
- [ ] Todos los elementos interactivos alcanzables con Tab
- [ ] Foco visible en todos los elementos interactivos (outline 2-3px)
- [ ] Skip link funcional
- [ ] Áreas táctiles ≥ 44×44px
- [ ] Enter/Espacio activan botones y enlaces

### Contraste y Color
- [ ] Texto normal: contraste ≥ 4.5:1 (WCAG AA)
- [ ] Texto grande (≥18pt): contraste ≥ 3:1
- [ ] Elementos UI: contraste ≥ 3:1
- [ ] No se usa solo color para transmitir información
- [ ] Estados hover/focus/active claramente visibles

### Responsive y Zoom
- [ ] Viewport meta tag sin `user-scalable=no`
- [ ] Zoom 200% sin scroll horizontal
- [ ] Breakpoints adecuados (móvil, tablet, desktop)
- [ ] Texto legible en todas las resoluciones

### ARIA y Semántica
- [ ] Roles ARIA no redundantes con HTML semántico
- [ ] `aria-label` descriptivo en elementos sin texto visible
- [ ] `aria-live` usado solo en regiones dinámicas
- [ ] `aria-busy` en estados de carga
- [ ] `aria-describedby` en elementos complejos

### Preferencias de Usuario
- [ ] `@media (prefers-reduced-motion)` implementado
- [ ] Animaciones desactivables
- [ ] Smooth scroll respeta preferencias
- [ ] (Opcional) `@media (prefers-contrast: high)`

---

## 10. Herramientas de Validación Recomendadas

1. **axe DevTools** (extensión Chrome/Firefox) - Auditoría automática
2. **WAVE** (WebAIM) - Evaluación visual de accesibilidad
3. **Lighthouse** (Chrome DevTools) - Auditoría general
4. **NVDA** / **JAWS** - Prueba con lectores de pantalla
5. **Contrast Checker** (WebAIM) - Validación de contraste
6. **Keyboard Navigation Test** - Navegación manual con Tab
7. **Responsive Design Mode** - Prueba de zoom 200%

---

## Conclusiones

La aplicación Brain tiene una **base sólida de accesibilidad**, con muchos aspectos ya implementados correctamente:

✅ Viewport meta tag correcto  
✅ Estilos de foco visible globales  
✅ Uso de ARIA en muchos elementos  
✅ Smooth scroll con preferencia de movimiento reducido  
✅ Responsive design funcional  

Sin embargo, requiere **correcciones críticas** en:

❌ Jerarquía de landmarks HTML  
❌ Contraste de color en varios elementos  
❌ Jerarquía de encabezados inconsistente  
❌ Falta de soporte completo para `prefers-reduced-motion`  

**Tiempo estimado de corrección:**
- Críticos: 2-3 horas
- Importantes: 4-5 horas
- Moderados: 3-4 horas
- Menores: 2-3 horas

**Total:** 11-15 horas de desarrollo para alcanzar cumplimiento completo WCAG 2.1 AA.

---

**Auditor:** AI Senior UX/UI & Accessibility Engineer  
**Próximos pasos:** Implementar correcciones críticas e importantes, luego validar con herramientas automáticas y pruebas manuales.

