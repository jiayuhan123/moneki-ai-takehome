<script setup lang="ts">
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import * as echarts from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { nextTick, onBeforeUnmount, ref, watch } from 'vue'

import type { DailyMetric } from '../types/api'

echarts.use([LineChart, GridComponent, TooltipComponent, CanvasRenderer])

const props = defineProps<{
  days: DailyMetric[]
  loading: boolean
}>()

const chartElement = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null
let resizeObserver: ResizeObserver | null = null

function renderChart() {
  const element = chartElement.value
  // 旧实现使用 v-show 隐藏图表：组件 mounted 时容器是 display:none，ECharts
  // 会在 0x0 的节点上初始化并输出警告。现在只在容器真实可见且浏览器已经
  // 完成一帧布局后初始化；尺寸保护同时覆盖面板暂时被父级隐藏的边界情况。
  if (!element || element.clientWidth === 0 || element.clientHeight === 0) return
  if (!chart) {
    chart = echarts.init(element)
    resizeObserver = new ResizeObserver(() => chart?.resize())
    resizeObserver.observe(element)
  }
  chart.setOption({
    animationDuration: 450,
    grid: { left: 20, right: 16, top: 24, bottom: 12, containLabel: true },
    tooltip: {
      trigger: 'axis',
      valueFormatter: (value: unknown) => `¥${Number(value).toLocaleString('zh-CN')}`,
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: props.days.map((day) => day.date.slice(5)),
      axisLine: { lineStyle: { color: '#d8d2c5' } },
      axisLabel: { color: '#68756e', hideOverlap: true },
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: '#68756e',
        formatter: (value: number) => `¥${value.toLocaleString('zh-CN')}`,
      },
      splitLine: { lineStyle: { color: '#ece8df' } },
    },
    series: [
      {
        name: '净营业额',
        type: 'line',
        smooth: 0.24,
        showSymbol: props.days.length <= 20,
        symbolSize: 7,
        lineStyle: { width: 3, color: '#df6b35' },
        itemStyle: { color: '#df6b35' },
        areaStyle: { color: 'rgba(223, 107, 53, 0.10)' },
        data: props.days.map((day) => day.net_revenue),
      },
    ],
  })
}

watch(
  () => [props.days, props.loading] as const,
  async () => {
    await nextTick()
    if (!props.loading && props.days.length > 0) {
      requestAnimationFrame(renderChart)
    }
  },
  { deep: true, immediate: true },
)

onBeforeUnmount(() => {
  resizeObserver?.disconnect()
  chart?.dispose()
})
</script>

<template>
  <section class="panel chart-panel">
    <header>
      <div>
        <p class="section-kicker">REVENUE TREND</p>
        <h2>每日净营业额</h2>
      </div>
      <span>{{ days.length }} 天</span>
    </header>
    <div v-if="loading" class="empty">正在读取趋势…</div>
    <div v-else-if="days.length === 0" class="empty">当前筛选条件下没有日期数据</div>
    <div v-else ref="chartElement" class="chart" />
  </section>
</template>

<style scoped>
.panel {
  padding: 24px;
  border: 1px solid var(--line);
  border-radius: 18px;
  background: var(--paper);
  box-shadow: var(--shadow);
}

header {
  display: flex;
  align-items: start;
  justify-content: space-between;
  gap: 16px;
}

header span {
  padding: 6px 10px;
  border-radius: 999px;
  background: #f0ece2;
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
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

.chart {
  width: 100%;
  height: 350px;
  margin-top: 16px;
}

.empty {
  display: grid;
  height: 350px;
  place-items: center;
  color: var(--muted);
}
</style>
