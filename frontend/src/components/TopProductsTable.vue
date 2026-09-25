<script setup lang="ts">
import type { ProductMetric } from '../types/api'

defineProps<{
  products: ProductMetric[]
  loading: boolean
}>()

const money = new Intl.NumberFormat('zh-CN', {
  style: 'currency',
  currency: 'CNY',
  minimumFractionDigits: 2,
})
const integer = new Intl.NumberFormat('zh-CN')
</script>

<template>
  <section class="panel products-panel">
    <header>
      <div>
        <p class="section-kicker">PRODUCT RANKING</p>
        <h2>Top 10 商品</h2>
      </div>
      <span>按净营业额</span>
    </header>

    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>排名</th>
            <th>商品</th>
            <th>净销量</th>
            <th>订单</th>
            <th>净营业额</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="5" class="empty">正在加载商品排行…</td>
          </tr>
          <tr v-else-if="products.length === 0">
            <td colspan="5" class="empty">当前筛选条件下没有商品数据</td>
          </tr>
          <tr v-for="(product, index) in products" v-else :key="product.product_id">
            <td><span class="rank" :class="{ top: index < 3 }">{{ index + 1 }}</span></td>
            <td>
              <strong>{{ product.product_name }}</strong>
              <small>{{ product.product_id }} · {{ product.product_category }}</small>
            </td>
            <td>{{ integer.format(product.qty) }}</td>
            <td>{{ integer.format(product.orders) }}</td>
            <td class="money">{{ money.format(product.net_revenue) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<style scoped>
.panel {
  min-width: 0;
  padding: 24px;
  border: 1px solid var(--line);
  border-radius: 18px;
  background: var(--paper);
  box-shadow: var(--shadow);
}

header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 17px;
}

header > span {
  color: var(--muted);
  font-size: 12px;
}

.section-kicker {
  margin: 0 0 5px;
  color: var(--brand-dark);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.12em;
}

h2 {
  margin: 0;
  font-family: Georgia, "Songti SC", serif;
  font-size: 23px;
}

.table-wrap {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

th,
td {
  padding: 12px 9px;
  border-bottom: 1px solid #ece8df;
  text-align: left;
  white-space: nowrap;
}

th {
  color: var(--muted);
  font-size: 11px;
  letter-spacing: 0.04em;
}

strong,
small {
  display: block;
}

small {
  margin-top: 3px;
  color: var(--muted);
}

.rank {
  display: grid;
  width: 27px;
  height: 27px;
  place-items: center;
  border-radius: 8px;
  background: #efebe2;
  font-weight: 800;
}

.rank.top {
  background: #f5d8c9;
  color: var(--brand-dark);
}

.money {
  color: var(--positive);
  font-weight: 750;
}

.empty {
  height: 160px;
  color: var(--muted);
  text-align: center;
}
</style>
