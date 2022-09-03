import factory

from async_factory_boy.factory.tortoise import AsyncTortoiseFactory

from . import models


class StandardFactory(AsyncTortoiseFactory):
    class Meta:
        model = models.StandardModel

    id = factory.Sequence(lambda n: n)
    foo = factory.Sequence(lambda n: "foo%d" % n)


class NonIntegerPkFactory(AsyncTortoiseFactory):
    class Meta:
        model = models.NonIntegerPk

    id = factory.Sequence(lambda n: "foo%d" % n)


class NoSessionFactory(AsyncTortoiseFactory):
    class Meta:
        model = models.StandardModel

    id = factory.Sequence(lambda n: n)


class MultifieldModelFactory(AsyncTortoiseFactory):
    class Meta:
        model = models.MultiFieldModel

    id = factory.Sequence(lambda n: n)
    foo = factory.Sequence(lambda n: "foo%d" % n)


class WithGetOrCreateFieldFactory(AsyncTortoiseFactory):
    class Meta:
        model = models.StandardModel

    id = factory.Sequence(lambda n: n)
    foo = factory.Sequence(lambda n: "foo%d" % n)


class WithMultipleGetOrCreateFieldsFactory(AsyncTortoiseFactory):
    class Meta:
        model = models.MultifieldUniqueModel

    id = factory.Sequence(lambda n: n)
    slug = factory.Sequence(lambda n: "slug%s" % n)
    text = factory.Sequence(lambda n: "text%s" % n)
    title = factory.Sequence(lambda n: "title%s" % n)
