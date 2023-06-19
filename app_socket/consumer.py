import uuid

from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
import paho.mqtt.client as mqtt
from django.conf import settings


class TestSocket(WebsocketConsumer):
    _mqtt_client: mqtt.Client
    session: str
    def _on_mqtt_receive(self, client, userdata, msg: mqtt.MQTTMessage):
        print("received from mqtt")
        self.send(text_data=f"Data from mqtt {msg.payload}")
    def test(self, *args, **kwargs):
        print("test")

    def connect(self):
        print("Connected to websocket")

        self._mqtt_client = mqtt.Client()
        self._mqtt_client.on_connect = self.test()
        self._mqtt_client.on_message = self._on_mqtt_receive

        self._mqtt_client.connect("localhost", settings.MQTT_PORT, 60)
        self._mqtt_client.subscribe(settings.MQTT_TOPIC_STATUS)
        self._mqtt_client.loop_start()
        self.session = uuid.uuid1().__str__()
        self.accept()
        self.send(text_data="Hello, world!")
        self.send(text_data=self.session)

    def receive(self, text_data=None, bytes_data=None):
        print("Received text")
        print(self.session)
        self.send(text_data="Hello")
