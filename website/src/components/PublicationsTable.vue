<template>
  <div class="publications-table card">
    <h3>Publications</h3>
    <div class="table-container">
      <table v-if="papers.length > 0">
        <thead>
          <tr>
            <th>Title</th>
            <th>Venue</th>
            <th>Year</th>
            <th>Citations</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="paper in papers" :key="paper.id || paper.paper_id">
            <td class="paper-title">
              <a 
                v-if="paper.url" 
                :href="paper.url" 
                target="_blank" 
                rel="noopener noreferrer"
                class="paper-link"
              >
                {{ paper.title }}
              </a>
              <span v-else>{{ paper.title }}</span>
            </td>
            <td>{{ paper.venue || 'N/A' }}</td>
            <td>{{ paper.year || 'N/A' }}</td>
            <td>{{ formatCitations(paper.citation_count) }}</td>
          </tr>
        </tbody>
      </table>
      
      <div v-else class="no-papers">
        <p>No publications found for this author.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  papers: {
    type: Array,
    required: true,
    default: () => []
  }
})

const formatCitations = (citations) => {
  if (citations === undefined || citations === null || citations === '') {
    return 'N/A'
  }
  
  const num = parseInt(citations)
  if (isNaN(num)) return 'N/A'
  
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  
  return num.toString()
}
</script>

<style scoped>
.publications-table h3 {
  margin-bottom: 20px;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.table-container {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

thead {
  background-color: var(--background);
  border-bottom: 2px solid var(--border-color);
}

th {
  text-align: left;
  padding: 12px 16px;
  font-weight: 600;
  color: var(--text-primary);
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

td {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
  vertical-align: top;
}

.paper-title {
  max-width: 300px;
}

.paper-link {
  color: var(--primary);
  text-decoration: none;
  font-weight: 500;
}

.paper-link:hover {
  text-decoration: underline;
}

.no-papers {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-secondary);
}

@media (max-width: 768px) {
  th, td {
    padding: 8px 12px;
    font-size: 13px;
  }
  
  .paper-title {
    max-width: 200px;
  }
  
  table {
    font-size: 13px;
  }
}
</style> 