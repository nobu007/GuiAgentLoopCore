from collections.abc import Iterator
from dataclasses import fields, is_dataclass
from typing import Any

from pydantic import BaseModel

from gui_agent_loop_core.converter.request_converter import RequestConverter
from gui_agent_loop_core.converter.response_converter_str import ResponseConverterStr
from gui_agent_loop_core.schema.message.schema import (
    BaseMessageContent,
    GuiAgentInterpreterABC,
    GuiAgentInterpreterChatMessage,
    GuiAgentInterpreterChatRequest,
    GuiAgentInterpreterChatRequestAny,
    GuiAgentInterpreterChatResponse,
    GuiAgentInterpreterChatResponseAny,
)


class DummySession:
    class DummyResponseClass:
        def __init__(self, content):
            self.content: str = content

        def __str__(self):
            return self.content

    class DummyResponsePydantic(BaseModel):
        content: str

    class DummyResponseDataClass(BaseModel):
        content: str

    DUMMY_RESPONSE_DICT = {"content": "DUMMY_RESPONSE_DICT"}
    DUMMY_RESPONSE_DATA_SET = [
        DUMMY_RESPONSE_DICT,
        DummyResponseClass(content="DummyResponseClass"),
        DummyResponsePydantic(content="DummyResponsePydantic"),
        DummyResponseDataClass(content="DummyResponseDataClass"),
    ]

    def generate_response(self, messages: BaseMessageContent) -> Any:
        print("generate_response messages=", messages)
        return DummySession.DummyResponsePydantic(content="DummyResponsePydantic")

    def generate_response_stream(self, messages: BaseMessageContent) -> Iterator[Any]:
        print("generate_response_stream messages=", messages)
        for i in range(4):
            yield DummySession.DUMMY_RESPONSE_DATA_SET[i]

    async def agenerate_response(self, messages: BaseMessageContent) -> Any:
        print("agenerate_response messages=", messages)
        return DummySession.DummyResponseDataClass(content="DummyResponseDataClass")

    async def agenerate_response_stream(self, messages: BaseMessageContent) -> Any:
        print("agenerate_response_stream messages=", messages)
        yield DummySession.DUMMY_RESPONSE_DICT


class ConnectorImplCodeinterpreterApi(GuiAgentInterpreterABC):
    def __init__(self):
        self.session = DummySession()  # just dummy data for test

    def chat_core(
        self,
        request_core: GuiAgentInterpreterChatRequestAny,
        display=True,
        stream=False,
        blocking=True,
    ) -> GuiAgentInterpreterChatResponseAny:
        print("chat_core request_core=", request_core)
        request_converter = RequestConverter()

        # core -> inner(dict)
        mapping_rules = RequestConverter.get_mapping_rules()
        request_converter = RequestConverter(mapping_rules=mapping_rules)
        request_dict_list_inner = request_converter.to_dict_from_core(request_core)

        # chat
        print("chat_core request_dict_list_inner=", request_dict_list_inner)
        # response_inner = self.chat(request_dict_list_inner, display, stream, blocking)
        last_message = request_dict_list_inner[-1]["content"]
        print("chat_core last_message=", last_message)

        stream = True  # ChainExecutor' object has no attribute 'stream'
        if stream:
            # last_message: str
            # response_inner: CodeInterpreterResponse

            # ======= ↓↓↓↓ LLM invoke ↓↓↓↓ #=======
            response_inner = self.session.generate_response_stream(request_dict_list_inner)
            # ======= ↑↑↑↑ LLM invoke ↑↑↑↑ #=======

            for chunk_inner in response_inner:
                print("chat_core response_inner chunk_inner=", chunk_inner)
                response_core = self.handle_response(chunk_inner)
                if response_core.end:
                    yield response_core
        else:
            # TODO: use blocking flag
            # response_inner: CodeInterpreterResponse

            # ======= ↓↓↓↓ LLM invoke ↓↓↓↓ #=======
            response_inner = self.session.generate_response(last_message)
            # ======= ↑↑↑↑ LLM invoke ↑↑↑↑ #=======

            print("response_inner=", response_inner)
            response_core = self.handle_response(chunk_inner)
            yield response_core

    def handle_response(self, response_inner: Any) -> GuiAgentInterpreterChatResponse:
        """汎用的なレスポンス処理(配列には未対応)"""
        response_core = GuiAgentInterpreterChatResponse()
        is_empty = True

        # GuiAgentInterpreterChatResponseの全メンバ名を取得
        response_inner_attributes = self.get_attributes(response_inner)

        # 辞書の場合の処理
        for response_inner_attr in response_inner_attributes:
            if response_inner_attr in response_core:
                value = response_inner[response_inner_attr]
                setattr(response_core, response_inner_attr, value)  # TODO: handle by type?
                is_empty = False

        # 取れない場合はstr経由で変換する
        if is_empty:
            response_converter_str = ResponseConverterStr()
            response_inner_str = str(response_inner)
            response_core = response_converter_str.to_core_from_single_str(response_inner_str)

        # roleを設定
        response_core.role = GuiAgentInterpreterChatMessage.Role.ASSISTANT

        return response_core

    def get_attributes(self, response_inner: Any):
        attributes = []

        if is_dataclass(response_inner):
            attributes = [field.name for field in fields(response_inner)]
        elif is_dataclass(response_inner):
            attributes = [
                attr
                for attr in dir(response_inner)
                if not callable(getattr(response_inner, attr)) and not attr.startswith("_")
            ]
        elif hasattr(response_inner, "__dict__"):
            attributes = response_inner.__dict__.keys()
        else:
            # default
            attributes = ["content", "thought", "code", "agent_name"]
        return attributes


def test():
    impl = ConnectorImplCodeinterpreterApi()
    request = GuiAgentInterpreterChatRequest(content="1+1=?")
    generator = impl.chat_core(request)
    for response in generator:
        print("type(response)=", type(response))
        print(response)


if __name__ == "__main__":
    test()
