from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


import ssl

class Base(DeclarativeBase):
    pass


connect_args = {}
# Check if it's a DigitalOcean or remote database URL to use SSL
if "ondigitalocean.com" in settings.database_url or "db" in settings.database_url:
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    connect_args["ssl"] = ssl_context

engine = create_async_engine(
    settings.database_url,
    echo=settings.app_debug,
    future=True,
    connect_args=connect_args
)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
