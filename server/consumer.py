import pika
import json
import threading
from shared import received_messages
from database import SessionLocal, DeviceStatus, DeviceStatusHistory
from datetime import datetime

def process_raspberry_data(data):
    """Processa dados de telemetria das Raspberries e salva no banco"""
    db = SessionLocal()
    try:
        raspberry_id = data.get("id")
        if not raspberry_id:
            return

        # 1. Atualizar status atual do dispositivo
        device = db.query(DeviceStatus).filter(
            DeviceStatus.raspberry_id == raspberry_id
        ).first()

        status_fields = {
            "wifi_status": data.get("wifi_status", "unknown"),
            "mem_usage": data.get("mem_usage", "0 MB"),
            "mem_percent": data.get("mem_percent", 0.0),
            "cpu_temp": data.get("cpu_temp", "N/A"),
            "cpu_percent": data.get("cpu_percent", 0.0),
            "spi_buses": data.get("spi_buses", 0),
            "i2c_buses": data.get("i2c_buses", 0),
            "usb_devices_count": data.get("usb_devices_count", 0),
            "net_bytes_sent": data.get("net_bytes_sent", 0),
            "net_bytes_recv": data.get("net_bytes_recv", 0),
            "net_ifaces": json.dumps(data.get("net_ifaces", [])),
            "gpu_temp": data.get("gpu_temp", "N/A"),
            "gpu_load": data.get("gpu_load", 0.0),
            "last_update": datetime.utcnow()
        }

        if device:
            for key, value in status_fields.items():
                setattr(device, key, value)
        else:
            device = DeviceStatus(raspberry_id=raspberry_id, **status_fields)
            db.add(device)

        # 2. Salvar no histórico para gráficos
        history = DeviceStatusHistory(
            raspberry_id=raspberry_id,
            wifi_status=status_fields["wifi_status"],
            mem_usage=status_fields["mem_usage"],
            mem_percent=status_fields["mem_percent"],
            cpu_temp=status_fields["cpu_temp"],
            cpu_percent=status_fields["cpu_percent"],
            spi_buses=status_fields["spi_buses"],
            i2c_buses=status_fields["i2c_buses"],
            usb_devices_count=status_fields["usb_devices_count"],
            net_bytes_sent=status_fields["net_bytes_sent"],
            net_bytes_recv=status_fields["net_bytes_recv"],
            net_ifaces=status_fields["net_ifaces"],
            timestamp=datetime.utcnow()
        )
        db.add(history)

        db.commit()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Telemetria salva para {raspberry_id}")

    except Exception as e:
        print(f"Erro ao processar dados de telemetria: {e}")
        db.rollback()
    finally:
        db.close()

def rabbit_consumer():
    """Consumer do RabbitMQ que processa mensagens das Raspberries"""
    try:
        credentials = pika.PlainCredentials('athavus', '1234')
        connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost', 5672, '/', credentials, heartbeat=600)
        )
        channel = connection.channel()
        channel.queue_declare(queue='rasp_data', durable=True)

        def callback(ch, method, properties, body):
            try:
                data = json.loads(body)
                print(f"Recebido: {data}")
                received_messages.append(data)

                # Processar e salvar no banco de dados
                process_raspberry_data(data)

            except json.JSONDecodeError as e:
                print(f"Erro ao decodificar JSON: {e}")
            except Exception as e:
                print(f"Erro no callback: {e}")

        channel.basic_consume(
            queue='rasp_data',
            on_message_callback=callback,
            auto_ack=True
        )

        print("RabbitMQ consumer iniciado")
        channel.start_consuming()

    except Exception as e:
        print(f"Erro ao conectar no RabbitMQ: {e}")

def start_consumer_thread():
    """Inicia o consumer em uma thread separada"""
    t = threading.Thread(target=rabbit_consumer, daemon=True)
    t.start()
    print("Thread do consumer iniciada")

