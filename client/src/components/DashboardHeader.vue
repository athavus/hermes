<template>
  <header class="sticky top-0 z-50 bg-white border-b border-gray-200 shadow-sm">
    <div class="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
      <h1 class="text-xl font-semibold text-gray-900">Grieves</h1>
      <div class="flex items-center gap-4">
        <button
          @click="$emit('export-db')"
          class="px-3 py-1 text-sm bg-blue-100 hover:bg-blue-200 rounded-md"
        >
          Exportar DB
        </button>
      </div>
    </div>
  </header>
</template>

<script>
export default {
  name: 'DashboardHeader',
  emits: ['refresh', 'export-db']
};
</script>
