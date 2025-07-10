<template>
  <div class="author-profile-view">
    <div class="container">
      <!-- Loading State -->
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>Loading author profile...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="error-container">
        <h2>Author Not Found</h2>
        <p>{{ error }}</p>
        <router-link to="/" class="btn">Back to Home</router-link>
      </div>

      <!-- Author Profile Content -->
      <div v-else-if="author" class="author-content">
        <!-- Header Section -->
        <div class="author-header card">
          <div class="author-info">
            <div class="author-avatar">
              <div class="avatar-placeholder">
                {{ getInitials(author.name || author.author_name) }}
              </div>
            </div>
            <div class="author-details">
              <h1 class="author-name">{{ author.name || author.author_name }}</h1>
              <p class="author-affiliation" v-if="author.affiliation">
                {{ author.affiliation }}
              </p>
              <div class="author-stats">
                <span class="stat-item">
                  <strong>{{ papers.length }}</strong> publications
                </span>
                <span class="stat-item" v-if="coauthors.length > 0">
                  <strong>{{ coauthors.length }}</strong> co-authors
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Metrics Dashboard -->
        <div class="metrics-section">
          <h2 class="section-title">Academic Metrics</h2>
          <div class="metrics-grid">
            <AuthorMetricCard 
              name="PQI Score" 
              :value="author.pqi_score" 
            />
            <AuthorMetricCard 
              name="ANCI Score" 
              :value="author.anci_score" 
            />
            <AuthorMetricCard 
              name="ACCEL Score" 
              :value="author.accel_score" 
            />
            <AuthorMetricCard 
              name="H-Index" 
              :value="author.h_index" 
            />
            <AuthorMetricCard 
              name="Citations" 
              :value="formatCitations(author.citations || author.citation_count)" 
            />
            <AuthorMetricCard 
              name="Papers" 
              :value="papers.length" 
            />
          </div>
        </div>

        <!-- Co-author Graph -->
        <CoauthorGraph :authorId="id" />

        <!-- Publications -->
        <PublicationsTable :papers="papers" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getAuthorById, getPapersByAuthor, getCoauthors } from '../services/dataLoader'
import AuthorMetricCard from '../components/AuthorMetricCard.vue'
import CoauthorGraph from '../components/CoauthorGraph.vue'
import PublicationsTable from '../components/PublicationsTable.vue'

const props = defineProps({
  id: {
    type: String,
    required: true
  }
})

const loading = ref(true)
const error = ref(null)
const author = ref(null)
const papers = ref([])
const coauthors = ref([])

const getInitials = (name) => {
  if (!name) return '?'
  return name
    .split(' ')
    .map(word => word.charAt(0))
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

const formatCitations = (citations) => {
  if (citations === undefined || citations === null || citations === '') {
    return 'N/A'
  }
  
  const num = parseInt(citations)
  if (isNaN(num)) return 'N/A'
  
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  
  return num.toString()
}

onMounted(async () => {
  try {
    loading.value = true
    error.value = null
    
    // Load author data
    const authorData = await getAuthorById(props.id)
    if (!authorData) {
      error.value = 'Author not found. Please check the URL and try again.'
      return
    }
    
    author.value = authorData
    
    // Load papers and coauthors in parallel
    const [papersData, coauthorsData] = await Promise.all([
      getPapersByAuthor(props.id),
      getCoauthors(props.id)
    ])
    
    papers.value = papersData
    coauthors.value = coauthorsData
    
  } catch (err) {
    console.error('Error loading author profile:', err)
    error.value = 'Failed to load author profile. Please try again later.'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.author-profile-view {
  padding: 40px 0;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100px 20px;
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
  padding: 100px 20px;
}

.error-container h2 {
  color: var(--text-primary);
  margin-bottom: 16px;
}

.error-container p {
  color: var(--text-secondary);
  margin-bottom: 24px;
}

.author-header {
  margin-bottom: 40px;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 24px;
}

.author-avatar {
  flex-shrink: 0;
}

.avatar-placeholder {
  width: 80px;
  height: 80px;
  background-color: var(--primary);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 600;
}

.author-details {
  flex: 1;
}

.author-name {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.author-affiliation {
  font-size: 18px;
  color: var(--text-secondary);
  margin-bottom: 16px;
}

.author-stats {
  display: flex;
  gap: 24px;
}

.stat-item {
  color: var(--text-secondary);
  font-size: 14px;
}

.stat-item strong {
  color: var(--text-primary);
  font-weight: 600;
}

.metrics-section {
  margin-bottom: 40px;
}

.section-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 24px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

@media (max-width: 768px) {
  .author-info {
    flex-direction: column;
    text-align: center;
    gap: 16px;
  }
  
  .author-name {
    font-size: 24px;
  }
  
  .author-affiliation {
    font-size: 16px;
  }
  
  .author-stats {
    justify-content: center;
  }
  
  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }
  
  .section-title {
    font-size: 20px;
  }
}
</style> 