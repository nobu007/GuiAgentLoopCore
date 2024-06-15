import os

import gradio as gr

from gui_agent_loop_core.backend.server_impl_common import get_gui_common_component
from gui_agent_loop_core.core.interpreter_manager import InterpreterManager
from gui_agent_loop_core.schema.backend.schema import GuiBackendType, GuiComponentName


def _create_interface_chat(interpreter_manager: InterpreterManager):
    print("create_interface_chat start")

    # Gradioインターフェースを複数持つ構成
    with gr.Blocks() as app:
        component_dict = get_gui_common_component(GuiBackendType.GRADIO, interpreter_manager.create_session_instance())
        agent_name = component_dict[GuiComponentName.AGENT_NAME]
        agent_name_radio = component_dict[GuiComponentName.AGENT_NAME_RADIO]
        agent_image = component_dict[GuiComponentName.AGENT_IMAGE]
        agent_state = component_dict[GuiComponentName.AGENT_STATE]
        agent_session = component_dict[GuiComponentName.AGENT_SESSION]

        # chat_iface
        input_textbox = gr.Textbox(
            placeholder="こんにちは！何かお手伝いできることはありますか？",
            container=False,
            scale=7,
            render=False,
            value=os.environ.get("INITIAL_PROMPT"),
        )
        chatbot = gr.Chatbot(
            placeholder="ここにAIの出力結果が表示されます",
            container=False,
            scale=7,
            render=False,
        )
        chat_iface = gr.ChatInterface(
            fn=interpreter_manager.chat,
            title="Chatbot",
            description=f"チャットボット({agent_name})との会話",
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

        # 定期実行(auto_chat)
        app.load(
            fn=interpreter_manager.auto_chat,
            outputs=[output_block],
            every=60,  # every:sec
        )
        # 定期実行(STATE_STOP検知)
        app.load(fn=interpreter_manager.update_state_view, outputs=[agent_state], every=3)
        # 定期実行(agent_name検知)
        app.load(fn=interpreter_manager.update_agent_name_view, outputs=[agent_name], every=3)

        # イベントチェイン(ボタンを押したらRUNNINGにする)
        chat_iface.textbox.submit(fn=interpreter_manager.change_state_running, outputs=[agent_state])
        chat_iface.submit_btn.click(fn=interpreter_manager.change_state_running, outputs=[agent_state])

    print("create_interface_chat end")
    return app, chat_iface, chatbot


def server(interpreter_manager: InterpreterManager):
    # Gradioインターフェースを作成する
    app, _, _ = _create_interface_chat(interpreter_manager)
    app.launch(server_name="0.0.0.0", debug=True)
