import redis.asyncio as aioredis
from src.config import Config

# Initialize Redis client
token_blocklist = aioredis.from_url(
    f"redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}", 
    decode_responses=True  # Ensures returned values are strings
)

async def add_jti_to_blocklist(jti: str) -> None:
    """Add a JTI (JWT ID) to the Redis blocklist with expiration."""
    await token_blocklist.set(
        name=jti,
        value="blocked",
        ex=Config.JTI_EXPIRY  # Expiry time for the token
    )

async def jti_token_in_blocklist(jti: str) -> bool:
    """Check if a JTI (JWT ID) exists in the Redis blocklist."""
    _jti = await token_blocklist.get(jti)
    return _jti is not None
