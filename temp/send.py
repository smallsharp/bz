#!/usr/bin/env python
import pika

auth = pika.PlainCredentials('root', 'root')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='127.0.0.1', port=8000))
channel = connection.channel()

channel.queue_declare(queue='TEST01')

channel.basic_publish(exchange='',
                      routing_key='TEST01',
                      body='Hello World!')
print(" [x] Sent 'Hello World!'")
connection.close()
