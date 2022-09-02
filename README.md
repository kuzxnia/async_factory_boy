# asyns_factory_boy
[factory_boy](https://github.com/FactoryBoy/factory_boy) extension with asynchronous ORM support

## Requirements
* python 

## Instalation

Install using `pip`
```
pip install async_factory_boy
```

## Example
async_factory_boy integrate with Object Relational Mapping (ORM) through subclass of 'factory.Factory'. All supported are listed below.

* SQLAlchemy, with `async_factory_boy.factory.sqlalchemy.AsyncSQLAlchemyFactory`

```python
from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory


class UserFactory(AsyncFactory):
    class Meta:
        model = User
        session = session

    name = Faker("name")
    created_at = Faker("date_time")
```


* Tortoise ORM, with `async_factory_boy.factory.tortoise.AsyncTortoiseFactory`


```python
from async_factory_boy.factory.tortoise import AsyncTortoiseFactory


class UserFactory(AsyncTortoiseFactory):
    class Meta:
        model = User

    name = Faker("name")
    created_at = Faker("date_time")
```

and factory usage

```python
user = await UserFactory.create()
user = await UserFactory.build()
```

##### for test configuration examples check `tests/` directory
