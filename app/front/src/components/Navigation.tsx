/**
 * Navigation Component - Responsive navigation bar with hamburger menu.
 * 
 * This component provides a responsive navigation experience:
 * - Desktop: Full horizontal navigation bar
 * - Mobile/Tablet: Hamburger menu that toggles a slide-out menu
 * 
 * Features:
 * - Accessible (ARIA labels, keyboard navigation, focus management)
 * - Smooth animations
 * - Supports external links and anchor navigation
 * - Auto-closes on navigation
 */

import { useState, useEffect, useRef, type ReactElement } from 'react'
import { NAV_ITEMS } from '../utils/constants'

/**
 * Navigation component with responsive hamburger menu.
 * 
 * @returns React element containing the navigation interface
 */
function Navigation(): ReactElement {
  // State to track whether mobile menu is open
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  
  // Ref to track the navigation element for click-outside detection
  const navRef = useRef<HTMLElement>(null)

  /**
   * Toggles the mobile menu open/closed state.
   */
  const toggleMenu = () => {
    setIsMenuOpen(prev => !prev)
  }

  /**
   * Closes the mobile menu.
   * Used when clicking a nav item or clicking outside.
   */
  const closeMenu = () => {
    setIsMenuOpen(false)
  }

  /**
   * Effect: Close menu when clicking outside the navigation.
   * Improves UX by allowing users to dismiss the menu intuitively.
   */
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (navRef.current && !navRef.current.contains(event.target as Node)) {
        closeMenu()
      }
    }

    if (isMenuOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isMenuOpen])

  /**
   * Effect: Prevent body scroll when mobile menu is open.
   * Improves mobile UX by preventing background scrolling.
   */
  useEffect(() => {
    if (isMenuOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }

    return () => {
      document.body.style.overflow = ''
    }
  }, [isMenuOpen])

  /**
   * Effect: Close menu on Escape key press.
   * Accessibility feature for keyboard navigation.
   */
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isMenuOpen) {
        closeMenu()
      }
    }

    document.addEventListener('keydown', handleEscape)
    return () => {
      document.removeEventListener('keydown', handleEscape)
    }
  }, [isMenuOpen])

  return (
    <nav 
      ref={navRef}
      className="nav-container" 
      aria-label="Secciones principales de Brain"
    >
      {/* 
        Hamburger button - only visible on mobile/tablet
        ACCESIBILIDAD: aria-expanded indica el estado del menú a lectores de pantalla
      */}
      <button
        className="nav-hamburger"
        onClick={toggleMenu}
        aria-expanded={isMenuOpen}
        aria-label={isMenuOpen ? 'Cerrar menú de navegación' : 'Abrir menú de navegación'}
        aria-controls="nav-menu"
      >
        {/* Animated hamburger icon */}
        <span className={`nav-hamburger__line ${isMenuOpen ? 'nav-hamburger__line--open-top' : ''}`} />
        <span className={`nav-hamburger__line ${isMenuOpen ? 'nav-hamburger__line--open-middle' : ''}`} />
        <span className={`nav-hamburger__line ${isMenuOpen ? 'nav-hamburger__line--open-bottom' : ''}`} />
      </button>

      {/* 
        Navigation menu - horizontal on desktop, slide-out on mobile
        ACCESIBILIDAD: id conecta con aria-controls del botón hamburguesa
      */}
      <div 
        id="nav-menu"
        className={`nav ${isMenuOpen ? 'nav--open' : ''}`}
        role="menubar"
      >
        {/* Mobile menu header with logo - only visible in mobile view */}
        <div className="nav__mobile-header">
          <a href="/" className="nav__mobile-brand" onClick={closeMenu}>
            Brain<span className="brand__spark" />
          </a>
        </div>
        
        {NAV_ITEMS.map((item) => (
          <a 
            key={item.id} 
            href={`#${item.id}`} 
            className="nav__link"
            onClick={closeMenu}
            role="menuitem"
          >
            {item.label}
          </a>
        ))}
        <a 
          href="/chat" 
          className="nav__link nav__link--primary" 
          aria-label="Acceder al chat con inteligencia artificial"
          onClick={closeMenu}
          role="menuitem"
        >
          <svg 
            className="nav__link-icon" 
            width="16" 
            height="16" 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor" 
            strokeWidth="2"
            aria-hidden="true"
          >
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
          Chat IA
        </a>
      </div>

      {/* 
        Backdrop overlay - appears behind menu on mobile when open
        ACCESIBILIDAD: Proporciona indicación visual del estado modal
      */}
      {isMenuOpen && (
        <div 
          className="nav-backdrop" 
          onClick={closeMenu}
          aria-hidden="true"
        />
      )}
    </nav>
  )
}

export default Navigation

