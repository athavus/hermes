<template>
    <div>
        <!-- Grid de Telemetria -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8 text-gray-700">
            <!-- WiFi Status -->
            <div class="bg-gray-50 p-4 rounded-lg border border-gray-100 transition-all hover:shadow-sm">
                <div class="flex items-center gap-3 mb-2">
                    <div class="p-2 rounded-lg">
                        <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0" />
                        </svg>
                    </div>
                    <h4 class="font-semibold text-gray-600">Conectividade</h4>
                </div>
                <p class="text-xl font-bold" :class="deviceDetails.wifi_status === 'online' ? 'text-green-600' : 'text-red-500'">
                    {{ deviceDetails.wifi_status === 'online' ? 'Online' : 'Offline' }}
                </p>
            </div>

            <!-- Memory Consumption -->
            <div class="bg-gray-50 p-4 rounded-lg border border-gray-100 transition-all hover:shadow-sm">
                <div class="flex items-center gap-3 mb-2">
                    <div class="p-2 rounded-lg">
                        <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                    </div>
                    <h4 class="font-semibold text-gray-600">RAM (Total/Uso)</h4>
                </div>
                <p class="text-xl font-bold text-gray-800">{{ deviceDetails.mem_usage || '0 MB' }}</p>
            </div>

            <!-- Temperature -->
            <div class="bg-gray-50 p-4 rounded-lg border border-gray-100 transition-all hover:shadow-sm">
                <div class="flex items-center gap-3 mb-2">
                    <div class="p-2 rounded-lg">
                        <svg class="w-5 h-5 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                    </div>
                    <h4 class="font-semibold text-gray-600">Temperatura CPU</h4>
                </div>
                <p class="text-xl font-bold text-gray-800">{{ deviceDetails.cpu_temp || '0°C' }}</p>
            </div>

            <!-- GPU Status -->
            <div class="bg-gray-50 p-4 rounded-lg border border-gray-100 transition-all hover:shadow-sm">
                <div class="flex items-center gap-3 mb-2">
                    <div class="p-2 rounded-lg">
                        <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                        </svg>
                    </div>
                    <h4 class="font-semibold text-gray-600">GPU (Carga/Temp)</h4>
                </div>
                <p class="text-xl font-bold text-gray-800">
                    {{ formatCpuPercent(deviceDetails.gpu_load) }}% / {{ deviceDetails.gpu_temp || 'N/A' }}
                </p>
            </div>
        </div>

        <!-- Estatísticas de Rede -->
        <div class="grid grid-cols-1 gap-6 mb-8">
            <div class="bg-white border border-gray-200 p-4 rounded-lg">
                <div class="flex justify-between items-center mb-4">
                    <h4 class="font-bold text-gray-700 flex items-center gap-2">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                        Tráfego de Rede
                    </h4>
                    <div class="text-xs text-gray-400 italic">
                        Última sincronização: {{ formatDate(deviceDetails.last_update) }}
                    </div>
                </div>
                <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
                    <div class="p-3 rounded-lg">
                        <span class="text-xs text-zinc-950 font-bold block uppercase tracking-wider">Bytes Enviados</span>
                        <span class="text-lg font-mono font-bold text-blue-800">{{ formatBytes(deviceDetails.net_bytes_sent) }}</span>
                    </div>
                    <div class="p-3 rounded-lg">
                        <span class="text-xs text-zinc-950 font-bold block uppercase tracking-wider">Bytes Recebidos</span>
                        <span class="text-lg font-mono font-bold text-green-800">{{ formatBytes(deviceDetails.net_bytes_recv) }}</span>
                    </div>
                    <div class="lg:col-span-2 p-3 rounded-lg flex flex-wrap items-center gap-2">
                        <span class="text-xs text-gray-500 font-bold block uppercase w-full mb-1">Interfaces Ativas</span>
                        <span v-for="iface in deviceDetails.net_ifaces" :key="iface" class="px-2 py-0.5 bg-white text-gray-600 text-xs rounded border border-gray-200 font-mono">
                            {{ iface }}
                        </span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Gráficos em Tempo Real -->
        <div class="mt-12 bg-white rounded-xl border border-gray-100 p-6 shadow-sm">
            <h3 class="text-xl font-bold mb-6 text-gray-800 flex items-center gap-3">
                Monitoramento de Performance
            </h3>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <!-- Gráfico CPU -->
                <div class="chart-card group">
                    <div class="flex justify-between items-center mb-4 pb-2 border-b border-gray-50">
                        <h4 class="font-bold text-gray-600">Uso de CPU</h4>
                        <span class="px-3 py-1 text-blue-700 font-mono font-bold rounded-lg border border-blue-100">
                            {{ formatCpuPercent(deviceDetails.cpu_percent) }}%
                        </span>
                    </div>
                    <div class="relative h-[220px]">
                        <canvas ref="cpuCanvas"></canvas>
                    </div>
                </div>

                <!-- Gráfico GPU -->
                <div class="chart-card group">
                    <div class="flex justify-between items-center mb-4 pb-2 border-b border-gray-50">
                        <h4 class="font-bold text-gray-600">Uso de GPU</h4>
                        <span class="px-3 py-1 text-green-700 font-mono font-bold rounded-lg border border-green-100">
                            {{ formatCpuPercent(deviceDetails.gpu_load) }}%
                        </span>
                    </div>
                    <div class="relative h-[220px]">
                        <canvas ref="gpuCanvas"></canvas>
                    </div>
                </div>

                <!-- Gráfico RAM -->
                <div class="chart-card group">
                    <div class="flex justify-between items-center mb-4 pb-2 border-b border-gray-50">
                        <h4 class="font-bold text-gray-600">Uso de RAM</h4>
                        <span class="px-3 py-1 text-purple-700 font-mono font-bold rounded-lg border border-purple-100">
                            {{ formatMemPercent(deviceDetails.mem_percent) }}%
                        </span>
                    </div>
                    <div class="relative h-[220px]">
                        <canvas ref="ramCanvas"></canvas>
                    </div>
                </div>

                <!-- Gráfico Temperatura CPU -->
                <div class="chart-card group">
                    <div class="flex justify-between items-center mb-4 pb-2 border-b border-gray-50">
                        <h4 class="font-bold text-gray-600">Temperatura CPU</h4>
                        <span class="px-3 py-1 text-orange-700 font-mono font-bold rounded-lg border border-orange-100">
                            {{ deviceDetails.cpu_temp || '0°C' }}
                        </span>
                    </div>
                    <div class="relative h-[220px]">
                        <canvas ref="tempCanvas"></canvas>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { ref, onMounted, watch, onBeforeUnmount, markRaw, toRaw } from 'vue';
