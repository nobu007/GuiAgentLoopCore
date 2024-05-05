import asyncio
import time
import traceback

from gui_agent_loop_core.util.message_format import format_response, show_data_debug
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.messages.base import BaseMessage


def convert_messages(langchain_messages: list[BaseMessage]):
    converted_messages = []
    for message in langchain_messages:
        if isinstance(message, HumanMessage):
            converted_message = {
                "role": "user",
                "type": "message",
                "content": message.content,
            }
        elif isinstance(message, AIMessage):
            converted_message = {
                "role": "assistant",
                "type": "message",
                "content": message.content,
            }
        else:
            print("WARN: converted_messages skip unknown message type=", type(message))
            continue
        converted_messages.append(converted_message)

    return converted_messages


def is_last_user_message_content_remain(last_user_message_content, converted_messages):
    for message in converted_messages:
        if last_user_message_content == message["content"]:
            print("is_last_user_message_content_remain=True")
            return True
    print("is_last_user_message_content_remain=False")
    return False


def process_messages_gradio(
    last_user_message_content: str,
    new_query: str,
    interpreter,
    memory: ConversationBufferWindowMemory,
):
    try:
        # Get the next message from the queue
        new_message = {"role": "user", "type": "message", "content": new_query}

        # messages from history
        messages = memory.load_memory_variables({})["history"]
        converted_messages = convert_messages(messages)

        if last_user_message_content != new_query:
            # is_auto=Trueの場合はここを通る
            if not is_last_user_message_content_remain(
                last_user_message_content, converted_messages
            ):
                # ユーザ入力を忘れたので追加する
                last_user_message = {
                    "role": "user",
                    "type": "message",
                    "content": last_user_message_content,
                }
                converted_messages.insert(0, last_user_message)

        converted_messages.append(new_message)

        # 最終的なメッセージ(実際はsystem_messageが追加される)
        show_data_debug(
            converted_messages,
            "converted_messages",
        )

        response_list = []
        for (
            response,
            chunk_type,
            chunk_role,
            chunk_start,
            chunk_end,
        ) in process_and_format_message(converted_messages, interpreter):
            # Send out assistant message chunks
            response_data = {
                "type": chunk_type,
                "role": chunk_role,
                "content": response,
                "start": chunk_start,
                "end": chunk_end,
            }

            yield response_data
            response_list.append(response)
        full_response = "".join(response_list)
        print("memory.save_context full_response=", full_response[:20])
        memory.save_context({"input": new_query}, {"output": full_response})

    except Exception as e:
        print(f"Error processing message: {e}")
        traceback.print_exc()


def process_and_format_message(message, interpreter):
    try:
        for chunk in interpreter.chat(message, display=False, stream=True):
            yield format_response(chunk)
    except Exception as e:
        print(f"Error in chat: {e}")
        traceback.print_exc()
