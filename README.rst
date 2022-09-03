async_factory_boy
=================

`factory_boy <https://github.com/FactoryBoy/factory_boy>`__ extension
with asynchronous ORM support

Requirements
------------

-  python (3.8, 3.9, 3.10)

Instalation
-----------

Install using ``pip``

::

   pip install async_factory_boy

Usage
-----

async_factory_boy integrate with Object Relational Mapping (ORM) through
subclass of ``factory.Factory``. All supported are listed below.

-  SQLAlchemy, with
   ``async_factory_boy.factory.sqlalchemy.AsyncSQLAlchemyFactory``

.. code:: python

   from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory


   class TestModelFactory(AsyncSQLAlchemyFactory):
       class Meta:
           model = TestModel
           session = session

       name = Faker("name")
       created_at = Faker("date_time")

-  Tortoise ORM, with
   ``async_factory_boy.factory.tortoise.AsyncTortoiseFactory``

.. code:: python

   from async_factory_boy.factory.tortoise import AsyncTortoiseFactory


   class TestModelFactory(AsyncTortoiseFactory):
       class Meta:
           model = TestModel

       name = Faker("name")
       created_at = Faker("date_time")

and factory usage

.. code:: python

   test = await TestModelFactory.create()
   test = await TestModelFactory.build()

For test configuration examples check ``tests/`` directory.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
