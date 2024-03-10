import pika
import json


def send_metric(action, data):
    connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq", 5672))
    channel = connection.channel()
    channel.queue_declare(queue="metrics_queue")

    message = json.dumps({"action": action, **data})

    channel.basic_publish(exchange="", routing_key="metrics_queue", body=message)
    print(" [x] Sent metric to 'metrics_queue'")
    connection.close()
