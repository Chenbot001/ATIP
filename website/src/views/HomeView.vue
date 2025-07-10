<template>
  <div class="home-view">
    <div class="container">
      <!-- Hero Section -->
      <div class="hero-section">
        <h1 class="main-title">ATIP</h1>
        <p class="subtitle">Academic Talent Identification and Profiling</p>
        <p class="description">
          Discover and rank researchers based on programmatically calculated metrics. 
          What does AI think of academic talent?
        </p>
        
        <!-- Search Bar -->
        <div class="search-section">
          <div class="search-container">
            <input 
              v-model="searchQuery"
              @keyup.enter="handleSearch"
              type="text" 
              placeholder="Search for researchers..."
              class="search-input"
            />
            <button @click="handleSearch" class="search-button">
              Search
            </button>
          </div>
        </div>
      </div>

      <!-- Leaderboards Section -->
      <div class="leaderboards-section">
        <h2 class="section-title">Top Researchers by Metric</h2>
        <div class="leaderboards-grid">
          <LeaderboardPreview 
            metric="pqi" 
            title="PQI Score" 
          />
          <LeaderboardPreview 
            metric="anci" 
            title="ANCI Score" 
          />
          <LeaderboardPreview 
            metric="accel" 
            title="ACCEL Score" 
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import LeaderboardPreview from '../components/LeaderboardPreview.vue'

const router = useRouter()
const searchQuery = ref('')

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    // For now, just navigate to a search results page or show a message
    // In a real implementation, you'd want to implement search functionality
    alert(`Search functionality for "${searchQuery.value}" would be implemented here.`)
  }
}
</script>

<style scoped>
.home-view {
  min-height: 100vh;
}

.hero-section {
  text-align: center;
  padding: 60px 0 40px;
}

.main-title {
  font-size: 64px;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 16px;
  letter-spacing: -2px;
}

.subtitle {
  font-size: 24px;
  color: var(--text-primary);
  margin-bottom: 16px;
  font-weight: 500;
}

.description {
  font-size: 18px;
  color: var(--text-secondary);
  max-width: 600px;
  margin: 0 auto 40px;
  line-height: 1.6;
}

.search-section {
  margin-bottom: 60px;
}

.search-container {
  display: flex;
  max-width: 500px;
  margin: 0 auto;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  overflow: hidden;
}

.search-input {
  flex: 1;
  padding: 16px 20px;
  border: none;
  font-size: 16px;
  outline: none;
  background-color: var(--surface);
}

.search-input::placeholder {
  color: var(--text-secondary);
}

.search-button {
  background-color: var(--primary);
  color: white;
  border: none;
  padding: 16px 24px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.search-button:hover {
  background-color: #2563eb;
}

.leaderboards-section {
  padding: 40px 0 60px;
}

.section-title {
  text-align: center;
  font-size: 32px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 40px;
}

.leaderboards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  max-width: 1000px;
  margin: 0 auto;
}

@media (max-width: 1024px) {
  .leaderboards-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .main-title {
    font-size: 48px;
  }
  
  .subtitle {
    font-size: 20px;
  }
  
  .description {
    font-size: 16px;
  }
  
  .leaderboards-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .section-title {
    font-size: 24px;
  }
  
  .hero-section {
    padding: 40px 0 30px;
  }
  
  .search-container {
    flex-direction: column;
  }
  
  .search-button {
    border-radius: 0 0 8px 8px;
  }
}
</style> 