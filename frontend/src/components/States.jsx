export function Loading({ label = 'Cargando…' }) {
  return (
    <div className="state">
      <div className="spinner" />
      {label}
    </div>
  )
}

export function ErrorState({ error }) {
  return (
    <div className="state state-error">
      <div style={{ fontSize: 22, marginBottom: 8 }}>⚠</div>
      {String(error?.message || error)}
      <div className="muted mt-20">
        ¿Levantaste el backend y construiste el warehouse + modelos?
      </div>
    </div>
  )
}

export function PageHeader({ title, subtitle }) {
  return (
    <div className="page-header">
      <h1 className="page-title">{title}</h1>
      {subtitle && <p className="page-subtitle">{subtitle}</p>}
    </div>
  )
}

export function KpiCard({ label, value, hint, tone }) {
  const toneClass = tone ? ` kpi-${tone}` : ''
  return (
    <div className="card kpi">
      <span className="kpi-label">{label}</span>
      <span className={'kpi-value' + toneClass}>{value}</span>
      {hint && <span className="kpi-hint">{hint}</span>}
    </div>
  )
}
