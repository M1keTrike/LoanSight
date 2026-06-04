import { useEffect, useState } from 'react'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  ReferenceLine,
} from 'recharts'
import { api } from '../api/client.js'
import { PageHeader, Loading, ErrorState } from '../components/States.jsx'
import { formatInt } from '../utils/format.js'

const AXIS = { stroke: '#8b949e', fontSize: 12 }
const TOOLTIP_STYLE = {
  background: '#161b22', border: '1px solid #2a313c', borderRadius: 8, color: '#e6edf3',
}

export default function Models() {
  const [metrics, setMetrics] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => { api.modelMetrics().then(setMetrics).catch(setError) }, [])

  if (error) return <ErrorState error={error} />
  if (!metrics) return <Loading label="Cargando métricas…" />

  const reg = metrics.regression
  const clf = metrics.classification
  const bestClf = clf.models.find((m) => m.model === clf.best_model)

  const rocData = bestClf.roc_curve.fpr.map((fpr, i) => ({
    fpr, tpr: bestClf.roc_curve.tpr[i],
  }))

  return (
    <>
      <PageHeader
        title="Modelos"
        subtitle={`Comparativa de algoritmos. Muestra de ${formatInt(metrics.sample_size)} préstamos · random_state=${metrics.random_state}.`}
      />

      <div className="card mb-16">
        <h3 className="card-title">Regresión — predicción de <code>int_rate</code> (mejor: RMSE más bajo)</h3>
        <table>
          <thead>
            <tr>
              <th>Modelo</th>
              <th className="num">RMSE</th>
              <th className="num">MAE</th>
              <th className="num">R²</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {reg.models.map((m) => (
              <tr key={m.model} className={m.model === reg.best_model ? 'best' : ''}>
                <td>{m.model}</td>
                <td className="num">{m.rmse.toFixed(3)}</td>
                <td className="num">{m.mae.toFixed(3)}</td>
                <td className="num">{m.r2.toFixed(3)}</td>
                <td>{m.model === reg.best_model && <span className="badge badge-best">MEJOR</span>}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card mb-16">
        <h3 className="card-title">
          Clasificación — predicción de default (mejor: AUC más alto)
        </h3>
        <p className="muted mb-16">
          Datos desbalanceados (default_rate ≈ {(clf.default_rate_train * 100).toFixed(1)}%):
          se priorizan AUC-ROC y F1 sobre accuracy.
        </p>
        <table>
          <thead>
            <tr>
              <th>Modelo</th>
              <th className="num">AUC-ROC</th>
              <th className="num">F1</th>
              <th className="num">Precision</th>
              <th className="num">Recall</th>
              <th className="num">Accuracy</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {clf.models.map((m) => (
              <tr key={m.model} className={m.model === clf.best_model ? 'best' : ''}>
                <td>{m.model}</td>
                <td className="num">{m.auc.toFixed(3)}</td>
                <td className="num">{m.f1.toFixed(3)}</td>
                <td className="num">{m.precision.toFixed(3)}</td>
                <td className="num">{m.recall.toFixed(3)}</td>
                <td className="num">{m.accuracy.toFixed(3)}</td>
                <td>{m.model === clf.best_model && <span className="badge badge-best">MEJOR</span>}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="grid grid-2">
        <div className="card">
          <h3 className="card-title">Curva ROC — {clf.best_model} (AUC = {bestClf.auc.toFixed(3)})</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={rocData} margin={{ top: 10, right: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a313c" />
              <XAxis type="number" dataKey="fpr" domain={[0, 1]} {...AXIS}
                label={{ value: 'FPR', position: 'insideBottom', offset: -4, fill: '#8b949e', fontSize: 12 }} />
              <YAxis type="number" dataKey="tpr" domain={[0, 1]} {...AXIS}
                label={{ value: 'TPR', angle: -90, position: 'insideLeft', fill: '#8b949e', fontSize: 12 }} />
              <Tooltip contentStyle={TOOLTIP_STYLE}
                formatter={(v) => v.toFixed(3)} />
              <ReferenceLine segment={[{ x: 0, y: 0 }, { x: 1, y: 1 }]}
                stroke="#8b949e" strokeDasharray="4 4" />
              <Line type="monotone" dataKey="tpr" stroke="#3fb950" strokeWidth={2.5} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h3 className="card-title">Matriz de confusión — {clf.best_model}</h3>
          <ConfusionMatrix cm={bestClf.confusion_matrix} />
        </div>
      </div>
    </>
  )
}

function ConfusionMatrix({ cm }) {

  const [[tn, fp], [fn, tp]] = cm
  return (
    <div style={{ display: 'flex', justifyContent: 'center', marginTop: 8 }}>
      <div className="cm-grid">
        <div />
        <div className="cm-head">Pred. Pagado</div>
        <div className="cm-head">Pred. Default</div>

        <div className="cm-head">Real Pagado</div>
        <div className="cm-cell cm-tn">{formatInt(tn)}<span className="cm-sub">TN</span></div>
        <div className="cm-cell cm-fp">{formatInt(fp)}<span className="cm-sub">FP</span></div>

        <div className="cm-head">Real Default</div>
        <div className="cm-cell cm-fn">{formatInt(fn)}<span className="cm-sub">FN</span></div>
        <div className="cm-cell cm-tp">{formatInt(tp)}<span className="cm-sub">TP</span></div>
      </div>
    </div>
  )
}
