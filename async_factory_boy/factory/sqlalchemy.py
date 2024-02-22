import asyncio
import inspect
from inspect import isawaitable
from typing import Any, Optional

from factory import errors, Factory, FactoryError
from factory.alchemy import SQLAlchemyOptions
from factory.builder import (BuildStep, DeclarationSet, parse_declarations, Resolver, StepBuilder)
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, NoResultFound


class AsyncResolver(Resolver):
    async def async_get(self, name: str) -> Any:
        """Get a value from the stub, resolving async values."""
        value = getattr(self, name)
        if isawaitable(value):
            value = await value
            self._Resolver__values[name] = value

        return value


class AsyncBuildStep(BuildStep):
    async def resolve(self, declarations: DeclarationSet) -> None:  # type: ignore[override]
        self.stub = AsyncResolver(
            declarations=declarations,
            step=self,
            sequence=self.sequence,
        )

        for field_name in declarations:
            self.attributes[field_name] = await self.stub.async_get(field_name)


class AsyncStepBuilder(StepBuilder):
    async def build(
        self,
        parent_step: Optional[AsyncBuildStep] = None,  # type: ignore[override]
        force_sequence: Any = None,
    ) -> Any:
        """Build a factory instance."""
        # This method is a copy-paste from the original StepBuilder.build method
        # with the only difference that the AsyncBuildStep is used instead of BuildStep
        # and the resolve method is awaited.

        pre, post = parse_declarations(
            self.extras,
            base_pre=self.factory_meta.pre_declarations,
            base_post=self.factory_meta.post_declarations,
        )

        if force_sequence is not None:
            sequence = force_sequence
        elif self.force_init_sequence is not None:
            sequence = self.force_init_sequence
        else:
            sequence = self.factory_meta.next_sequence()

        # The next line was changed:
        step = AsyncBuildStep(
            builder=self,
            sequence=sequence,
            parent_step=parent_step,
        )
        # The next line was changed:
        await step.resolve(pre)

        args, kwargs = self.factory_meta.prepare_arguments(step.attributes)

        instance = self.factory_meta.instantiate(
            step=step,
            args=args,
            kwargs=kwargs,
        )

        # The next two lines were added:
        if inspect.isawaitable(instance):
            instance = await instance

        postgen_results = {}
        for declaration_name in post.sorted():
            declaration = post[declaration_name]
            postgen_results[
                declaration_name] = declaration.declaration.evaluate_post(
                instance=instance,
                step=step,
                overrides=declaration.context,
            )
        self.factory_meta.use_postgeneration_results(
            instance=instance,
            step=step,
            results=postgen_results,
        )
        return instance


class AsyncSQLAlchemyFactory(Factory):
    _options_class = SQLAlchemyOptions

    @classmethod
    async def _generate(cls, strategy, params):
        # Original params are used in _get_or_create if it cannot build an
        # object initially due to an IntegrityError being raised
        cls._original_params = params

        if cls._meta.abstract:
            raise errors.FactoryError(
                "Cannot generate instances of abstract factory {f}; "
                "Ensure {f}.Meta.model is set and {f}.Meta.abstract "
                "is either not set or False.".format(**dict(f=cls.__name__)),
            )

        step = AsyncStepBuilder(cls._meta, params, strategy)
        return await step.build()

    @classmethod
    async def create(cls, **kwargs):
        session = cls._meta.sqlalchemy_session

        instance = await super().create(**kwargs)
        # one commit per build to avoid share the same connection
        await session.commit()
        return instance

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        session = cls._meta.sqlalchemy_session

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
                        obj = (
                            await session
                            .execute(select(model_class)
                            .filter_by(**get_or_create_params))
                        ).scalars().one()
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
