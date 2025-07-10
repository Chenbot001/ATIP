import Papa from 'papaparse'

// Cache for parsed data
const dataCache = {}

// Helper function to fetch and parse CSV
async function fetchAndParseCSV(filename) {
  if (dataCache[filename]) {
    return dataCache[filename]
  }

  try {
    const response = await fetch(`/data/${filename}`)
    if (!response.ok) {
      throw new Error(`Failed to fetch ${filename}: ${response.status}`)
    }
    
    const csvText = await response.text()
    const result = Papa.parse(csvText, {
      header: true,
      skipEmptyLines: true
    })
    
    dataCache[filename] = result.data
    return result.data
  } catch (error) {
    console.error(`Error loading ${filename}:`, error)
    return []
  }
}

// Data access functions
export async function getAuthors() {
  return await fetchAndParseCSV('author_profiles.csv')
}

export async function getPapers() {
  return await fetchAndParseCSV('paper_info.csv')
}

export async function getAuthorships() {
  return await fetchAndParseCSV('authorships.csv')
}

export async function getTop100PQI() {
  return await fetchAndParseCSV('top100_pqi.csv')
}

export async function getTop100ANCI() {
  return await fetchAndParseCSV('top100_anci.csv')
}

export async function getTop100ACCEL() {
  return await fetchAndParseCSV('top100_accel.csv')
}

export async function getAuthorById(authorId) {
  const authors = await getAuthors()
  return authors.find(author => author.id === authorId || author.author_id === authorId)
}

export async function getPapersByAuthor(authorId) {
  const authorships = await getAuthorships()
  const papers = await getPapers()
  
  const authorPapers = authorships.filter(authorship => 
    authorship.author_id === authorId || authorship.id === authorId
  )
  
  return authorPapers.map(authorship => {
    const paper = papers.find(p => p.paper_id === authorship.paper_id)
    return {
      ...authorship,
      ...paper
    }
  })
}

export async function getCoauthors(authorId) {
  const authorships = await getAuthorships()
  const authors = await getAuthors()
  
  // Get all papers by this author
  const authorPapers = authorships.filter(authorship => 
    authorship.author_id === authorId || authorship.id === authorId
  )
  
  // Get all coauthors from these papers
  const coauthorIds = new Set()
  authorPapers.forEach(authorship => {
    const paperAuthorships = authorships.filter(a => a.paper_id === authorship.paper_id)
    paperAuthorships.forEach(a => {
      if (a.author_id !== authorId && a.id !== authorId) {
        coauthorIds.add(a.author_id || a.id)
      }
    })
  })
  
  return Array.from(coauthorIds).map(id => {
    return authors.find(author => author.id === id || author.author_id === id)
  }).filter(Boolean)
} 