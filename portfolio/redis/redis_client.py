import redis.asyncio as redis_async
import redis 
import environ

env = environ.Env()
environ.Env.read_env()  # to Ensure .env is loaded

REDIS_WEBSOCKET_URL = env("REDIS_WEBSOCKET_URL", default="redis://127.0.0.1:6379/0")

redis_async_client = redis_async.from_url(
    REDIS_WEBSOCKET_URL,
    socket_timeout=5,
    socket_connect_timeout=5,
    health_check_interval=30,
)

redis_sync_client = redis.Redis.from_url(
    REDIS_WEBSOCKET_URL,
    socket_timeout=5,
    socket_connect_timeout=5,
    health_check_interval=30,
)