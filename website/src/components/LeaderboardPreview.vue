<template>
  <div class="leaderboard-preview card">
    <div class="preview-header">
      <h3>{{ title }}</h3>
      <router-link :to="`/ranking/${metric}`" class="view-all">View All</router-link>
    </div>
    
    <div class="preview-list" v-if="!loading">
      <div 
        v-for="(author, index) in topAuthors" 
        :key="author.id || author.author_id"
        class="preview-item"
      >
        <div class="rank">{{ index + 1 }}</div>
        <div class="author-info">
          <router-link 
            :to="`/author/${author.id || author.author_id}`"
            class="author-name"
          >
            {{ author.name || author.author_name }}
          </router-link>
          <div class="author-affiliation" v-if="author.affiliation">
            {{ author.affiliation }}
          </div>
        </div>
        <div class="score">{{ formatScore(author[scoreField]) }}</div>
      </div>
    </div>
    
    <div class="loading" v-else>
      Loading...
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getTop100PQI, getTop100ANCI, getTop100ACCEL } from '../services/dataLoader'

const props = defineProps({
  metric: {
    type: String,
    required: true,
    validator: (value) => ['pqi', 'anci', 'accel'].includes(value)
  },
  title: {
    type: String,
    required: true
  }
})

const loading = ref(true)
const topAuthors = ref([])

const scoreField = {
  pqi: 'pqi_score',
  anci: 'anci_score', 
  accel: 'accel_score'
}[props.metric]

const dataLoaders = {
  pqi: getTop100PQI,
  anci: getTop100ANCI,
  accel: getTop100ACCEL
}

const formatScore = (score) => {
  if (score === undefined || score === null) return 'N/A'
  return parseFloat(score).toFixed(2)
}

onMounted(async () => {
  try {
    const data = await dataLoaders[props.metric]()
    topAuthors.value = data.slice(0, 5) // Top 5 authors
  } catch (error) {
    console.error('Error loading leaderboard data:', error)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.leaderboard-preview {
  height: 100%;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.preview-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.view-all {
  color: var(--primary);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
}

.view-all:hover {
  text-decoration: underline;
}

.preview-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.preview-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid var(--border-color);
}

.preview-item:last-child {
  border-bottom: none;
}

.rank {
  font-weight: 600;
  color: var(--primary);
  min-width: 24px;
  font-size: 14px;
}

.author-info {
  flex: 1;
  min-width: 0;
}

.author-name {
  color: var(--text-primary);
  text-decoration: none;
  font-weight: 500;
  display: block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.author-name:hover {
  color: var(--primary);
}

.author-affiliation {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.score {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 14px;
}

.loading {
  text-align: center;
  color: var(--text-secondary);
  padding: 20px 0;
}

@media (max-width: 768px) {
  .preview-item {
    gap: 8px;
  }
  
  .author-affiliation {
    font-size: 11px;
  }
}
</style> 