import asyncio
import time
from functools import partial

import gradio as gr
from langchain.memory import ConversationBufferWindowMemory

from .message_format import show_data_debug
from .message_process import process_messages_gradio

STATE_INIT = "init"
STATE_RUNNING = "running"
STATE_STOP = "stop"
g_last_user_message_content = "N/A"
g_current_state = STATE_INIT


# チャットボットの応答を生成する関数
def chat(
    interpreter,
    memory: ConversationBufferWindowMemory,
    new_query: str,
    is_auto=False,
):
    global g_last_user_message_content, g_current_state
    print("interpreter=", type(interpreter))
    print("memory=", type(memory))
    show_data_debug(new_query, "new_query")
    if not new_query:
        print("skip no input")
        yield ""
        return

    # store last_user_message_content
    if not is_auto:
        g_last_user_message_content = new_query

    # Start a separate task for processing messages
    g_current_state = STATE_RUNNING
    response = ""
    for chunk in process_messages_gradio(
        g_last_user_message_content, new_query, interpreter, memory
    ):
        response += chunk["content"]
        yield response

    # 最終的な応答を履歴に追加する
    g_current_state = STATE_STOP
    response += "\n処理完了！"
    yield response


def auto_chat(interpreter, memory: ConversationBufferWindowMemory):
    print("called auto_chat state=", g_current_state)
    if g_current_state == STATE_STOP:
        # シミュレートされた入力を生成する
        simulated_input = "会話履歴で状況を確認してから自動的に処理を続けてください。"
        for response in chat(interpreter, memory, simulated_input, is_auto=True):
            yield response
    elif g_current_state == STATE_RUNNING:
        print(f"auto_chat skip(state={g_current_state})")
        yield "実行中です。処理完了後に自動実行を継続します。"
    else:
        # STATE_INIT
        print(f"auto_chat skip(state={g_current_state})")
        yield "自動実行するには初回のユーザ指示を出してください。"


def change_state_stop(chatbot, state: str):
    # TODO: delete chat()内で状態遷移が完結するため不要になった
    global g_current_state
    if g_current_state != STATE_RUNNING:
        # この処理はRUNNINGをSTOPにするだけ
        print("change_state_stop(stay) ->", g_current_state)
        return g_current_state

    if chatbot is None or len(chatbot) == 0:
        # あり得ないと思うが念のため再度INITに戻す
        g_current_state = STATE_INIT
        print("change_state_stop(WARN) ->", g_current_state)
        return g_current_state

    show_data_debug(chatbot, "change_state_stop(chatbot)")

    last_output = chatbot[-1]
    last_output_len = len(last_output)
    print("last_output_len=", last_output_len)
    if last_output_len > 1:
        g_current_state = STATE_STOP
        print("change_state_stop ->", g_current_state)
        return g_current_state
    else:
        g_current_state = STATE_RUNNING
        print("change_state_stop ->", g_current_state)
        return g_current_state


def change_state_running_from_stop(state: str):
    # TODO: delete
    global g_current_state
    if g_current_state is STATE_STOP:
        g_current_state = STATE_RUNNING
        print("change_state_running_from_stop ->", STATE_RUNNING)
        return g_current_state
    else:
        print("change_state_running_from_stop(stay) ->", g_current_state)
        return g_current_state


def change_state_running():
    global g_current_state
    g_current_state = STATE_RUNNING
    print("change_state_running ->", g_current_state)
    return g_current_state


def update_state_view():
    print("update_state_view g_current_state=", g_current_state)
    return g_current_state


def create_interface_chat(interpreter, memory):
    print("create_interface_chat start")
    # 部分適用された関数を作成する
    chat_with_llm = partial(chat, interpreter, memory)
    auto_chat_with_llm = partial(auto_chat, interpreter, memory)

    # Gradioインターフェースを複数持つ構成
    with gr.Blocks() as app:
        # state
        state_label = gr.Label(label="state", value=STATE_INIT)
        # chat_iface
        input_textbox = gr.Textbox(
            placeholder="こんにちは！何かお手伝いできることはありますか？",
            container=False,
            scale=7,
            render=False,
        )
        chatbot = gr.Chatbot(
            placeholder="こんにちは！何かお手伝いできることはありますか？",
            container=False,
            scale=7,
            render=False,
        )
        chat_iface = gr.ChatInterface(
            fn=chat_with_llm,
            title="Chatbot",
            description="チャットボットとの会話",
            theme="soft",
            textbox=input_textbox,
            chatbot=chatbot,
            examples=[
                "ステップバイステップで考えて原因を特定してから修正案を検討してください。",
                "設計方針をmarkdownで整理して報告してください。",
                "作成したファイルと配置先を報告してください。",
                "実装内容を自己レビューしてください。",
                "さらなる改善案を提案して内容を精査した上で作業を進めてください。",
            ],
            cache_examples=False,
            retry_btn=None,
            undo_btn="Delete Previous",
            clear_btn="Clear",
        )

        # 外部トリガの結果を表示するためのTextareaBlock
        output_block = gr.Textbox(label="出力メッセージ")

        # 定期実行
        app.load(
            fn=auto_chat_with_llm,
            outputs=[output_block],
            every=10,  # every:sec
        )
        app.load(fn=update_state_view, outputs=[state_label], every=3)

        # イベントチェイン(ボタンを押したらRUNNINGにする)
        chat_iface.textbox.submit(fn=change_state_running, outputs=[state_label])
        chat_iface.submit_btn.click(fn=change_state_running, outputs=[state_label])

        # イベントチェイン(chatbotが終わったらSTOPにする)
        # chatbot.change(
        #     fn=change_state_stop, inputs=[chatbot, state_label], outputs=[state_label]
        # )

    print("create_interface_chat end")
    return app, chat_iface, chatbot


def server(interpreter):
    # チャット履歴を保持するための状態
    print("ConversationBufferWindowMemory created.")
    memory = ConversationBufferWindowMemory(
        k=10,
        memory_key="history",
        input_key="input",
        output_key="output",
        return_messages=True,
    )

    # Gradioインターフェースを作成する
    app, chat_iface, chatbot = create_interface_chat(interpreter, memory)
    app.launch(server_name="0.0.0.0", debug=True)
