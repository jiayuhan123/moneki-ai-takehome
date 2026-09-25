<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'

import { dashboardApi } from './api/dashboard'
import DashboardFilters from './components/DashboardFilters.vue'
import DataQualityPanel from './components/DataQualityPanel.vue'
import MetricCards from './components/MetricCards.vue'
import RevenueTrendChart from './components/RevenueTrendChart.vue'
import TopProductsTable from './components/TopProductsTable.vue'
import type {
  DailyMetric,
  DashboardFilters as DashboardFilterState,
  DataQualityResponse,
  HealthResponse,
  ProductMetric,
  Store,
  SummaryMetrics,
} from './types/api'

const health = ref<HealthResponse | null>(null)
const stores = ref<Store[]>([])
const summary = ref<SummaryMetrics | null>(null)
const days = ref<DailyMetric[]>([])
const products = ref<ProductMetric[]>([])
const quality = ref<DataQualityResponse | null>(null)
const loading = ref(true)
const error = ref('')
const lastUpdated = ref('')

const filters = reactive<DashboardFilterState>({ start: '', end: '', storeId: '' })
let activeRequest: AbortController | null = null

const scopeLabel = computed(() => {
  const store = stores.value.find((item) => item.store_id === filters.storeId)
  return store ? `${store.store_id} · ${store.store_name}` : '全部门店'
})

async function loadDashboard() {
  if (!filters.start || !filters.end) return
  if (filters.start > filters.end) {
    error.value = '开始日期不能晚于结束日期。'
    return
  }

  // 用户快速切换筛选时终止旧请求，防止较慢的旧响应覆盖新结果。
  activeRequest?.abort()
  activeRequest = new AbortController()
  loading.value = true
  error.value = ''
  try {
    const [nextSummary, nextDays, nextProducts, nextQuality] = await Promise.all([
      dashboardApi.summary(filters, activeRequest.signal),
      dashboardApi.daily(filters, activeRequest.signal),
      dashboardApi.topProducts(filters, activeRequest.signal),
      dashboardApi.dataQuality(activeRequest.signal),
    ])
    summary.value = nextSummary
    days.value = nextDays
    products.value = nextProducts
    quality.value = nextQuality
    lastUpdated.value = new Intl.DateTimeFormat('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    }).format(new Date())
  } catch (reason) {
    if ((reason as Error).name !== 'AbortError') {
      error.value = reason instanceof Error ? reason.message : '加载看板失败，请稍后重试。'
    }
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  if (!health.value) return
  filters.start = health.value.data_period.start
  filters.end = health.value.data_period.end
  filters.storeId = ''
  void loadDashboard()
}

onMounted(async () => {
  try {
    const [nextHealth, nextStores] = await Promise.all([dashboardApi.health(), dashboardApi.stores()])
    health.value = nextHealth
    stores.value = nextStores
    filters.start = nextHealth.data_period.start
    filters.end = nextHealth.data_period.end
    await loadDashboard()
  } catch (reason) {
    error.value = reason instanceof Error ? reason.message : '初始化看板失败。'
    loading.value = false
  }
})

onBeforeUnmount(() => activeRequest?.abort())
</script>

<template>
  <main class="app-shell">
    <header class="hero">
      <div>
        <p class="eyebrow">MONEKI OPERATIONS</p>
        <h1>经营数据看板</h1>
        <p class="intro">
          用统一的 KB-001 v3 口径观察门店趋势、商品表现与原始 POS 数据质量。
        </p>
      </div>
      <div class="status-card">
        <div class="status-row">
          <span class="status-dot" :class="health?.status === 'ok' ? 'online' : ''" />
          <strong>{{ health?.status === 'ok' ? '数据服务正常' : '正在连接服务' }}</strong>
        </div>
        <dl>
          <div><dt>服务模式</dt><dd>{{ health?.llm_mode === 'live' ? 'LIVE' : 'MOCK' }}</dd></div>
          <div><dt>知识文档</dt><dd>{{ health?.kb_docs ?? '—' }} 篇</dd></div>
          <div><dt>有效明细</dt><dd>{{ health?.valid_sales_rows?.toLocaleString('zh-CN') ?? '—' }}</dd></div>
        </dl>
      </div>
    </header>

    <DashboardFilters
      v-model:start="filters.start"
      v-model:end="filters.end"
      v-model:store-id="filters.storeId"
      :stores="stores"
      :loading="loading"
      @submit="loadDashboard"
      @reset="resetFilters"
    />

    <div v-if="error" class="error-banner" role="alert">
      <span>{{ error }}</span>
      <button type="button" @click="loadDashboard">重试</button>
    </div>

    <section class="context-line" aria-label="当前查询范围">
      <span>{{ scopeLabel }}</span>
      <span>{{ filters.start || '—' }} 至 {{ filters.end || '—' }}</span>
      <span v-if="lastUpdated">更新于 {{ lastUpdated }}</span>
    </section>

    <MetricCards :summary="summary" :loading="loading" />
    <RevenueTrendChart :days="days" :loading="loading" />

    <section class="lower-grid">
      <TopProductsTable :products="products" :loading="loading" />
      <DataQualityPanel :quality="quality" :loading="loading" />
    </section>
  </main>
</template>

<style scoped>
.hero {
  display: grid;
  grid-template-columns: 1fr minmax(270px, 340px);
  gap: 48px;
  align-items: end;
  margin-bottom: 30px;
}

.status-card {
  padding: 18px;
  border: 1px solid var(--line);
  border-radius: 16px;
  background: rgb(255 253 248 / 76%);
}

.status-row {
  display: flex;
  align-items: center;
  gap: 9px;
  margin-bottom: 14px;
}

.status-dot {
  width: 9px;
  height: 9px;
  border-radius: 999px;
  background: #aaa69b;
}

.status-dot.online {
  background: var(--positive);
  box-shadow: 0 0 0 5px rgb(44 122 91 / 12%);
}

dl {
  display: grid;
  gap: 8px;
  margin: 0;
}

dl div {
  display: flex;
  justify-content: space-between;
}

dt,
dd {
  margin: 0;
  font-size: 12px;
}

dt {
  color: var(--muted);
}

dd {
  font-weight: 750;
}

.context-line {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 18px 0 12px;
}

.context-line span {
  padding: 6px 10px;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: rgb(255 255 255 / 44%);
  color: var(--muted);
  font-size: 11px;
  font-weight: 650;
}

.error-banner {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-top: 14px;
  padding: 13px 16px;
  border: 1px solid #e0a69e;
  border-radius: 11px;
  background: #fff0ed;
  color: #7f2d24;
  font-size: 13px;
}

.error-banner button {
  border: 0;
  background: transparent;
  color: inherit;
  cursor: pointer;
  font-weight: 800;
}

.app-shell > :deep(.chart-panel) {
  margin-top: 16px;
}

.lower-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.65fr) minmax(340px, 0.85fr);
  gap: 16px;
  margin-top: 16px;
}

@media (max-width: 1050px) {
  .lower-grid,
  .hero {
    grid-template-columns: 1fr;
  }
}
</style>
