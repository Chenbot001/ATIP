<template>
  <div class="ranking-view">
    <div class="container">
      <div class="ranking-header">
        <h1 class="ranking-title">{{ getMetricTitle(metric) }} Rankings</h1>
        <p class="ranking-description">{{ getMetricDescription(metric) }}</p>
      </div>

      <div class="ranking-table-container card">
        <div v-if="loading" class="loading-container">
          <div class="loading-spinner"></div>
          <p>Loading rankings...</p>
        </div>

        <div v-else-if="error" class="error-container">
          <p>{{ error }}</p>
        </div>

        <div v-else class="table-wrapper">
          <table class="ranking-table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>Name</th>
                <th>Affiliation</th>
                <th>{{ getMetricTitle(metric) }} Score</th>
              </tr>
            </thead>
            <tbody>
              <tr 
                v-for="(author, index) in rankings" 
                :key="author.id || author.author_id"
                class="ranking-row"
              >
                <td class="rank-cell">
                  <span class="rank-number">{{ index + 1 }}</span>
                </td>
                <td class="name-cell">
                  <router-link 
                    :to="`/author/${author.id || author.author_id}`"
                    class="author-link"
                  >
                    {{ author.name || author.author_name }}
                  </router-link>
                </td>
                <td class="affiliation-cell">
                  {{ author.affiliation || 'N/A' }}
                </td>
                <td class="score-cell">
                  {{ formatScore(author[scoreField]) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { getTop100PQI, getTop100ANCI, getTop100ACCEL } from '../services/dataLoader'

const props = defineProps({
  metric: {
    type: String,
    required: true,
    validator: (value) => ['pqi', 'anci', 'accel'].includes(value)
  }
})

const loading = ref(true)
const error = ref(null)
const rankings = ref([])

const scoreField = computed(() => {
  const fields = {
    pqi: 'pqi_score',
    anci: 'anci_score',
    accel: 'accel_score'
  }
  return fields[props.metric]
})

const dataLoaders = {
  pqi: getTop100PQI,
  anci: getTop100ANCI,
  accel: getTop100ACCEL
}

const getMetricTitle = (metric) => {
  const titles = {
    pqi: 'PQI',
    anci: 'ANCI',
    accel: 'ACCEL'
  }
  return titles[metric] || metric.toUpperCase()
}

const getMetricDescription = (metric) => {
  const descriptions = {
    pqi: 'Paper Quality Index - measures the quality and impact of research publications',
    anci: 'Academic Network Citation Index - evaluates citation patterns and academic influence',
    accel: 'Academic Excellence - comprehensive measure of research excellence and productivity'
  }
  return descriptions[metric] || 'Academic performance metric'
}

const formatScore = (score) => {
  if (score === undefined || score === null || score === '') {
    return 'N/A'
  }
  return parseFloat(score).toFixed(2)
}

onMounted(async () => {
  try {
    loading.value = true
    error.value = null
    
    const data = await dataLoaders[props.metric]()
    rankings.value = data
  } catch (err) {
    console.error('Error loading rankings:', err)
    error.value = 'Failed to load rankings. Please try again later.'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.ranking-view {
  padding: 40px 0;
}

.ranking-header {
  text-align: center;
  margin-bottom: 40px;
}

.ranking-title {
  font-size: 36px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.ranking-description {
  font-size: 18px;
  color: var(--text-secondary);
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.6;
}

.ranking-table-container {
  overflow: hidden;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--border-color);
  border-top: 4px solid var(--primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-container {
  text-align: center;
  padding: 40px 20px;
  color: #EF4444;
}

.table-wrapper {
  overflow-x: auto;
}

.ranking-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 16px;
}

.ranking-table thead {
  background-color: var(--background);
  border-bottom: 2px solid var(--border-color);
}

.ranking-table th {
  text-align: left;
  padding: 16px 20px;
  font-weight: 600;
  color: var(--text-primary);
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.ranking-table td {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
  vertical-align: middle;
}

.ranking-row:hover {
  background-color: var(--background);
}

.rank-cell {
  width: 80px;
  text-align: center;
}

.rank-number {
  display: inline-block;
  width: 32px;
  height: 32px;
  background-color: var(--primary);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
}

.name-cell {
  min-width: 200px;
}

.author-link {
  color: var(--primary);
  text-decoration: none;
  font-weight: 500;
}

.author-link:hover {
  text-decoration: underline;
}

.affiliation-cell {
  min-width: 250px;
  color: var(--text-secondary);
}

.score-cell {
  text-align: right;
  font-weight: 600;
  color: var(--text-primary);
  min-width: 120px;
}

@media (max-width: 768px) {
  .ranking-title {
    font-size: 28px;
  }
  
  .ranking-description {
    font-size: 16px;
  }
  
  .ranking-table {
    font-size: 14px;
  }
  
  .ranking-table th,
  .ranking-table td {
    padding: 12px 16px;
  }
  
  .name-cell {
    min-width: 150px;
  }
  
  .affiliation-cell {
    min-width: 150px;
  }
}
</style> 