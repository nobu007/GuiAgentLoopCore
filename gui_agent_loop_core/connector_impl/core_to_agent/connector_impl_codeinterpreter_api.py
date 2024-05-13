from typing import List, Union

from pydantic import BaseModel

from gui_agent_loop_core.converter.request_converter import RequestConverter
from gui_agent_loop_core.converter.request_converter_str import RequestConverterStr
from gui_agent_loop_core.schema.schema import (
    GuiAgentInterpreterABC,
    GuiAgentInterpreterChatMessage,
    GuiAgentInterpreterChatRequestAny,
    GuiAgentInterpreterChatResponseAny,
)

CoreAny = Union[str, BaseModel, List[BaseModel]]


class ConnectorImplCodeinterpreterApi(GuiAgentInterpreterABC):
    def chat_core(
        self,
        request_core: GuiAgentInterpreterChatRequestAny,
        display=True,
        stream=False,
        blocking=True,
    ) -> GuiAgentInterpreterChatResponseAny:
        converter = RequestConverter()
        converter_str = RequestConverterStr()

        # core -> inner(dict)
        mapping_rules = RequestConverter.get_mapping_rules()
        converter = RequestConverter(mapping_rules=mapping_rules)
        request_dict_list_inner = converter.to_dict_from_core(request_core)

        # chat
        print("chat_core request_inner=", request_dict_list_inner)
        # response_inner = self.chat(request_dict_list_inner, display, stream, blocking)
        last_message = request_dict_list_inner[-1]["content"]
        print("chat_core last_message=", last_message)

        stream = False  # ChainExecutor' object has no attribute 'stream'
        if stream:
            # last_message: str
            # response_inner: CodeInterpreterResponse
            response_inner = self.session.generate_response_stream(last_message)
            for chunk_inner in response_inner:
                chunk_inner = str(chunk_inner)  # for error case
                print("chat_core response_inner chunk_inner=", chunk_inner)

                # inner -> core
                response_core = converter_str.to_core_from_single_str(last_message)
                response_core.role = GuiAgentInterpreterChatMessage.Role.ASSISTANT
                yield response_core
        else:
            # last_message: str
            # response_inner: CodeInterpreterResponse
            response_inner = self.session.generate_response(last_message)
            print("response_inner=", response_inner)
            response_inner_str = str(response_inner.content)  # workaround
            response_inner_code_log_str = str(response_inner.code_log)  # workaround
            response_core = converter_str.to_core_from_single_str(response_inner_str)
            response_core.role = GuiAgentInterpreterChatMessage.Role.ASSISTANT
            print("response_inner_code_log_str=", response_inner_code_log_str)
            print("response_core=", response_core)
            yield response_core


def test():
    pass


if __name__ == "__main__":
    test()
