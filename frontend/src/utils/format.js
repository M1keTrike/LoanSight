export function formatMetric(value, format) {
  if (value === null || value === undefined || Number.isNaN(value)) return '—'
  switch (format) {
    case 'percent':
      return `${(value * 100).toFixed(2)}%`
    case 'percent_points':
      return `${value.toFixed(2)}%`
    case 'currency':
      return formatCurrency(value)
    case 'integer':
      return Math.round(value).toLocaleString('en-US')
    default:
      return value.toLocaleString('en-US', { maximumFractionDigits: 2 })
  }
}

export function formatCurrency(value) {
  if (value === null || value === undefined) return '—'
  if (Math.abs(value) >= 1e9) return `$${(value / 1e9).toFixed(2)}B`
  if (Math.abs(value) >= 1e6) return `$${(value / 1e6).toFixed(2)}M`
  if (Math.abs(value) >= 1e3) return `$${(value / 1e3).toFixed(1)}K`
  return `$${value.toFixed(0)}`
}

export function formatPercent(value, digits = 2) {
  if (value === null || value === undefined) return '—'
  return `${(value * 100).toFixed(digits)}%`
}

export function formatInt(value) {
  if (value === null || value === undefined) return '—'
  return Math.round(value).toLocaleString('en-US')
}

export function humanize(text) {
  if (!text) return ''
  return text
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase())
}
