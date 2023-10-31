import asyncio
import inspect

from factory import Factory, FactoryError
from factory.alchemy import SQLAlchemyOptions
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, NoResultFound


class AsyncSQLAlchemyFactory(Factory):
    _options_class = SQLAlchemyOptions

    @classmethod
    def _generate(cls, strategy, params):
        # Original params are used in _get_or_create if it cannot build an
        # object initially due to an IntegrityError being raised
        cls._original_params = params
        return super()._generate(strategy, params)

    @classmethod
    async def create(cls, **kwargs):
        session_factory = cls._meta.sqlalchemy_session_factory
        if session_factory:
            cls._meta.sqlalchemy_session = session_factory()
        session = cls._meta.sqlalchemy_session

        instance = await super().create(**kwargs)
        # one commit per build to avoid share the same connection
        await session.commit()
        return instance

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        async def maker_coroutine():
            for key, value in kwargs.items():
                # when using SubFactory, you'll have a Task in the corresponding kwarg
                # await tasks to pass model instances instead
                if inspect.isawaitable(value):
                    kwargs[key] = await value
            # replace as needed by your way of creating model instances

            if cls._meta.sqlalchemy_get_or_create:
                return await cls._get_or_create(model_class, *args, **kwargs)
            return await cls._save(model_class, *args, **kwargs)

        # A Task can be awaited multiple times, unlike a coroutine.
        # useful when a factory and a subfactory must share a same object
        return asyncio.create_task(maker_coroutine())

    @classmethod
    async def create_batch(cls, size, **kwargs):
        return [await cls.create(**kwargs) for _ in range(size)]

    @classmethod
    async def _get_or_create(cls, model_class, *args, **kwargs):
        session = cls._meta.sqlalchemy_session

        key_fields = {}
        for field in cls._meta.sqlalchemy_get_or_create:
            if field not in kwargs:
                raise FactoryError(
                    "sqlalchemy_get_or_create - "
                    "Unable to find initialization value for '%s' in factory %s" %
                    (field, cls.__name__))
            key_fields[field] = kwargs.pop(field)

        obj = (await session.execute(select(model_class).filter_by(*args, **key_fields))).scalars().first()

        if not obj:
            try:
                obj = await cls._save(model_class, *args, **key_fields, **kwargs)
            except IntegrityError as e:
                await session.rollback()
                get_or_create_params = {
                    lookup: value
                    for lookup, value in cls._original_params.items()
                    if lookup in cls._meta.sqlalchemy_get_or_create
                }
                if get_or_create_params:
                    try:
                        obj = (await session.execute(select(model_class).filter_by(**get_or_create_params))).scalars().one()
                    except NoResultFound:
                        # Original params are not a valid lookup and triggered a create(),
                        # that resulted in an IntegrityError.
                        raise e
                else:
                    raise e

        return obj

    @classmethod
    async def _save(cls, model_class, *args, **kwargs):
        session = cls._meta.sqlalchemy_session

        obj = model_class(*args, **kwargs)
        session.add(obj)
        await session.commit()
        return obj

    class Meta:
        abstract = True
