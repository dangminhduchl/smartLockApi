import redis.asyncio as redis_async
import redis


class RedisSingleton:
    _instance: redis_async.Redis = None
    _non_async_instance: redis.Redis = None
    def __init__(self):
        self.host = "redis_container"
        self.port = 6379
        pass

    def get_instance(self) -> redis_async.Redis:
        if not self._instance:
            self._instance = redis_async.Redis(host=self.host, port=self.port)
        return self._instance

    def get_non_async_instance(self) -> redis.Redis:
        if not self._non_async_instance:
            self._non_async_instance = redis.Redis(host=self.host, port=self.port)
        return self._non_async_instance