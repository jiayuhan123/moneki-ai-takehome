<script setup lang="ts">
import type { Store } from '../types/api'

defineProps<{
  stores: Store[]
  loading: boolean
}>()

const start = defineModel<string>('start', { required: true })
const end = defineModel<string>('end', { required: true })
const storeId = defineModel<string>('storeId', { required: true })

defineEmits<{
  submit: []
  reset: []
}>()
</script>

<template>
  <form class="filter-bar" @submit.prevent="$emit('submit')">
    <label>
      <span>开始日期</span>
      <input v-model="start" type="date" required />
    </label>
    <label>
      <span>结束日期</span>
      <input v-model="end" type="date" required />
    </label>
    <label class="store-field">
      <span>门店</span>
      <select v-model="storeId">
        <option value="">全部门店</option>
        <option v-for="store in stores" :key="store.store_id" :value="store.store_id">
          {{ store.store_id }} · {{ store.store_name }}（{{ store.district }}）
        </option>
      </select>
    </label>
    <div class="actions">
      <button class="secondary" type="button" :disabled="loading" @click="$emit('reset')">
        重置
      </button>
      <button class="primary" type="submit" :disabled="loading">
        {{ loading ? '正在查询…' : '查询数据' }}
      </button>
    </div>
  </form>
</template>

<style scoped>
.filter-bar {
  display: grid;
  grid-template-columns: 180px 180px minmax(260px, 1fr) auto;
  gap: 16px;
  align-items: end;
  padding: 20px;
  border: 1px solid var(--line);
  border-radius: 18px;
  background: rgb(255 253 248 / 88%);
  box-shadow: var(--shadow);
}

label {
  display: grid;
  gap: 7px;
}

label span {
  color: var(--muted);
  font-size: 12px;
  font-weight: 750;
  letter-spacing: 0.04em;
}

input,
select {
  width: 100%;
  height: 44px;
  padding: 0 12px;
  border: 1px solid #cbc5b8;
  border-radius: 10px;
  outline: none;
  background: white;
  color: var(--ink);
}

input:focus,
select:focus {
  border-color: var(--brand);
  box-shadow: 0 0 0 3px rgb(223 107 53 / 14%);
}

.actions {
  display: flex;
  gap: 10px;
}

button {
  height: 44px;
  padding: 0 18px;
  border: 0;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 750;
}

button:disabled {
  cursor: wait;
  opacity: 0.58;
}

.primary {
  background: var(--ink);
  color: white;
}

.secondary {
  border: 1px solid var(--line);
  background: transparent;
  color: var(--ink);
}

@media (max-width: 900px) {
  .filter-bar {
    grid-template-columns: 1fr 1fr;
  }

  .store-field,
  .actions {
    grid-column: 1 / -1;
  }

  .actions button {
    flex: 1;
  }
}

@media (max-width: 560px) {
  .filter-bar {
    grid-template-columns: 1fr;
  }

  .store-field,
  .actions {
    grid-column: auto;
  }
}
</style>
