const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function request(path, { params, method = 'GET', body } = {}) {
  const url = new URL(path, BASE_URL)
  if (params) {
    Object.entries(params).forEach(([k, v]) => {
      if (v !== null && v !== undefined && v !== '') url.searchParams.set(k, v)
    })
  }
  const options = { method, headers: {} }
  if (body !== undefined) {
    options.headers['Content-Type'] = 'application/json'
    options.body = JSON.stringify(body)
  }

  const res = await fetch(url, options)
  if (!res.ok) {
    let detail
    try {
      detail = (await res.json()).detail
    } catch {
      detail = res.statusText
    }
    throw new Error(typeof detail === 'string' ? detail : `Error ${res.status}`)
  }
  return res.json()
}

export const api = {

  health: () => request('/health'),

  dimensions: () => request('/olap/dimensions'),
  metrics: () => request('/olap/metrics'),
  yearRange: () => request('/olap/year-range'),
  kpis: (yearFrom, yearTo) =>
    request('/olap/kpis', { params: { year_from: yearFrom, year_to: yearTo } }),
  olapQuery: ({ dimension, metric, yearFrom, yearTo }) =>
    request('/olap/query', {
      params: { dimension, metric, year_from: yearFrom, year_to: yearTo },
    }),

  predictClassification: (features) =>
    request('/predict/classification', { method: 'POST', body: features }),
  predictRegression: (features) =>
    request('/predict/regression', { method: 'POST', body: features }),

  modelMetrics: () => request('/models/metrics'),
  modelMetadata: () => request('/models/metadata'),
}

export { BASE_URL }
