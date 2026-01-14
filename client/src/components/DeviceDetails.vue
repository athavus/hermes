<template>
  <section
    v-if="deviceDetails"
    class="col-span-3 bg-white rounded-lg shadow p-6 overflow-auto max-h-[calc(100vh-128px)]"
  >
    <h2 class="text-lg font-semibold mb-4">Monitoramento do Dispositivo: {{ deviceId }}</h2>

    <DeviceStatusGrid 
      :device-details="deviceDetails" 
    />
  </section>
</template>

<script>
import DeviceStatusGrid from './DeviceStatusGrid.vue';

export default {
  name: 'DeviceDetails',
  components: {
    DeviceStatusGrid
  },
  props: {
    deviceDetails: {
      type: Object,
      default: null
    },
    deviceId: {
      type: [String, Number],
      default: null
    },
    loading: {
      type: Boolean,
      default: false
    }
  }
};
</script>

