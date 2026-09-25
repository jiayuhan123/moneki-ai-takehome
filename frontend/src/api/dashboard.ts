import type {
  DailyMetric,
  DashboardFilters,
  DataQualityResponse,
  HealthResponse,
  ProductMetric,
  Store,
  SummaryMetrics,
} from '../types/api'

interface RequestOptions {
  signal?: AbortSignal
  params?: Record<string, string | number | undefined>
}

async function apiJson<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const url = new URL(path, window.location.origin)
  for (const [key, value] of Object.entries(options.params ?? {})) {
    if (value !== undefined && value !== '') url.searchParams.set(key, String(value))
  }

  const response = await fetch(`${url.pathname}${url.search}`, {
    headers: { Accept: 'application/json' },
    signal: options.signal,
  })
  if (!response.ok) {
    const detail = await response.text()
    throw new Error(`接口 ${path} 返回 ${response.status}：${detail.slice(0, 180)}`)
  }
  return response.json() as Promise<T>
}

function metricParams(filters: DashboardFilters) {
  return {
    start: filters.start,
    end: filters.end,
    store_id: filters.storeId || undefined,
  }
}

export const dashboardApi = {
  health: (signal?: AbortSignal) => apiJson<HealthResponse>('/api/health', { signal }),
  stores: (signal?: AbortSignal) =>
    apiJson<{ stores: Store[] }>('/api/stores', { signal }).then((body) => body.stores),
  summary: (filters: DashboardFilters, signal?: AbortSignal) =>
    apiJson<SummaryMetrics>('/api/metrics/summary', {
      signal,
      params: metricParams(filters),
    }),
  daily: (filters: DashboardFilters, signal?: AbortSignal) =>
    apiJson<{ days: DailyMetric[] }>('/api/metrics/daily', {
      signal,
      params: metricParams(filters),
    }).then((body) => body.days),
  topProducts: (filters: DashboardFilters, signal?: AbortSignal) =>
    apiJson<{ products: ProductMetric[] }>('/api/metrics/top-products', {
      signal,
      params: { ...metricParams(filters), limit: 10 },
    }).then((body) => body.products),
  dataQuality: (signal?: AbortSignal) =>
    apiJson<DataQualityResponse>('/api/data_quality', { signal }),
}