import Chart from 'chart.js/auto';
import { deviceService } from '../services/raspberryApi';

export default {
    name: 'DeviceStatusGrid',
    props: {
        deviceDetails: {
            type: Object,
            required: true
        }
    },
    setup(props) {
        const cpuCanvas = ref(null);
        const gpuCanvas = ref(null);
        const ramCanvas = ref(null);
        const tempCanvas = ref(null);

        let cpuChart = null;
        let gpuChart = null;
        let ramChart = null;
        let tempChart = null;

        const maxPoints = 30;
        const labels = Array.from({ length: maxPoints }, (_, i) => '');
        const cpuData = ref(Array(maxPoints).fill(0));
        const gpuData = ref(Array(maxPoints).fill(0));
        const ramData = ref(Array(maxPoints).fill(0));
        const tempData = ref(Array(maxPoints).fill(0));

        const formatDate = (dateString) => {
            if (!dateString) return '--:--:--';
            return new Date(dateString).toLocaleTimeString();
        };

        const formatCpuPercent = (val) => {
            return typeof val === 'number' ? val.toFixed(1) : '0.0';
        };

        const formatMemPercent = (val) => {
            return typeof val === 'number' ? val.toFixed(1) : '0.0';
        };

        const formatBytes = (bytes) => {
            if (!bytes || bytes === 0) return '0 B';
            const k = 1024;
            const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        };

        const createChart = (ctx, label, color, initialData, min, max, unit) => {
            if (!ctx) return null;
            const chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: label,
                        data: [...initialData],
                        borderColor: color,
                        backgroundColor: (context) => {
                            const chart = context.chart;
                            const {ctx, chartArea} = chart;
                            if (!chartArea) return null;
                            const gradient = ctx.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);
                            gradient.addColorStop(0, color.replace('1)', '0)'));
                            gradient.addColorStop(1, color.replace('1)', '0.2)'));
                            return gradient;
                        },
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                            callbacks: {
                                label: (context) => `${context.parsed.y}${unit}`
                            }
                        }
                    },
                    scales: {
                        x: { display: false },
                        y: {
                            min: min,
                            max: max,
                            ticks: {
                                color: '#94a3b8',
                                font: { size: 10 },
                                callback: (value) => `${value}${unit}`
                            },
                            grid: {
                                color: '#f1f5f9'
                            }
                        }
                    },
                    animation: { duration: 0 }
                }
            });
            return markRaw(chart);
        };

        const updateData = (history) => {
            if (!history || history.length === 0) return;

            const last = [...history].reverse().slice(-maxPoints);

            cpuData.value = last.map(h => h.cpu_percent || 0);
            gpuData.value = last.map(h => h.gpu_load || 0);
            ramData.value = last.map(h => h.mem_percent || 0);
            tempData.value = last.map(h => {
                const tempStr = String(h.cpu_temp || '0');
                if (tempStr === 'N/A') return 0;
                return parseFloat(tempStr.replace('°C', '')) || 0;
            });

            if (cpuChart) {
                cpuChart.data.datasets[0].data = [...cpuData.value];
                cpuChart.update('none');
            }
            if (gpuChart) {
                gpuChart.data.datasets[0].data = [...gpuData.value];
                gpuChart.update('none');
            }
            if (ramChart) {
                ramChart.data.datasets[0].data = [...ramData.value];
                ramChart.update('none');
            }
            if (tempChart) {
                tempChart.data.datasets[0].data = [...tempData.value];
                tempChart.update('none');
            }
        };

        const loadHistory = async () => {
            try {
                const history = await deviceService.getDeviceHistory(props.deviceDetails.raspberry_id);
                updateData(history);
            } catch (err) {
                console.error('Falha ao obter histórico:', err);
            }
        };

        watch(() => props.deviceDetails.last_update, () => {
             cpuData.value.push(props.deviceDetails.cpu_percent || 0);
             cpuData.value.shift();

             gpuData.value.push(props.deviceDetails.gpu_load || 0);
             gpuData.value.shift();

             ramData.value.push(props.deviceDetails.mem_percent || 0);
             ramData.value.shift();

             const tempStr = String(props.deviceDetails.cpu_temp || '0');
             const t = tempStr === 'N/A' ? 0 : (parseFloat(tempStr.replace('°C', '')) || 0);
             tempData.value.push(t);
             tempData.value.shift();

             if (cpuChart) {
                cpuChart.data.datasets[0].data = [...cpuData.value];
                cpuChart.update('none');
             }
             if (gpuChart) {
                gpuChart.data.datasets[0].data = [...gpuData.value];
                gpuChart.update('none');
             }
             if (ramChart) {
                ramChart.data.datasets[0].data = [...ramData.value];
                ramChart.update('none');
             }
             if (tempChart) {
                tempChart.data.datasets[0].data = [...tempData.value];
                tempChart.update('none');
             }
        });

        watch(() => props.deviceDetails.raspberry_id, () => {
            loadHistory();
        }, { immediate: true });

        onMounted(() => {
            cpuChart = createChart(cpuCanvas.value, 'CPU', 'rgba(37, 99, 235, 1)', cpuData.value, 0, 100, '%');
            gpuChart = createChart(gpuCanvas.value, 'GPU', 'rgba(22, 163, 74, 1)', gpuData.value, 0, 100, '%');
            ramChart = createChart(ramCanvas.value, 'RAM', 'rgba(147, 51, 234, 1)', ramData.value, 0, 100, '%');
            tempChart = createChart(tempCanvas.value, 'Temp', 'rgba(234, 88, 12, 1)', tempData.value, 0, 100, '°C');
        });

        onBeforeUnmount(() => {
            if (cpuChart) cpuChart.destroy();
            if (gpuChart) gpuChart.destroy();
            if (ramChart) ramChart.destroy();
            if (tempChart) tempChart.destroy();
        });

        return {
            cpuCanvas,
            gpuCanvas,
            ramCanvas,
            tempCanvas,
            formatDate,
            formatCpuPercent,
            formatMemPercent,
            formatBytes
        };
    }
};
</script>

<style scoped>
.chart-card {
    @apply bg-white p-2 transition-all;
}
canvas {
    width: 100% !important;
    height: 100% !important;
}
</style>
