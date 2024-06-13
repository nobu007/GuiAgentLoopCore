import gradio as gr

from gui_agent_loop_core.backend.server_impl_common import update_agent_image
from gui_agent_loop_core.core.interpreter_manager import InterpreterManager

STATE_INIT = "init"
STATE_RUNNING = "running"
STATE_STOP = "stop"
g_last_user_message_content = "N/A"
g_current_state = STATE_INIT


def _create_interface_chat(interpreter_manager: InterpreterManager):
    print("create_interface_chat start")

    # Gradioインターフェースを複数持つ構成
    with gr.Blocks() as app:
        # image
        agent_image = gr.Image(value=update_agent_image("AGENT_EXECUTOR"), width=128, height=128, label="Agent Image")
        # state
        state_label = gr.Label(label="state", value=STATE_INIT)
        # agentの種類を表示するためのLabel
        agent_name_label = gr.Label(label="Agent Name", value="")
        # session
        agent_session = gr.State(interpreter_manager.create_session_instance())
        print("agent_session.session_id=", agent_session.value.session_id)

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
            fn=interpreter_manager.chat,
            title="Chatbot",
            description=f"チャットボット({agent_name_label})との会話",
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

        # agent_name_labelの出力が変更されたときにagentのアイコンを更新
        agent_name_label.change(
            fn=update_agent_image,
            inputs=[agent_name_label],
            outputs=[agent_image],
        )

        # 定期実行(auto_chat)
        app.load(
            fn=interpreter_manager.auto_chat,
            outputs=[output_block],
            every=60,  # every:sec
        )
        # 定期実行(STATE_STOP検知)
        app.load(fn=interpreter_manager.update_state_view, outputs=[state_label], every=3)
        # 定期実行(agent_name検知)
        app.load(fn=interpreter_manager.update_agent_name_view, outputs=[agent_name_label], every=3)

        # イベントチェイン(ボタンを押したらRUNNINGにする)
        chat_iface.textbox.submit(fn=interpreter_manager.change_state_running, outputs=[state_label])
        chat_iface.submit_btn.click(fn=interpreter_manager.change_state_running, outputs=[state_label])

    print("create_interface_chat end")
    return app, chat_iface, chatbot


def server(interpreter_manager: InterpreterManager):
    # Gradioインターフェースを作成する
    app, _, _ = _create_interface_chat(interpreter_manager)
    app.launch(server_name="0.0.0.0", debug=True)
