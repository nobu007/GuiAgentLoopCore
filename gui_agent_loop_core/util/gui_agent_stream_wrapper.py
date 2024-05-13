import asyncio
import types
from collections.abc import AsyncIterable, Iterable
from typing import Any, AsyncGenerator, AsyncIterator, Coroutine, Iterator, Union


class GuiAgentStreamWrapper(Iterable, AsyncIterable):
    def __init__(self, value: Any):
        if isinstance(value, types.AsyncGeneratorType):
            # 非同期ジェネレータの場合
            self.aiterator = self._wrap_async_generator(value)
            # print("init aiterator list")
        elif isinstance(value, types.GeneratorType):
            # 同期ジェネレータの場合
            self.iterator = self._wrap_sync_generator(value)
            # print("init iterator list")
        elif asyncio.iscoroutine(value) or isinstance(value, asyncio.Future):
            # 非同期関数の戻り値（単一の値）の場合
            self.aiterator = self._wrap_async_single_value(value)
            # print("init aiterator single")
        else:
            # 同期の単一の値の場合
            self.iterator = self._wrap_single_value(value)
            # print("init iterator single")

    async def _wrap_async_generator(self, value: AsyncGenerator) -> AsyncIterator:
        async for item in value:
            yield item

    async def _wrap_async_single_value(self, value: Union[Coroutine, asyncio.Future]) -> AsyncIterator:
        result = await value
        yield result

    def _wrap_sync_generator(self, value: Iterator) -> Iterator:
        yield from value

    def _wrap_single_value(self, value: Any) -> Iterator:
        yield value

    def __iter__(self) -> Iterator:
        if hasattr(self, 'iterator'):
            return self.iterator
        else:
            return self._sync_iter()

    def _sync_iter(self) -> Iterator:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._collect_results())

    async def _collect_results(self) -> Iterator:
        results = []
        async for item in self._async_iter():
            results.append(item)
        return iter(results)

    def __aiter__(self) -> AsyncIterator:
        if hasattr(self, 'aiterator'):
            return self.aiterator
        elif hasattr(self, 'iterator'):
            return self._async_iter_from_sync()
        else:
            raise TypeError("Not an async iterable")

    async def _async_iter_from_sync(self) -> AsyncIterator:
        for item in self.iterator:
            yield item

    async def _async_iter(self) -> AsyncIterator:
        if hasattr(self, 'aiterator'):
            async for item in self.aiterator:
                yield item
        elif hasattr(self, 'iterator'):
            for item in self.iterator:
                yield item
        else:
            raise TypeError("Not an async iterable")


def sync_stream_wrapper(value: Any) -> GuiAgentStreamWrapper:
    return GuiAgentStreamWrapper(value)


async def sample_async_generator():
    for i in range(3):
        yield i
        await asyncio.sleep(0.1)


async def sample_async_single_value():
    await asyncio.sleep(0.1)
    return 42


def sample_sync_generator():
    for i in range(2):
        yield i


def sample_sync_single_value():
    return 43


async def test_async_gui_agent_stream_wrapper():
    test_async_aiter()
    test_async_single_value_aiter()


def test_sync_gui_agent_stream_wrapper():
    test_sync_iter()
    test_sync_single_value_iter()


async def test_async_aiter():
    wrapped = GuiAgentStreamWrapper(sample_async_generator())
    result = [item async for item in wrapped]
    assert result == [0, 1, 2]


async def test_async_single_value_aiter():
    wrapped = GuiAgentStreamWrapper(sample_async_single_value())
    result = [item async for item in wrapped]
    assert result == [42]


def test_sync_iter():
    wrapped = GuiAgentStreamWrapper(sample_sync_generator())
    result = [item for item in wrapped]
    assert result == [0, 1]


def test_sync_single_value_iter():
    wrapped = GuiAgentStreamWrapper(sample_sync_single_value())
    result = [item for item in wrapped]
    assert result == [43]


if __name__ == "__main__":
    test_async_gui_agent_stream_wrapper()
    test_sync_gui_agent_stream_wrapper()
