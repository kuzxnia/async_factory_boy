import factory
import pytest

from async_factory_boy.factory.tortoise import AsyncTortoiseFactory

from .factory import NonIntegerPkFactory, NoSessionFactory, StandardFactory
from .models import SpecialFieldModel


class TestSQLAlchemyPkSequence:
    @pytest.fixture(autouse=True)
    def setup(self):
        StandardFactory.reset_sequence(1)

    async def test_pk_first(self):
        std = await StandardFactory.build()
        assert 'foo1' == std.foo

    async def test_pk_many(self):
        std1 = await StandardFactory.build()
        std2 = await StandardFactory.build()
        assert 'foo1' == std1.foo
        assert 'foo2' == std2.foo

    async def test_pk_creation(self):
        std1 = await StandardFactory.create()
        assert 'foo1' == std1.foo
        assert 1 == std1.id

        StandardFactory.reset_sequence()
        std2 = await StandardFactory.create()
        assert 'foo0' == std2.foo
        assert 0 == std2.id

    async def test_pk_force_value(self):
        std1 = await StandardFactory.create(id=10)
        assert 'foo1' == std1.foo  # sequence and pk are unrelated
        assert 10 == std1.id

        StandardFactory.reset_sequence()
        std2 = await StandardFactory.create()
        assert 'foo0' == std2.foo  # Sequence doesn't care about pk
        assert 0 == std2.id


class TestSQLAlchemyNonIntegerPk:
    @pytest.fixture(autouse=True)
    def setup(self):
        yield
        NonIntegerPkFactory.reset_sequence()

    async def test_first(self):
        nonint = await NonIntegerPkFactory.build()
        assert 'foo0' == nonint.id

    async def test_many(self):
        nonint1 = await NonIntegerPkFactory.build()
        nonint2 = await NonIntegerPkFactory.build()

        assert 'foo0' == nonint1.id
        assert 'foo1' == nonint2.id

    async def test_creation(self):
        nonint1 = await NonIntegerPkFactory.create()
        assert 'foo0' == nonint1.id

        NonIntegerPkFactory.reset_sequence()
        nonint2 = await NonIntegerPkFactory.build()
        assert 'foo0' == nonint2.id

    async def test_force_pk(self):
        nonint1 = await NonIntegerPkFactory.create(id='foo10')
        assert 'foo10' == nonint1.id

        NonIntegerPkFactory.reset_sequence()
        nonint2 = await NonIntegerPkFactory.create()
        assert 'foo0' == nonint2.id


class TestSQLAlchemyNoSession:
    async def test_build_does_not_raises_exception_when_no_session_was_set(self):
        NoSessionFactory.reset_sequence()  # Make sure we start at test ID 0

        inst0 = await NoSessionFactory.build()
        inst1 = await NoSessionFactory.build()
        assert inst0.id == 0
        assert inst1.id == 1


class TestNameConflict:
    """Regression test for `TypeError: _save() got multiple values for argument 'session'`
    See #775.
    """
    async def test_no_name_conflict_on_save(self):
        class SpecialFieldWithSaveFactory(AsyncTortoiseFactory):
            class Meta:
                model = SpecialFieldModel

            id = factory.Sequence(lambda n: n)
            session = ''

        saved_child = await SpecialFieldWithSaveFactory()
        assert saved_child.session == ""

    async def test_no_name_conflict_on_get_or_create(self):
        class SpecialFieldWithGetOrCreateFactory(AsyncTortoiseFactory):
            class Meta:
                model = SpecialFieldModel

            id = factory.Sequence(lambda n: n)
            session = ''

        get_or_created_child = await SpecialFieldWithGetOrCreateFactory()
        assert get_or_created_child.session == ""
