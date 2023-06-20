import json
import uuid

from channels.generic.websocket import WebsocketConsumer
import paho.mqtt.client as mqtt
from django.conf import settings

from app_socket.service import convert_status_to_json
from lockControl.models import Status
from lockControl.utils import danger_check_status


class StatusSocket(WebsocketConsumer):
    _mqtt_client: mqtt.Client
    session: str

    def _on_mqtt_receive(self, client, userdata, msg: mqtt.MQTTMessage):
        print("received from mqtt")
        message = msg.payload.decode("utf-8")
        status = convert_status_to_json(message)
        status_obj = Status.objects.latest("update_at")
        status_obj.lock = status.get("lock")
        status_obj.door = status.get("door")
        status_obj.save()
        if danger_check_status(status):
            Status.objects.create(lock=status.get("lock"), door=status.get("door"))
            status["notice"] = settings.SERCURITY_ALERT
        self.send(text_data=json.dumps(status))

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

class NoticeSocket(WebsocketConsumer):
    def _on_mqtt_receive(self, client, userdata, msg: mqtt.MQTTMessage):
        pass
    def test(self, *args, **kwargs):
        print("test")

    def connect(self):
        print("Connected to websocket")

        self._mqtt_client = mqtt.Client()
        self._mqtt_client.on_connect = self.test()
        self._mqtt_client.on_message = self._on_mqtt_receive

        self._mqtt_client.connect("localhost", settings.MQTT_PORT, 60)
        self._mqtt_client.loop_start()
        self.session = uuid.uuid1().__str__()
        self.accept()

    def receive(self, text_data=None, bytes_data=None):
        print("Received text")
        print(self.session)
        self.send(text_data="Hello")

