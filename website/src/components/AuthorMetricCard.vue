<template>
  <div class="metric-card card">
    <div class="metric-name">{{ name }}</div>
    <div class="metric-value">{{ formatValue(value) }}</div>
  </div>
</template>

<script setup>
const props = defineProps({
  name: {
    type: String,
    required: true
  },
  value: {
    type: [String, Number],
    required: true
  }
})

const formatValue = (value) => {
  if (value === undefined || value === null || value === '') {
    return 'N/A'
  }
  
  if (typeof value === 'number') {
    return value.toFixed(2)
  }
  
  return value
}
</script>

<style scoped>
.metric-card {
  text-align: center;
  padding: 16px;
  min-width: 120px;
}

.metric-name {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.metric-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

@media (max-width: 768px) {
  .metric-card {
    min-width: 100px;
    padding: 12px;
  }
  
  .metric-value {
    font-size: 20px;
  }
}
</style> 