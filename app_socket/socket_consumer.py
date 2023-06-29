import aioredis
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer

import redis.asyncio as redis
from smartLock.utils import RedisSingleton

class StatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.redis = RedisSingleton().get_instance()
        await self.accept()
        redis_pubsub = self.redis.pubsub()
        await redis_pubsub.psubscribe('__keyspace@0__:status')
        async for message in redis_pubsub.listen():
            value = await self.redis.get("status")
            # Xử lý message ở đây
            await self.send(text_data=value.decode("utf-8"))

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
