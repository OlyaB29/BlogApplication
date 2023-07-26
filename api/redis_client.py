import aioredis
from config import settings

# Redis client for saving information about the number of likes and dislikes for each post, receiving it and changing it


class RedisCl:
    REDIS = aioredis.from_url("redis://{}".format(settings.REDIS_HOST), password=settings.REDIS_PASS)

    async def get_ratings(self, post_id):
        async with self.REDIS.pipeline(transaction=True) as pipe:
            likes, dislikes = await (pipe.get("{}_likes".format(post_id)).get("{}_dislikes".format(post_id)).execute())
            return likes, dislikes

    async def actualize_ratings(self, post_id, likes, dislikes):
        async with self.REDIS.pipeline(transaction=True) as pipe:
            await (pipe.set("{}_likes".format(post_id), likes, 604800).set("{}_dislikes".format(post_id), dislikes,
                                                                           604800).execute())

    async def add_rating(self, post_id, rating_type):
        async with self.REDIS.client() as conn:
            key = "{}_{}".format(post_id, rating_type)
            if await conn.get(key):
                await conn.incr(key)
                return True
            return False

    async def deduct_rating(self, post_id, rating_type):
        async with self.REDIS.client() as conn:
            key = "{}_{}".format(post_id, rating_type)
            if await conn.get(key):
                await conn.decr(key)
                return True
            return False

    async def edit_rating(self, post_id, from_type, to_type):
        async with self.REDIS.client() as conn:
            key_from = "{}_{}".format(post_id, from_type)
            key_to = "{}_{}".format(post_id, to_type)
            if await conn.get(key_from):
                pipe = conn.pipeline(transaction=True)
                await pipe.decr(key_from).incr(key_to).execute()
                return True
            return False

