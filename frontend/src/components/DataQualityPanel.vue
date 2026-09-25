<script setup lang="ts">
import { computed } from 'vue'

import type { DataQualityResponse } from '../types/api'

const props = defineProps<{
  quality: DataQualityResponse | null
  loading: boolean
}>()

const labels: Record<string, string> = {
  '1_unparseable_date': '日期无法解析',
  '2_empty_amount': '金额为空或无效',
  '3_qty_le_zero': '数量小于等于 0',
  '4_store_not_in_stores': '门店外键无效',
  '5_product_not_in_products': '商品外键无效',
  '6_duplicate_row': '完全重复明细',
}

const integer = new Intl.NumberFormat('zh-CN')
const report = computed(() => props.quality?.cleaning_report)
const retention = computed(() => {
  if (!report.value?.raw_rows) return 0
  return (report.value.kept_rows / report.value.raw_rows) * 100
})
const removals = computed(() =>
  Object.entries(report.value?.removed ?? {})
    .filter(([key]) => key in labels)
    .map(([key, value]) => ({ key, label: labels[key], value })),
)
</script>

<template>
  <section class="panel quality-panel">
    <header>
      <div>
        <p class="section-kicker">DATA QUALITY</p>
        <h2>数据质量台账</h2>
      </div>
      <span>KB-001 v3</span>
    </header>

    <div v-if="loading || !report" class="empty">正在核对清洗台账…</div>
    <template v-else>
      <div class="quality-summary">
        <div>
          <span>原始明细</span>
          <strong>{{ integer.format(report.raw_rows) }}</strong>
        </div>
        <div>
          <span>有效明细</span>
          <strong>{{ integer.format(report.kept_rows) }}</strong>
        </div>
        <div>
          <span>已剔除</span>
          <strong>{{ integer.format(quality?.removed_total ?? 0) }}</strong>
        </div>
      </div>

      <div class="retention-head">
        <span>数据保留率</span>
        <strong>{{ retention.toFixed(2) }}%</strong>
      </div>
      <div class="retention-track" aria-label="数据保留率">
        <div :style="{ width: `${retention}%` }" />
      </div>

      <ul>
        <li v-for="item in removals" :key="item.key">
          <span>{{ item.label }}</span>
          <strong>{{ integer.format(item.value) }}</strong>
        </li>
      </ul>

      <p class="footnote">
        保留 {{ integer.format(report.kept_sales_rows) }} 条销售行与
        {{ integer.format(report.kept_refund_rows) }} 条退款行。
      </p>
    </template>
  </section>
</template>

<style scoped>
.panel {
  padding: 24px;
  border: 1px solid var(--line);
  border-radius: 18px;
  background: var(--ink);
  color: #fffdf8;
  box-shadow: var(--shadow);
}

header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
}

header > span {
  color: #bfc9c2;
  font-size: 12px;
}

.section-kicker {
  margin: 0 0 5px;
  color: #f0a37f;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.12em;
}

h2 {
  margin: 0;
  font-family: Georgia, "Songti SC", serif;
  font-size: 23px;
}

.quality-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin: 22px 0;
}

.quality-summary > div {
  padding: 13px;
  border: 1px solid rgb(255 255 255 / 12%);
  border-radius: 11px;
  background: rgb(255 255 255 / 5%);
}

.quality-summary span,
.quality-summary strong {
  display: block;
}

.quality-summary span,
.retention-head span,
.footnote {
  color: #bfc9c2;
  font-size: 11px;
}

.quality-summary strong {
  margin-top: 7px;
  font-size: 21px;
}

.retention-head {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.retention-track {
  height: 7px;
  overflow: hidden;
  border-radius: 999px;
  background: rgb(255 255 255 / 10%);
}

.retention-track div {
  height: 100%;
  border-radius: inherit;
  background: #ef8b5e;
}

ul {
  display: grid;
  gap: 0;
  margin: 20px 0 0;
  padding: 0;
  list-style: none;
}

li {
  display: flex;
  justify-content: space-between;
  padding: 9px 0;
  border-bottom: 1px solid rgb(255 255 255 / 9%);
  font-size: 12px;
}

li span {
  color: #d4dcd6;
}

.footnote {
  margin: 16px 0 0;
  line-height: 1.6;
}

.empty {
  display: grid;
  min-height: 300px;
  place-items: center;
  color: #bfc9c2;
}
</style>
