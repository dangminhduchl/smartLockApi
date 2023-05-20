import json

import paho.mqtt.client as mqtt
from django.conf import settings
from ..models import Status

class MQTTManager:
    def __init__(self):
        self.client_receive = mqtt.Client()

        self.client_receive.on_message = self.on_message_receive

        self.client_send = mqtt.Client()


        self.client_receive.connect(settings.MQTT_HOST, settings.MQTT_PORT, 60)

        self.client_receive.loop_start()

        self.client_receive.subscribe(settings.MQTT_TOPIC_STATUS)

        self.client_send.connect(settings.MQTT_HOST, settings.MQTT_PORT, 60)

    def on_message_receive(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode('utf-8')
        print('Received message:', payload)

        if topic == settings.MQTT_TOPIC_STATUS:
            try:
                status_data = json.loads(payload)
                lock = int(status_data.get('lock'))
                door = int(status_data.get('door'))

                status = Status(lock=lock, door=door)
                status.save()

                if lock == 1 and door == 0:
                    self.send_alert_to_user()

            except json.JSONDecodeError:
                print('Invalid JSON data received')

    def send_control_to_esp8266(self, lock,door):
        control_data = {'lock': lock,'door':door}
        payload = json.dumps(control_data)
        self.client_send.publish(settings.MQTT_TOPIC_CONTROL, payload)
        self.client_send.publish(settings.MQTT_TOPIC_STATUS, payload)

    def send_alert_to_user(self):
        # Implement your alert mechanism here
        pass