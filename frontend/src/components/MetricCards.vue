<script setup lang="ts">
import { computed } from 'vue'

import type { SummaryMetrics } from '../types/api'

const props = defineProps<{
  summary: SummaryMetrics | null
  loading: boolean
}>()

const money = new Intl.NumberFormat('zh-CN', {
  style: 'currency',
  currency: 'CNY',
  minimumFractionDigits: 2,
})
const integer = new Intl.NumberFormat('zh-CN')

const cards = computed(() => [
  {
    label: '净营业额',
    value: props.summary ? money.format(props.summary.net_revenue) : '—',
    note: '销售实收减去退款',
    tone: 'brand',
  },
  {
    label: '退款金额',
    value: props.summary ? money.format(props.summary.refund_amount) : '—',
    note: '按退款发生日归属',
    tone: 'danger',
  },
  {
    label: '有效订单',
    value: props.summary ? integer.format(props.summary.orders) : '—',
    note: '销售行去重订单号',
    tone: 'ink',
  },
  {
    label: '客单价',
    value: props.summary?.aov == null ? '—' : money.format(props.summary.aov),
    note: '净营业额 ÷ 有效订单',
    tone: 'positive',
  },
  {
    label: '净销量',
    value: props.summary ? integer.format(props.summary.qty) : '—',
    note: '销售数量减退款数量',
    tone: 'ink',
  },
])
</script>

<template>
  <section class="metrics" aria-label="经营指标">
    <article v-for="card in cards" :key="card.label" class="metric-card" :class="card.tone">
      <div class="label">{{ card.label }}</div>
      <div class="value" :class="{ shimmer: loading }">{{ loading ? '加载中' : card.value }}</div>
      <div class="note">{{ card.note }}</div>
    </article>
  </section>
</template>

<style scoped>
.metrics {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 14px;
}

.metric-card {
  min-height: 154px;
  padding: 21px;
  border: 1px solid var(--line);
  border-top: 4px solid var(--ink);
  border-radius: 16px;
  background: var(--paper);
  box-shadow: var(--shadow);
}

.metric-card.brand {
  border-top-color: var(--brand);
}

.metric-card.danger {
  border-top-color: var(--danger);
}

.metric-card.positive {
  border-top-color: var(--positive);
}

.label,
.note {
  color: var(--muted);
  font-size: 12px;
}

.value {
  margin: 16px 0 12px;
  font-size: clamp(22px, 2.4vw, 31px);
  font-weight: 800;
  letter-spacing: -0.035em;
}

.shimmer {
  color: #9a968c;
}

@media (max-width: 1100px) {
  .metrics {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 680px) {
  .metrics {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
