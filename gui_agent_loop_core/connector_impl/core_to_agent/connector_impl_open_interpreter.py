from typing import List, Union

from pydantic import BaseModel

from gui_agent_loop_core.converter.request_converter import RequestConverter
from gui_agent_loop_core.schema.message.schema import (
    GuiAgentInterpreterABC,
    GuiAgentInterpreterChatRequestAny,
    GuiAgentInterpreterChatResponse,
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
        mapping_rules = RequestConverter.get_mapping_rules()
        converter = RequestConverter(mapping_rules=mapping_rules)
        request_dict_list_inner = converter.to_dict_from_core(request_core)

        # chat
        print("chat_core request_dict_list_inner=", request_dict_list_inner)
        response_inner = self.chat(request_dict_list_inner, display, stream, blocking)

        for chunk_inner in response_inner:
            print("chat_core response_inner chunk_inner=", chunk_inner)

            # inner -> core
            response_core = converter.to_core_from_dict([chunk_inner], core_class=GuiAgentInterpreterChatResponse)

            yield response_core
