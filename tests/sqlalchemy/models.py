from sqlalchemy import Column, Integer, Unicode
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class StandardModel(Base):
    __tablename__ = "StandardModelTable"

    id = Column(Integer(), primary_key=True)
    foo = Column(Unicode(20))


class MultiFieldModel(Base):
    __tablename__ = "MultiFieldModelTable"

    id = Column(Integer(), primary_key=True)
    foo = Column(Unicode(20))
    slug = Column(Unicode(20), unique=True)


class MultifieldUniqueModel(Base):
    __tablename__ = "MultiFieldUniqueModelTable"

    id = Column(Integer(), primary_key=True)
    slug = Column(Unicode(20), unique=True)
    text = Column(Unicode(20), unique=True)
    title = Column(Unicode(20), unique=True)


class NonIntegerPk(Base):
    __tablename__ = "NonIntegerPk"

    id = Column(Unicode(20), primary_key=True)


class SpecialFieldModel(Base):
    __tablename__ = "SpecialFieldModelTable"

    id = Column(Integer(), primary_key=True)
    session = Column(Unicode(20))
