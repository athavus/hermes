import json
import socket
import time
import psutil
import pika
from glob import glob
import os

def get_system_info():
    """Coleta informações do sistema para telemetria, otimizado para PC e RPi"""
    try:
        mem = psutil.virtual_memory()
        mem_usage = f"{int(mem.used / (1024**2))} MB"
        mem_percent = float(mem.percent)
        cpu_percent = psutil.cpu_percent(interval=None)

        cpu_temp = "N/A"
        try:
            # 1. Tenta via psutil (mais portátil)
            temps = psutil.sensors_temperatures()
            if temps:
                # Procura por 'k10temp' (AMD), 'coretemp' (Intel), 'cpu-thermal' (RPi)
                for name, entries in temps.items():
                    if any(x in name.lower() for x in ['cpu', 'thermal', 'soc', 'core', 'k10temp']):
                        if entries:
                            cpu_temp = f"{entries[0].current:.1f}°C"
                            break
            
            # 2. Fallback para hwmon (comum em Linux PC)
            if cpu_temp == "N/A":
                hwmon_paths = glob("/sys/class/hwmon/hwmon*/")
                for path in hwmon_paths:
                    try:
                        with open(os.path.join(path, "name"), "r") as f:
                            name = f.read().strip()
                        if any(x in name.lower() for x in ['k10temp', 'coretemp', 'cpu']):
                            temp_file = os.path.join(path, "temp1_input")
                            if os.path.exists(temp_file):
                                with open(temp_file, "r") as f:
                                    temp = float(f.read()) / 1000.0
                                    cpu_temp = f"{temp:.1f}°C"
                                    break
                    except:
                        continue

            # 3. Fallback para thermal_zone (comum em RPi)
            if cpu_temp == "N/A":
                for i in range(5):
                    path = f"/sys/class/thermal/thermal_zone{i}/temp"
                    if os.path.exists(path):
                        with open(path, "r") as f:
                            temp = float(f.read()) / 1000.0
                            cpu_temp = f"{temp:.1f}°C"
                            break
        except:
            pass

        # Identifica interfaces ativas
        net_stats = psutil.net_if_stats()
        wifi_status = "offline"
        # Tenta wlan0 (RPi) ou wlo1 (Laptop/PC)
        for iface in ["wlan0", "wlo1", "wlx"]:
            if any(iface in name for name in net_stats) and net_stats.get(next(name for name in net_stats if iface in name)).isup:
                wifi_status = "online"
                break

        net_io = psutil.net_io_counters()
        net_bytes_sent = net_io.bytes_sent
        net_bytes_recv = net_io.bytes_recv

        net_ifaces = [
            iface
            for iface in psutil.net_if_addrs()
            if iface in net_stats and net_stats[iface].isup
        ]

        gpu_load = 0.0
        gpu_temp = "N/A"
        try:
            # Tenta encontrar a GPU (ajustado para o card1 do seu PC)
            gpu_busy_path = "/sys/class/drm/card1/device/gpu_busy_percent"
            if os.path.exists(gpu_busy_path):
                with open(gpu_busy_path, "r") as f:
                    gpu_load = float(f.read().strip())
            
            # Tenta temperatura da GPU via hwmon (associada ao amdgpu no card1)
            # No seu sistema parece estar no hwmon0 ou hwmon1
            hwmon_paths = glob("/sys/class/hwmon/hwmon*/")
            for path in hwmon_paths:
                try:
                    with open(os.path.join(path, "name"), "r") as f:
                        name = f.read().strip()
                    if name == "amdgpu":
                        temp_file = os.path.join(path, "temp1_input")
                        if os.path.exists(temp_file):
                            with open(temp_file, "r") as f:
                                gpu_temp = f"{float(f.read()) / 1000.0:.1f}°C"
                                break
                except:
                    continue
        except:
            pass

        return {
            "mem_usage": mem_usage,
            "mem_percent": mem_percent,
            "cpu_temp": cpu_temp,
            "cpu_percent": cpu_percent,
            "gpu_temp": gpu_temp,
            "gpu_load": gpu_load,
            "wifi_status": wifi_status,
            "net_bytes_sent": net_bytes_sent,
            "net_bytes_recv": net_bytes_recv,
            "net_ifaces": net_ifaces,
        }

    except Exception as e:
        print(f"Erro ao coletar info do sistema: {e}")
        return {}

def start_telemetry(rabbitmq_host="192.168.15.3", user="athavus", password="1234"):
    raspberry_id = socket.gethostname()
    print(f"Iniciando telemetria para: {raspberry_id}")
    
    while True:
        try:
            credentials = pika.PlainCredentials(user, password)
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=rabbitmq_host, 
                    port=5672, 
                    virtual_host="/", 
                    credentials=credentials, 
                    heartbeat=600
                )
            )
            channel = connection.channel()
            channel.queue_declare(queue="rasp_data", durable=True)

            while True:
                sys_info = get_system_info()
                if sys_info:
                    data = {
                        "id": raspberry_id,
                        **sys_info,
                        "timestamp": time.time()
                    }

                    channel.basic_publish(
                        exchange="",
                        routing_key="rasp_data",
                        body=json.dumps(data),
                        properties=pika.BasicProperties(
                            delivery_mode=2,
                        ),
                    )
                    # Printa a mensagem inteira como solicitado
                    print(f"Recebido: {data}")
                
                time.sleep(1)

        except KeyboardInterrupt:
            print("\nEncerrando telemetria...")
            if 'connection' in locals() and connection.is_open:
                connection.close()
            break
        except Exception as e:
            print(f"Erro na telemetria: {e}. Tentando reconectar...")
            time.sleep(5)

if __name__ == "__main__":
    start_telemetry()
