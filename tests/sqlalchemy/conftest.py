import asyncio

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from . import models

engine = create_async_engine("sqlite+aiosqlite://")
async_session  = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)
# global session instance for factory-boy
sc_session = scoped_session(async_session)


@pytest.fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='function', autouse=True)#(scope="session")
async def db_session() -> AsyncSession:
    async with engine.begin() as connection:
        await connection.run_sync(models.Base.metadata.drop_all)
        await connection.run_sync(models.Base.metadata.create_all)
        # operation in progress
        # await connection.begin_nested()

        # if sc_session.registry.has():
        #     await sc_session.registry().close()

        # sc_session.registry.clear()
        # sc_session.configure(bind=connection)

        async with async_session(bind=connection) as session:
            yield session
            await session.flush()
            await session.rollback()


# @pytest_asyncio.fixture(autouse=True)
# async def clean_session(db_session):
#     for table in reversed(models.Base.metadata.sorted_tables):
#         await db_session.execute(table.delete())
#     await db_session.commit()

#     return db_session
