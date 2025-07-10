<template>
  <div class="coauthor-graph card">
    <h3>Co-author Network</h3>
    <div class="graph-container">
      <div ref="graphContainer" class="graph-element"></div>
      <div v-if="loading" class="loading-overlay">
        <div class="loading-text">Loading co-author network...</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import cytoscape from 'cytoscape'
import { getCoauthors, getAuthorById } from '../services/dataLoader'

const props = defineProps({
  authorId: {
    type: String,
    required: true
  }
})

const graphContainer = ref(null)
const loading = ref(true)
let cy = null

onMounted(async () => {
  try {
    const [author, coauthors] = await Promise.all([
      getAuthorById(props.authorId),
      getCoauthors(props.authorId)
    ])

    if (!author) {
      console.error('Author not found')
      return
    }

    // Create graph data
    const nodes = [
      {
        data: {
          id: author.id || author.author_id,
          name: author.name || author.author_name,
          isMain: true
        }
      },
      ...coauthors.map(coauthor => ({
        data: {
          id: coauthor.id || coauthor.author_id,
          name: coauthor.name || coauthor.author_name,
          isMain: false
        }
      }))
    ]

    const edges = coauthors.map(coauthor => ({
      data: {
        id: `${author.id || author.author_id}-${coauthor.id || coauthor.author_id}`,
        source: author.id || author.author_id,
        target: coauthor.id || coauthor.author_id
      }
    }))

    // Initialize Cytoscape
    cy = cytoscape({
      container: graphContainer.value,
      elements: {
        nodes,
        edges
      },
      style: [
        {
          selector: 'node',
          style: {
            'background-color': '#3B82F6',
            'label': 'data(name)',
            'color': '#FFFFFF',
            'font-size': '12px',
            'font-weight': 'bold',
            'text-wrap': 'wrap',
            'text-max-width': '80px',
            'text-valign': 'center',
            'text-halign': 'center',
            'width': '60px',
            'height': '60px',
            'border-width': '2px',
            'border-color': '#FFFFFF'
          }
        },
        {
          selector: 'node[isMain = "true"]',
          style: {
            'background-color': '#EF4444',
            'width': '80px',
            'height': '80px',
            'font-size': '14px'
          }
        },
        {
          selector: 'edge',
          style: {
            'width': '2px',
            'line-color': '#E5E7EB',
            'curve-style': 'bezier',
            'target-arrow-color': '#E5E7EB',
            'target-arrow-shape': 'triangle'
          }
        }
      ],
      layout: {
        name: 'cose',
        animate: true,
        animationDuration: 1000,
        nodeDimensionsIncludeLabels: true,
        fit: true,
        padding: 50
      }
    })

    // Add event listeners
    cy.on('mouseover', 'node', function() {
      this.style('background-color', '#10B981')
    })

    cy.on('mouseout', 'node', function() {
      const isMain = this.data('isMain')
      this.style('background-color', isMain ? '#EF4444' : '#3B82F6')
    })

  } catch (error) {
    console.error('Error loading co-author graph:', error)
  } finally {
    loading.value = false
  }
})

onUnmounted(() => {
  if (cy) {
    cy.destroy()
  }
})
</script>

<style scoped>
.coauthor-graph {
  margin-top: 20px;
}

.coauthor-graph h3 {
  margin-bottom: 20px;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.graph-container {
  position: relative;
  height: 400px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
}

.graph-element {
  width: 100%;
  height: 100%;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.loading-text {
  color: var(--text-secondary);
  font-size: 16px;
}

@media (max-width: 768px) {
  .graph-container {
    height: 300px;
  }
}
</style> 