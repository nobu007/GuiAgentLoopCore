import traceback
from collections.abc import Iterator

from langchain.memory import ConversationBufferWindowMemory
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.messages.base import BaseMessage

from gui_agent_loop_core.schema.message.schema import (
    GuiAgentInterpreterABC,
    GuiAgentInterpreterChatMessage,
    GuiAgentInterpreterChatRequest,
    GuiAgentInterpreterChatRequestList,
    GuiAgentInterpreterChatResponse,
    GuiAgentInterpreterChatResponseAny,
)
from gui_agent_loop_core.util.gui_agent_stream_wrapper import GuiAgentStreamWrapper
from gui_agent_loop_core.util.message_format import format_response, show_data_debug


def convert_core_from_langchain_messages(
    langchain_messages: list[BaseMessage],
) -> GuiAgentInterpreterChatRequestList:
    request_core_list = []
    for message in langchain_messages:
        show_data_debug(
            message,
            "langchain_message",
        )
        converted_message = GuiAgentInterpreterChatRequest()
        if isinstance(message, HumanMessage):
            converted_message.type = GuiAgentInterpreterChatMessage.Type.MESSAGE
            converted_message.role = GuiAgentInterpreterChatMessage.Role.USER
            converted_message.content = message.content
        elif isinstance(message, AIMessage):
            converted_message.type = GuiAgentInterpreterChatMessage.Type.MESSAGE
            converted_message.role = GuiAgentInterpreterChatMessage.Role.ASSISTANT
            converted_message.content = message.content
        else:
            print("WARN: converted_messages skip unknown message type=", type(message))
            continue
        request_core_list.append(converted_message)

    return request_core_list


def is_last_user_message_content_remain(last_user_message_content, converted_messages):
    for message in converted_messages:
        if last_user_message_content == message.content:
            print("is_last_user_message_content_remain=True")
            return True
    print("is_last_user_message_content_remain=False")
    return False


def prepare_and_process_messages(
    last_user_message_content: str,
    new_query: str,
    interpreter: GuiAgentInterpreterABC,
    memory: ConversationBufferWindowMemory,
) -> GuiAgentInterpreterChatResponseAny:
    try:
        # Get the next message from the queue
        new_request = GuiAgentInterpreterChatRequest.user(new_query)
        print("add new_query=", new_query)
        print("add new_request=", new_request)

        # messages from history
        messages = memory.load_memory_variables({})["history"]
        request_core_list = convert_core_from_langchain_messages(messages)

        if last_user_message_content != new_query:
            # is_auto=Trueの場合はここを通る
            if not is_last_user_message_content_remain(last_user_message_content, request_core_list):
                # ユーザ入力を忘れたので追加する
                print("add last_user_message_content=", last_user_message_content)
                last_user_message = GuiAgentInterpreterChatRequest.user(last_user_message_content)
                request_core_list.insert(0, last_user_message)

        request_core_list.append(new_request)

        # 最終的なメッセージ(実際はsystem_messageが追加される)
        show_data_debug(
            request_core_list,
            "request_core_list",
        )

        response_list = []

        # ======= ↓↓↓↓ LLM invoke ↓↓↓↓ #=======
        response_chunks = process_and_format_message(request_core_list, interpreter)
        # ======= ↑↑↑↑ LLM invoke ↑↑↑↑ #=======

        for chunk in response_chunks:
            # Send out assistant message chunks
            yield chunk
            response_list.append(chunk.content)
        full_response = "".join(response_list)
        print("memory.save_context full_response=", full_response[:20])
        memory.save_context({"input": new_query}, {"output": full_response})

    except Exception as e:
        print(f"Error processing message: {e}")
        traceback.print_exc()


def process_and_format_message(
    request_core_list: GuiAgentInterpreterChatRequestList,
    interpreter: GuiAgentInterpreterABC,
) -> Iterator[GuiAgentInterpreterChatResponse]:
    try:
        # TODO: rename message -> messages
        response = interpreter.chat_core(request_core_list, display=False, stream=True)
        response_wrapper = GuiAgentStreamWrapper(response)  # wrapper is always as sync stream list

        for chunk in response_wrapper:
            formatted_chunk = format_response(chunk)
            yield formatted_chunk
    except Exception as e:
        print(f"Error in chat: {e}")
        traceback.print_exc()
