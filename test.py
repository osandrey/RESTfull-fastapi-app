from jose import jwt

# дані для заповнення токена
payload = {"sub": "1234567890", "name": "Andrii Osa"}

# створення токена з симетричним ключем
encoded = jwt.encode(payload, "secret_key", algorithm='HS256')
print(encoded)

# перевірка токена
decoded = jwt.decode(encoded, "secret_key", algorithms=['HS256'])
print(decoded)









import aioredis

# Create a Redis connection pool
redis_pool = None

async def create_redis_pool():
    global redis_pool
    redis_pool = await aioredis.create_redis_pool(
        (settings.redis_host, settings.redis_port),
        encoding="utf-8",
        decode_responses=True
    )

@app.on_event("startup")
async def startup():
    # Create the Redis connection pool
    await create_redis_pool()

    # Initialize FastAPILimiter using the Redis connection pool
    await FastAPILimiter.init(redis_pool)