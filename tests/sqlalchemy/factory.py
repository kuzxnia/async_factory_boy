import factory

from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory

from . import models
from .conftest import sc_session


class StandardFactory(AsyncSQLAlchemyFactory):
    class Meta:
        model = models.StandardModel
        sqlalchemy_session = sc_session

    id = factory.Sequence(lambda n: n)
    foo = factory.Sequence(lambda n: "foo%d" % n)


class SessionGetterFactory(AsyncSQLAlchemyFactory):
    class Meta:
        model = models.StandardModel
        sqlalchemy_session = None
        sqlalchemy_session_factory = lambda: sc_session

    id = factory.Sequence(lambda n: n)
    foo = factory.Sequence(lambda n: "foo%d" % n)


class NonIntegerPkFactory(AsyncSQLAlchemyFactory):
    class Meta:
        model = models.NonIntegerPk
        sqlalchemy_session = sc_session

    id = factory.Sequence(lambda n: "foo%d" % n)


class NoSessionFactory(AsyncSQLAlchemyFactory):
    class Meta:
        model = models.StandardModel
        sqlalchemy_session = None

    id = factory.Sequence(lambda n: n)


class MultifieldModelFactory(AsyncSQLAlchemyFactory):
    class Meta:
        model = models.MultiFieldModel
        sqlalchemy_get_or_create = ("slug",)
        sqlalchemy_session = sc_session
        sqlalchemy_session_persistence = "commit"

    id = factory.Sequence(lambda n: n)
    foo = factory.Sequence(lambda n: "foo%d" % n)


class WithGetOrCreateFieldFactory(AsyncSQLAlchemyFactory):
    class Meta:
        model = models.StandardModel
        sqlalchemy_get_or_create = ("foo",)
        sqlalchemy_session = sc_session
        sqlalchemy_session_persistence = "commit"

    id = factory.Sequence(lambda n: n)
    foo = factory.Sequence(lambda n: "foo%d" % n)


class WithMultipleGetOrCreateFieldsFactory(AsyncSQLAlchemyFactory):
    class Meta:
        model = models.MultifieldUniqueModel
        sqlalchemy_get_or_create = (
            "slug",
            "text",
        )
        sqlalchemy_session = sc_session
        sqlalchemy_session_persistence = "commit"

    id = factory.Sequence(lambda n: n)
    slug = factory.Sequence(lambda n: "slug%s" % n)
    text = factory.Sequence(lambda n: "text%s" % n)
