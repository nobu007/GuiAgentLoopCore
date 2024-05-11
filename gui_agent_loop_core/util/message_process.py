import inspect
import traceback

from langchain.memory import ConversationBufferWindowMemory
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.messages.base import BaseMessage

from gui_agent_loop_core.schema.schema import (
    GuiAgentInterpreterABC,
    GuiAgentInterpreterChatMessage,
    GuiAgentInterpreterChatMessageList,
    GuiAgentInterpreterChatRequest,
    GuiAgentInterpreterChatRequestAny,
    GuiAgentInterpreterChatRequestList,
    GuiAgentInterpreterChatResponseAny,
    GuiAgentInterpreterChatResponseAnyAsync,
    GuiAgentInterpreterChatResponseGenerator,
)
from gui_agent_loop_core.util.message_format import format_response, show_data_debug


def convert_messages(langchain_messages: list[BaseMessage]) -> GuiAgentInterpreterChatRequestList:
    request_core_list = []
    for message in langchain_messages:
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


async def process_messages_gradio(
    last_user_message_content: str,
    new_query: str,
    interpreter: GuiAgentInterpreterABC,
    memory: ConversationBufferWindowMemory,
) -> GuiAgentInterpreterChatResponseAny:
    try:
        # Get the next message from the queue
        new_request = GuiAgentInterpreterChatRequest()
        new_request.type = GuiAgentInterpreterChatMessage.Type.MESSAGE
        new_request.role = GuiAgentInterpreterChatMessage.Role.USER
        new_request.content = new_query

        # messages from history
        messages = memory.load_memory_variables({})["history"]
        request_core_list = convert_messages(messages)

        if last_user_message_content != new_query:
            # is_auto=Trueの場合はここを通る
            if not is_last_user_message_content_remain(last_user_message_content, request_core_list):
                # ユーザ入力を忘れたので追加する
                last_user_message = GuiAgentInterpreterChatRequest()
                last_user_message.type = GuiAgentInterpreterChatMessage.Type.MESSAGE
                last_user_message.role = GuiAgentInterpreterChatMessage.Role.USER
                last_user_message.content = last_user_message_content
                request_core_list.insert(0, last_user_message)

        request_core_list.append(new_request)

        # 最終的なメッセージ(実際はsystem_messageが追加される)
        show_data_debug(
            request_core_list,
            "request_core_list",
        )

        response_list = []
        response_chunks = process_and_format_message(request_core_list, interpreter)
        # print("process_messages_gradio response_chunks=", response_chunks)
        async for chunk in response_chunks:
            # Send out assistant message chunks
            # print("process_messages_gradio response=", chunk)
            yield chunk
            response_list.append(chunk.content)
        full_response = "".join(response_list)
        print("memory.save_context full_response=", full_response[:20])
        memory.save_context({"input": new_query}, {"output": full_response})

    except Exception as e:
        print(f"Error processing message: {e}")
        traceback.print_exc()


async def process_and_format_message(
    request_core_list: GuiAgentInterpreterChatRequestList, interpreter: GuiAgentInterpreterABC
) -> GuiAgentInterpreterChatResponseAny:
    try:
        # TODO: rename message -> messages
        response_chunks = interpreter.chat_core(request_core_list, display=False, stream=True)
        if not inspect.isasyncgen(response_chunks):
            # 同期ジェネレーターの場合
            for chunk in format_message_sync(response_chunks):
                yield chunk
        else:
            # 非同期ジェネレーターの場合
            for chunk in format_message_async(response_chunks):
                yield chunk
    except Exception as e:
        print(f"Error in chat: {e}")
        traceback.print_exc()


def format_message_sync(
    response_chunks: GuiAgentInterpreterChatResponseAnyAsync,
) -> GuiAgentInterpreterChatResponseGenerator:
    try:
        for chunk in response_chunks:
            yield format_response(chunk)
    except Exception as e:
        print(f"Error in chat: {e}")
        traceback.print_exc()


async def format_message_async(
    response_chunks: GuiAgentInterpreterChatResponseAnyAsync,
) -> GuiAgentInterpreterChatResponseAnyAsync:
    try:
        async for chunk in response_chunks:
            yield format_response(chunk)
    except Exception as e:
        print(f"Error in chat: {e}")
        traceback.print_exc()
