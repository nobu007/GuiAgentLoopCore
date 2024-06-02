import gradio as gr

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
        agent_image = gr.Image(width=128, height=128, label="Agent Image", value="resource/agent_icon.png")
        # state
        state_label = gr.Label(label="state", value=STATE_INIT)
        # agentの種類を表示するためのLabel
        agent_name_label = gr.Label(label="Agent Name", value="")
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

        def update_agent_image(agent_name):
            agent_image_path = "resource/agent_icon.png"
            if agent_name == "agent_executor":
                agent_image_path = "resource/agent_executor_icon.png"
            elif agent_name == "supervisor":
                agent_image_path = "resource/supervisor.png"
            elif agent_name == "llm_planner":
                agent_image_path = "resource/llm_planner_icon.png"
            elif agent_name == "thought":
                agent_image_path = "resource/thought_icon.png"
            else:
                pass
            return agent_image_path

        # agent_name_labelの出力が変更されたときにagentのアイコンを更新
        agent_name_label.change(
            fn=update_agent_image,
            inputs=[agent_name_label],
            outputs=[agent_image],
        )

        # 定期実行
        app.load(
            fn=interpreter_manager.auto_chat,
            outputs=[output_block],
            every=60,  # every:sec
        )
        app.load(fn=interpreter_manager.update_state_view, outputs=[state_label], every=3)
        app.load(fn=interpreter_manager.update_agent_name_view, outputs=[agent_name_label], every=3)

        # イベントチェイン(ボタンを押したらRUNNINGにする)
        chat_iface.textbox.submit(fn=interpreter_manager.change_state_running, outputs=[state_label])
        chat_iface.submit_btn.click(fn=interpreter_manager.change_state_running, outputs=[state_label])

        # イベントチェイン(chatbotが終わったらSTOPにする)
        # chatbot.change(
        #     fn=change_state_stop, inputs=[chatbot, state_label], outputs=[state_label]
        # )

    print("create_interface_chat end")
    return app, chat_iface, chatbot


def server(interpreter_manager: InterpreterManager):
    # Gradioインターフェースを作成する
    app, _, _ = _create_interface_chat(interpreter_manager)
    app.launch(server_name="0.0.0.0", debug=True)
