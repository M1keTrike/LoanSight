import { useEffect, useState } from 'react'
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer,
} from 'recharts'
import { api } from '../api/client.js'
import { PageHeader, KpiCard, Loading, ErrorState } from '../components/States.jsx'
import { formatCurrency, formatInt, formatPercent } from '../utils/format.js'

const AXIS = { stroke: '#8b949e', fontSize: 12 }
const TOOLTIP_STYLE = {
  background: '#161b22', border: '1px solid #2a313c',
  borderRadius: 8, color: '#e6edf3',
}

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    Promise.all([
      api.kpis(),
      api.olapQuery({ dimension: 'grado', metric: 'loan_count' }),
      api.olapQuery({ dimension: 'tiempo', metric: 'default_rate' }),
    ])
      .then(([kpis, byGrade, byYear]) => {
        setData({
          kpis,
          byGrade: byGrade.rows.map((r) => ({
            grade: r.dimension_value,
            loans: r.metric_value,
          })),
          byYear: byYear.rows.map((r) => ({
            year: r.dimension_value,
            rate: +(r.metric_value * 100).toFixed(2),
          })),
        })
      })
      .catch(setError)
  }, [])

  if (error) return <ErrorState error={error} />
  if (!data) return <Loading label="Cargando indicadores…" />

  const k = data.kpis
  return (
    <>
      <PageHeader
        title="Dashboard"
        subtitle="Panorama global de la cartera de préstamos Lending Club (2007–2018)."
      />

      <div className="grid grid-kpi mb-16">
        <KpiCard label="Préstamos" value={formatInt(k.total_loans)}
          hint="Total en el warehouse" />
        <KpiCard label="Monto financiado" value={formatCurrency(k.total_funded)}
          tone="accent" hint="Suma de funded_amnt" />
        <KpiCard label="Tasa de interés media" value={`${k.avg_int_rate.toFixed(2)}%`}
          hint="Promedio int_rate" />
        <KpiCard label="Tasa de default" value={formatPercent(k.default_rate)}
          tone="bad" hint={`${formatInt(k.completed_loans)} préstamos terminados`} />
      </div>

      <div className="grid grid-2">
        <div className="card">
          <h3 className="card-title">Distribución de préstamos por grado</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={data.byGrade}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a313c" vertical={false} />
              <XAxis dataKey="grade" {...AXIS} />
              <YAxis {...AXIS} tickFormatter={formatInt} width={60} />
              <Tooltip contentStyle={TOOLTIP_STYLE} formatter={(v) => formatInt(v)} />
              <Bar dataKey="loans" name="Préstamos" fill="#2f81f7" radius={[5, 5, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h3 className="card-title">Tasa de default por año de emisión</h3>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={data.byYear}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a313c" vertical={false} />
              <XAxis dataKey="year" {...AXIS} />
              <YAxis {...AXIS} unit="%" width={50} />
              <Tooltip contentStyle={TOOLTIP_STYLE} formatter={(v) => `${v}%`} />
              <Line type="monotone" dataKey="rate" name="Tasa default"
                stroke="#f85149" strokeWidth={2.5} dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
      <p className="muted mt-20">
        Nota: la tasa de default se calcula solo sobre préstamos terminados
        (Fully Paid / Charged Off); los préstamos vigentes recientes la
        reducen artificialmente en 2017–2018.
      </p>
    </>
  )
}
