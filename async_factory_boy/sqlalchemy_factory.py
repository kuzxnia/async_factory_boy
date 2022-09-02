import asyncio                                                                           
import inspect                                                                           
                                                                                         
from factory import Factory                                                              
from typing import Any
                                                                                         
                                                                                         
class AsyncSQLAlchemyFactory(Factory):                                                             
    session: Any
    
    @classmethod                                                                         
    async def create(cls, **kwargs):                                                     
        instance = await super().create(**kwargs)                                        
        # one commit per build to avoid share the same connection                        
        await cls.session.commit()                                                        
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
            instance = model_class(*args, **kwargs)                                      
            cls.session.add(instance)                                                     
            return instance                                                              
                                                                                         
        # A Task can be awaited multiple times, unlike a coroutine.                      
        # useful when a factory and a subfactory must share a same object                
        return asyncio.create_task(maker_coroutine())                                    
                                                                                         
    @classmethod                                                                         
    async def create_batch(cls, size, **kwargs):                                         
        return [await cls.create(**kwargs) for _ in range(size)]                         

    class Meta:
        abstract = True
        exclude = ("session",)
