from tortoise.fields.data import BooleanField, CharField, DateField, DecimalField, IntField, TextField
from tortoise.models import Model


class StandardModel(Model):

    id = IntField(pk=True)
    foo = CharField(max_length=20)


class MultiFieldModel(Model):

    id = IntField(pk=True)
    foo = CharField(max_length=20)
    slug = CharField(max_length=20, unique=True)


class MultifieldUniqueModel(Model):

    id = IntField(pk=True)
    slug = CharField(max_length=20, unique=True)
    text = CharField(max_length=20, unique=True)
    title = CharField(max_length=20, unique=True)


class NonIntegerPk(Model):

    id = CharField(max_length=20, pk=True)


class SpecialFieldModel(Model):

    id = IntField(pk=True)
    session = CharField(max_length=20)
