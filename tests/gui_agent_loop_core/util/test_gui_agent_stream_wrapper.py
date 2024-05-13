import pytest

from gui_agent_loop_core.util.gui_agent_stream_wrapper import (
    test_async_gui_agent_stream_wrapper,
    test_sync_gui_agent_stream_wrapper,
)


@pytest.mark.asyncio
async def test_async_gui_agent_stream_wrapper_run():
    test_async_gui_agent_stream_wrapper()


def test_sync_gui_agent_stream_wrapper_run():
    test_sync_gui_agent_stream_wrapper()
