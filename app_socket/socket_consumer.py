import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings

from lockControl.models import Status
from lockControl.utils import danger_check_status
from smartLock.utils import RedisSingleton


class StatusConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.redis = None

    async def connect(self):
        self.redis = RedisSingleton().get_instance()
        await self.accept()
        redis_pubsub = self.redis.pubsub()
        await redis_pubsub.psubscribe('__keyspace@0__:status')
        while redis_pubsub.listen():
            value = await self.redis.get("status")
            # Xử lý message ở đây
            if value:
                await self.send(text_data=value.decode("utf-8"))
                value_dict = json.loads(value.decode("utf-8"))
                status = await sync_to_async(Status.objects.get)(pk=2)
                status.lock = value_dict['lock']
                status.door = value_dict['door']
                await sync_to_async(status.save)()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data=None, bytes_data=None):
        keys = self.redis.keys('*')
        values = self.redis.mget(keys)

        # Tạo một từ điển để lưu trữ cặp khóa-giá trị
        data = dict(zip(keys, values))

        # In ra danh sách khóa và giá trị
        for key, value in data.items():
            print(f"Key: {key.decode()}, Value: {value.decode()}")
