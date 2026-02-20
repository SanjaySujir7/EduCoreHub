import React, { createContext, useState, useEffect, useCallback } from 'react';

const themes = {
  dark: {
    '--bg-primary': '#060b18',
    '--bg-secondary': '#0d1530',
    '--bg-tertiary': '#131b3a',
    '--card-bg': 'rgba(13, 21, 48, 0.85)',
    '--card-border': 'rgba(0, 212, 255, 0.12)',
    '--text-primary': '#e2e8f0',
    '--text-secondary': '#94a3b8',
    '--accent-primary': '#00d4ff',
    '--accent-secondary': '#7c3aed',
    '--accent-glow': '0 0 30px rgba(0, 212, 255, 0.35)',
    '--btn-glow': '0 0 25px rgba(0, 212, 255, 0.5)',
    '--input-bg': 'rgba(13, 21, 48, 0.6)',
    '--border-color': 'rgba(0, 212, 255, 0.18)',
    '--error': '#ef4444',
    '--success': '#22c55e',
    '--overlay': 'rgba(6, 11, 24, 0.6)',
    '--shadow': '0 8px 32px rgba(0, 0, 0, 0.4)',
  },
  light: {
    '--bg-primary': '#eef2f7',
    '--bg-secondary': '#ffffff',
    '--bg-tertiary': '#e2e8f0',
    '--card-bg': 'rgba(255, 255, 255, 0.88)',
    '--card-border': 'rgba(59, 130, 246, 0.12)',
    '--text-primary': '#0f172a',
    '--text-secondary': '#475569',
    '--accent-primary': '#3b82f6',
    '--accent-secondary': '#8b5cf6',
    '--accent-glow': '0 0 25px rgba(59, 130, 246, 0.2)',
    '--btn-glow': '0 0 20px rgba(59, 130, 246, 0.35)',
    '--input-bg': 'rgba(241, 245, 249, 0.85)',
    '--border-color': 'rgba(59, 130, 246, 0.18)',
    '--error': '#dc2626',
    '--success': '#16a34a',
    '--overlay': 'rgba(241, 245, 249, 0.6)',
    '--shadow': '0 8px 32px rgba(0, 0, 0, 0.08)',
  },
};

export const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState(() => localStorage.getItem('app-theme') || 'dark');

  const applyTheme = useCallback((t) => {
    const vars = themes[t];
    const root = document.documentElement;
    Object.entries(vars).forEach(([k, v]) => root.style.setProperty(k, v));
    root.setAttribute('data-theme', t);
  }, []);

  useEffect(() => {
    // Inject base reset + font
    if (!document.getElementById('base-reset')) {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = 'https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap';
      document.head.appendChild(link);

      const style = document.createElement('style');
      style.id = 'base-reset';
      style.textContent = `
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        html { scroll-behavior: smooth; }
        body {
          font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif;
          min-height: 100vh;
          transition: background-color 0.5s ease, color 0.5s ease;
          background-color: var(--bg-primary);
          color: var(--text-primary);
          overflow-x: hidden;
        }
        a { text-decoration: none; color: inherit; }
        input, button, select, textarea { font-family: inherit; }
        #root { min-height: 100vh; }
      `;
      document.head.appendChild(style);
    }
    applyTheme(theme);
    localStorage.setItem('app-theme', theme);
  }, [theme, applyTheme]);

  const toggleTheme = () => setTheme(p => (p === 'dark' ? 'light' : 'dark'));

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};
