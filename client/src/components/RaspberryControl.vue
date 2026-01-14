<template>
    <div class="min-h-screen bg-gray-50">
        <DashboardHeader
            :is-online="isOnline"
            @refresh="fetchAllData"
            @export-db="downloadDb"
        />

        <main
            class="max-w-7xl mx-auto p-6 grid grid-cols-1 lg:grid-cols-4 gap-6"
        >
            <DeviceSelector
                :devices="devices"
                :selected-device-id="selectedDeviceId"
                @select-device="selectDevice"
            />

            <DeviceDetails
                :device-details="selectedDeviceDetails"
                :device-id="selectedDeviceId"
                :loading="loading"
            />

            <LoadingOverlay :loading="loading" />
            <ErrorBanner :error="error" @dismiss="error = null" />
        </main>
    </div>
</template>

<script>
import { ref, computed, onMounted, onBeforeUnmount } from "vue";
import {
    deviceService,
    realtimeService,
    exportService,
} from "../services/raspberryApi.js";
import DashboardHeader from "./DashboardHeader.vue";
import DeviceSelector from "./DeviceSelector.vue";
import DeviceDetails from "./DeviceDetails.vue";
import LoadingOverlay from "./LoadingOverlay.vue";
import ErrorBanner from "./ErrorBanner.vue";

export default {
    name: "RaspberryControl",
    components: {
        DashboardHeader,
        DeviceSelector,
        DeviceDetails,
        LoadingOverlay,
        ErrorBanner,
    },
    setup() {
        const loading = ref(false);
        const error = ref(null);
        const isOnline = ref(true);

        const devices = ref([]);
        const selectedDeviceId = ref(null);
        const selectedDeviceDetails = ref(null);
        const realtimeMessages = ref([]);

        let refreshTimer = null;

        const fetchDevices = async () => {
            try {
                const data = await deviceService.getAllDevices();
                devices.value = data;
                if (!selectedDeviceId.value && data.length > 0) {
                    selectedDeviceId.value = data[0].raspberry_id;
                }
            } catch (err) {
                error.value = "Erro ao buscar dispositivos.";
                isOnline.value = false;
            }
        };

        const fetchDeviceDetails = async (id) => {
            if (!id) return;
            try {
                const details = await deviceService.getDevice(id);
                selectedDeviceDetails.value = details;
                isOnline.value = true;
            } catch {
                error.value = "Erro ao buscar detalhes do dispositivo.";
                selectedDeviceDetails.value = null;
                isOnline.value = false;
            }
        };

        const fetchRealtimeMessages = async () => {
            try {
                const data = await realtimeService.getData(50);
                realtimeMessages.value = data.data || [];
                isOnline.value = true;
            } catch {
                error.value = "Erro ao buscar mensagens em tempo real.";
                isOnline.value = false;
            }
        };

        const fetchAllData = async () => {
            loading.value = true;
            error.value = null;
            try {
                await fetchDevices();
                if (selectedDeviceId.value) {
                    await fetchDeviceDetails(selectedDeviceId.value);
                }
                await fetchRealtimeMessages();
                isOnline.value = true;
            } catch {
                error.value = "Erro ao carregar dados da API.";
                isOnline.value = false;
            }
            loading.value = false;
        };

        const downloadDb = async () => {
            try {
                const blob = await exportService.downloadDatabaseZip();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = "raspberry_telemetry_export.zip";
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);
            } catch (e) {
                console.error(e);
                error.value = "Falha ao exportar banco";
            }
        };

        const selectDevice = async (id) => {
            if (id === selectedDeviceId.value) return;
            selectedDeviceId.value = id;
            loading.value = true;
            error.value = null;
            await fetchDeviceDetails(id);
            loading.value = false;
        };

        const filteredRealtimeMessages = computed(() => {
            return realtimeMessages.value.filter(
                (msg) => (msg.raspberry_id || msg.id) == selectedDeviceId.value,
            );
        });

        onMounted(() => {
            fetchAllData();

            refreshTimer = setInterval(() => {
                if (selectedDeviceId.value) {
                    fetchDeviceDetails(selectedDeviceId.value);
                    fetchRealtimeMessages();
                }
            }, 1200);
        });

        onBeforeUnmount(() => {
            if (refreshTimer) clearInterval(refreshTimer);
        });

        return {
            loading,
            error,
            isOnline,
            devices,
            selectedDeviceId,
            selectedDeviceDetails,
            realtimeMessages,
            filteredRealtimeMessages,
            fetchAllData,
            selectDevice,
            downloadDb,
        };
    },
};
</script>

<style scoped>
section {
    scrollbar-width: thin;
    scrollbar-color: rgba(107, 114, 128, 0.5) transparent;
}

section::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

section::-webkit-scrollbar-thumb {
    background-color: rgba(107, 114, 128, 0.5);
    border-radius: 4px;
}

button {
    transition: background-color 0.3s ease;
}

.chart-container {
    position: relative;
    height: 250px;
    width: 100%;
}
</style>

<style scoped>
section {
    scrollbar-width: thin;
    scrollbar-color: rgba(107, 114, 128, 0.5) transparent;
}

section::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

section::-webkit-scrollbar-thumb {
    background-color: rgba(107, 114, 128, 0.5);
    border-radius: 4px;
}

button {
    transition: background-color 0.3s ease;
}

.chart-container {
    position: relative;
    height: 250px;
    width: 100%;
}
</style>
