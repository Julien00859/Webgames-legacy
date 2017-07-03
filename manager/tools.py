from typing import get_type_hints
from functools import partial

def cast_using_type_hints(type_hints: dict, kwargs: dict):
    return {key: None if value is None else type_hints[key](value) for key, value in kwargs.items()}

def cast_list_using_type_hints(func, datas: list):
    castuth = partial(cast_using_type_hints, get_type_hints(func))
    return list(map(lambda d: func(**d), [castuth(d) for d in datas]))

async def call_later_coro(delay, coro, *args, **kwargs):
    logger.debug("Schedule async call for %s with args %s %s in %d secondes", coro, args, kwargs, delay, call_id)
    await asyncio.sleep(delay)
    logger.debug("Call %s with args %s %s", coro, args, kwargs)
    await coro(*args, **kwargs)