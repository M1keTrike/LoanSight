import { useEffect, useState } from 'react'
import { api } from '../api/client.js'
import { PageHeader, Loading, ErrorState } from '../components/States.jsx'
import { formatPercent, humanize } from '../utils/format.js'

const DEFAULT_FORM = {
  loan_amnt: 15000,
  term: 36,
  annual_inc: 65000,
  dti: 18.4,
  emp_length: 5,
  purpose: 'debt_consolidation',
}

const NUMERIC_FIELDS = [
  { key: 'loan_amnt', label: 'Monto del préstamo (USD)', step: 500, min: 500 },
  { key: 'annual_inc', label: 'Ingreso anual (USD)', step: 1000, min: 0 },
  { key: 'dti', label: 'DTI (debt-to-income)', step: 0.1, min: 0 },
]

export default function Predictor() {
  const [tab, setTab] = useState('classification')
  const [meta, setMeta] = useState(null)
  const [form, setForm] = useState(DEFAULT_FORM)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [metaError, setMetaError] = useState(null)

  useEffect(() => {
    api.modelMetadata().then(setMeta).catch(setMetaError)
  }, [])

  useEffect(() => { setResult(null); setError(null) }, [tab])

  if (metaError) return <ErrorState error={metaError} />
  if (!meta) return <Loading label="Cargando formulario…" />

  const set = (key, value) => setForm((f) => ({ ...f, [key]: value }))

  const submit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    const payload = {
      loan_amnt: Number(form.loan_amnt),
      term: Number(form.term),
      annual_inc: Number(form.annual_inc),
      dti: Number(form.dti),
      emp_length: Number(form.emp_length),
      purpose: form.purpose,
    }
    try {
      const fn = tab === 'classification' ? api.predictClassification : api.predictRegression
      setResult(await fn(payload))
    } catch (err) {
      setError(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <PageHeader
        title="Predictor"
        subtitle="Inferencia en vivo con los modelos entrenados. La API aplica el mismo pipeline de preprocesamiento."
      />

      <div className="tabs">
        <div className={'tab' + (tab === 'classification' ? ' active' : '')}
          onClick={() => setTab('classification')}>
          Clasificación · Default
        </div>
        <div className={'tab' + (tab === 'regression' ? ' active' : '')}
          onClick={() => setTab('regression')}>
          Regresión · Tasa de interés
        </div>
      </div>

      <div className="grid grid-2">
        <div className="card">
          <h3 className="card-title">Características del préstamo</h3>
          <form onSubmit={submit}>
            <div className="grid" style={{ gridTemplateColumns: '1fr 1fr', gap: 14 }}>
              {NUMERIC_FIELDS.map((f) => (
                <div className="field" key={f.key}>
                  <label>{f.label}</label>
                  <input type="number" step={f.step} min={f.min}
                    value={form[f.key]}
                    onChange={(e) => set(f.key, e.target.value)} required />
                </div>
              ))}
              <div className="field">
                <label>Plazo</label>
                <select value={form.term} onChange={(e) => set('term', e.target.value)}>
                  <option value={36}>36 meses</option>
                  <option value={60}>60 meses</option>
                </select>
              </div>
              <div className="field">
                <label>Antigüedad laboral (años)</label>
                <select value={form.emp_length} onChange={(e) => set('emp_length', e.target.value)}>
                  {Array.from({ length: 11 }, (_, i) => (
                    <option key={i} value={i}>{i === 10 ? '10+' : i} {i === 1 ? 'año' : 'años'}</option>
                  ))}
                </select>
              </div>
              <div className="field">
                <label>Propósito</label>
                <select value={form.purpose} onChange={(e) => set('purpose', e.target.value)}>
                  {meta.purpose_options.map((p) => (
                    <option key={p} value={p}>{humanize(p)}</option>
                  ))}
                </select>
              </div>
            </div>
            <button className="btn mt-20" type="submit" disabled={loading}>
              {loading ? 'Calculando…' : 'Predecir'}
            </button>
          </form>
        </div>

        <div className="card">
          <h3 className="card-title">Resultado</h3>
          {error && <ErrorState error={error} />}
          {!error && !result && (
            <div className="state">Completa el formulario y pulsa <b>Predecir</b>.</div>
          )}
          {!error && result && tab === 'classification' && (
            <ClassificationResult result={result} />
          )}
          {!error && result && tab === 'regression' && (
            <RegressionResult result={result} />
          )}
        </div>
      </div>
    </>
  )
}

function ClassificationResult({ result }) {
  const p = result.probability_default
  const isDefault = result.prediction === 'Charged Off'
  const color = p >= 0.5 ? '#f85149' : p >= 0.3 ? '#d29922' : '#3fb950'
  return (
    <div className="result-card">
      <span className={'pill ' + (isDefault ? 'pill-default' : 'pill-paid')}>
        {isDefault ? 'Probable default' : 'Probable pago completo'}
      </span>
      <div className="result-big" style={{ color }}>{formatPercent(p)}</div>
      <div className="muted">Probabilidad estimada de default</div>
      <div className="gauge-track">
        <div className="gauge-fill" style={{ width: `${p * 100}%`, background: color }} />
      </div>
      <div className="muted">Modelo: <b>{result.model}</b></div>
    </div>
  )
}

function RegressionResult({ result }) {
  return (
    <div className="result-card">
      <span className="pill pill-paid">Tasa de interés estimada</span>
      <div className="result-big kpi-accent">{result.predicted_int_rate.toFixed(2)}%</div>
      <div className="muted">int_rate predicho para este perfil</div>
      <div className="muted mt-20">Modelo: <b>{result.model}</b></div>
    </div>
  )
}
