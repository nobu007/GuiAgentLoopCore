import os
from typing import Any, Dict, List, Union

from pydantic import BaseModel

from gui_agent_loop_core.converter.request_converter import RequestConverter
from gui_agent_loop_core.converter.request_converter_str import RequestConverterStr
from gui_agent_loop_core.converter.response_converter_str import ResponseConverterStr
from gui_agent_loop_core.schema.message.schema import (
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
        print("chat_core request_core=", request_core)
        request_converter = RequestConverter()
        request_converter_str = RequestConverterStr()
        response_converter_str = ResponseConverterStr()

        # core -> inner(dict)
        mapping_rules = RequestConverter.get_mapping_rules()
        request_converter = RequestConverter(mapping_rules=mapping_rules)
        request_dict_list_inner = request_converter.to_dict_from_core(request_core)

        # chat
        print("chat_core request_dict_list_inner=", request_dict_list_inner)
        # response_inner = self.chat(request_dict_list_inner, display, stream, blocking)
        last_message = request_dict_list_inner[-1]["content"]
        full_message = request_dict_list_inner
        full_message_str = str(request_dict_list_inner)
        print("chat_core last_message=", last_message)
        if last_message == os.environ.get("AUTO_CHAT_PROMPT"):
            # プロンプト節約のため履歴を使わない方式なので初期プロンプトを毎回入れる
            last_message = os.environ.get("INITIAL_PROMPT", last_message)
        print("chat_core last_message=", last_message)

        stream = True  # ChainExecutor' object has no attribute 'stream'
        if stream:
            # last_message: str
            # response_inner: CodeInterpreterResponse

            # ======= ↓↓↓↓ LLM invoke ↓↓↓↓ #=======
            response_inner = self.session.generate_response_stream(request_dict_list_inner)
            # ======= ↑↑↑↑ LLM invoke ↑↑↑↑ #=======

            for chunk_inner in response_inner:
                chunk_inner = str(chunk_inner)  # for error case
                print("chat_core response_inner chunk_inner=", chunk_inner)

                # inner -> core
                response_core = response_converter_str.to_core_from_single_str(chunk_inner)
                response_core.role = GuiAgentInterpreterChatMessage.Role.ASSISTANT
                yield response_core
        else:
            # last_message: str
            # response_inner: CodeInterpreterResponse

            # ======= ↓↓↓↓ LLM invoke ↓↓↓↓ #=======
            response_inner = self.session.generate_response(last_message)
            # ======= ↑↑↑↑ LLM invoke ↑↑↑↑ #=======

            print("response_inner=", response_inner)
            response_inner_str = str(response_inner.content)  # workaround
            response_inner_code_log_str = str(response_inner.code_log)  # workaround
            response_core = response_converter_str.to_core_from_single_str(response_inner_str)
            response_core.role = GuiAgentInterpreterChatMessage.Role.ASSISTANT
            response_core.code = response_inner.code_log
            response_core.agent_name = response_inner.agent_name
            print("response_inner_code_log_str=", response_inner_code_log_str)
            print("response_core=", response_core)
            yield response_core


def test():
    pass


if __name__ == "__main__":
    test()
