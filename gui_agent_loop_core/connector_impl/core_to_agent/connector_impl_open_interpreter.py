from typing import List, Optional, Type, Union

from pydantic import BaseModel

from gui_agent_loop_core.converter.request_converter import RequestConverter
from gui_agent_loop_core.schema.schema import (
    GuiAgentInterpreterABC,
    GuiAgentInterpreterChatRequest,
    GuiAgentInterpreterChatRequestAny,
    GuiAgentInterpreterChatRequestList,
)

CoreAny = Union[str, BaseModel, List[BaseModel]]


class ConnectorImplOpenInterpreter(GuiAgentInterpreterABC):

    def chat_core(
        self,
        request_core: GuiAgentInterpreterChatRequestAny,
        display=True,
        stream=False,
        blocking=True,
    ):
        # core -> inner
        converter = RequestConverter()
        request_dict_list_inner = converter.to_dict_from_core(request_core)

        # chat
        response_inner = self.chat(request_dict_list_inner, display, stream, blocking)
        print("chat_core response_inner=", response_inner)

        # inner -> core
        response_core_list = converter.to_core_from_dict(response_inner)
        for chunk in response_core_list:
            yield chunk
