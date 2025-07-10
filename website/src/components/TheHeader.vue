<template>
  <header class="header">
    <div class="container">
      <router-link to="/" class="logo">
        <h1>ATIP</h1>
      </router-link>
    </div>
  </header>
</template>

<script setup>
// No additional logic needed
</script>

<style scoped>
.header {
  background-color: var(--surface);
  border-bottom: 1px solid var(--border-color);
  padding: 16px 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.logo {
  text-decoration: none;
  color: var(--text-primary);
}

.logo h1 {
  font-size: 24px;
  font-weight: 700;
  color: var(--primary);
  margin: 0;
}

@media (max-width: 768px) {
  .logo h1 {
    font-size: 20px;
  }
}
</style> 