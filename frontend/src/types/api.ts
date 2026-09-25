export interface DataPeriod {
  start: string
  end: string
}

export interface HealthResponse {
  status: string
  llm_mode: 'mock' | 'live'
  kb_docs: number
  kb_chunks: number
  valid_sales_rows: number
  today: string
  data_period: DataPeriod
}

export interface Store {
  store_id: string
  store_name: string
  category: string
  district: string
}

export interface SummaryMetrics {
  start: string
  end: string
  store_id: string | null
  product_id: string | null
  net_revenue: number
  refund_amount: number
  orders: number
  aov: number | null
  qty: number
}

export interface DailyMetric {
  date: string
  net_revenue: number
  orders: number
  aov: number | null
}

export interface ProductMetric {
  product_id: string
  product_name: string
  product_category: string
  net_revenue: number
  orders: number
  qty: number
}

export interface CleaningReport {
  raw_rows: number
  kept_rows: number
  kept_sales_rows: number
  kept_refund_rows: number
  removed: Record<string, number>
}

export interface DataQualityResponse {
  cleaning_report: CleaningReport
  removed_total: number
  data_period: DataPeriod
  kb_warnings: string[]
}

export interface DashboardFilters {
  start: string
  end: string
  storeId: string
}
