import { NavLink } from 'react-router-dom'

const LINKS = [
  { to: '/', label: 'Dashboard', icon: '▣', end: true },
  { to: '/explore', label: 'Explorador OLAP', icon: '⊞' },
  { to: '/predict', label: 'Predictor', icon: '◎' },
  { to: '/models', label: 'Modelos', icon: '◈' },
]

export default function Layout({ children }) {
  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-logo">L</div>
          <div>
            <div className="brand-name">LoanSight</div>
            <div className="brand-sub">Riesgo crediticio</div>
          </div>
        </div>
        <nav className="nav">
          {LINKS.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              end={l.end}
              className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}
            >
              <span className="nav-icon">{l.icon}</span>
              {l.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="main">{children}</main>
    </div>
  )
}
