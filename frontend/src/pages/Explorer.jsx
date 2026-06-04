import { useEffect, useState } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts'
import { api } from '../api/client.js'
import { PageHeader, Loading, ErrorState } from '../components/States.jsx'
import { formatMetric, humanize } from '../utils/format.js'

const AXIS = { stroke: '#8b949e', fontSize: 12 }
const TOOLTIP_STYLE = {
  background: '#161b22', border: '1px solid #2a313c', borderRadius: 8, color: '#e6edf3',
}

export default function Explorer() {
  const [catalog, setCatalog] = useState(null)
  const [sel, setSel] = useState({ dimension: 'grado', metric: 'default_rate', yearFrom: 2015, yearTo: 2018 })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    Promise.all([api.dimensions(), api.metrics(), api.yearRange()])
      .then(([d, m, y]) => {
        setCatalog({ dimensions: d.dimensions, metrics: m.metrics, years: y })
        setSel((s) => ({ ...s, yearFrom: y.min < 2015 ? 2015 : y.min, yearTo: y.max }))
      })
      .catch(setError)
  }, [])

  useEffect(() => {
    if (!catalog) return
    setLoading(true)
    api.olapQuery(sel)
      .then((r) => { setResult(r); setError(null) })
      .catch(setError)
      .finally(() => setLoading(false))
  }, [catalog, sel])

  if (error && !catalog) return <ErrorState error={error} />
  if (!catalog) return <Loading label="Cargando catálogo OLAP…" />

  const metricMeta = catalog.metrics.find((m) => m.name === sel.metric)
  const years = []
  for (let y = catalog.years.min; y <= catalog.years.max; y++) years.push(y)

  const chartData = (result?.rows || []).map((r) => ({
    label: humanize(r.dimension_value),
    value: r.metric_value,
    count: r.loan_count,
  }))

  const update = (patch) => setSel((s) => ({ ...s, ...patch }))

  return (
    <>
      <PageHeader
        title="Explorador OLAP"
        subtitle="Agrega el warehouse por cualquier dimensión y métrica, con filtro temporal."
      />

      <div className="card mb-16">
        <div className="controls">
          <div className="field">
            <label>Dimensión</label>
            <select value={sel.dimension} onChange={(e) => update({ dimension: e.target.value })}>
              {catalog.dimensions.map((d) => (
                <option key={d.name} value={d.name}>{d.title}</option>
              ))}
            </select>
          </div>
          <div className="field">
            <label>Métrica</label>
            <select value={sel.metric} onChange={(e) => update({ metric: e.target.value })}>
              {catalog.metrics.map((m) => (
                <option key={m.name} value={m.name}>{m.title}</option>
              ))}
            </select>
          </div>
          <div className="field">
            <label>Año desde</label>
            <select value={sel.yearFrom} onChange={(e) => update({ yearFrom: +e.target.value })}>
              {years.map((y) => <option key={y} value={y}>{y}</option>)}
            </select>
          </div>
          <div className="field">
            <label>Año hasta</label>
            <select value={sel.yearTo} onChange={(e) => update({ yearTo: +e.target.value })}>
              {years.map((y) => <option key={y} value={y}>{y}</option>)}
            </select>
          </div>
        </div>
      </div>

      {error && <ErrorState error={error} />}
      {loading && <Loading label="Consultando…" />}

      {!loading && result && (
        <div className="grid grid-2">
          <div className="card">
            <h3 className="card-title">{metricMeta?.title} por {catalog.dimensions.find((d) => d.name === sel.dimension)?.title}</h3>
            <ResponsiveContainer width="100%" height={Math.max(280, chartData.length * 26)}>
              <BarChart data={chartData} layout="vertical" margin={{ left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2a313c" horizontal={false} />
                <XAxis type="number" {...AXIS}
                  tickFormatter={(v) => formatMetric(v, metricMeta?.format)} />
                <YAxis type="category" dataKey="label" {...AXIS} width={130} />
                <Tooltip contentStyle={TOOLTIP_STYLE}
                  formatter={(v) => formatMetric(v, metricMeta?.format)} />
                <Bar dataKey="value" name={metricMeta?.title} fill="#2f81f7" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="card">
            <h3 className="card-title">Detalle</h3>
            <div style={{ maxHeight: 380, overflowY: 'auto' }}>
              <table>
                <thead>
                  <tr>
                    <th>{catalog.dimensions.find((d) => d.name === sel.dimension)?.title}</th>
                    <th className="num">{metricMeta?.title}</th>
                    <th className="num">N.º préstamos</th>
                  </tr>
                </thead>
                <tbody>
                  {result.rows.map((r) => (
                    <tr key={r.dimension_value}>
                      <td>{humanize(r.dimension_value)}</td>
                      <td className="num">{formatMetric(r.metric_value, metricMeta?.format)}</td>
                      <td className="num">{r.loan_count.toLocaleString('en-US')}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
