import os

import gradio as gr

from gui_agent_loop_core.core.interpreter_manager import InterpreterManager
from gui_agent_loop_core.schema.schema import (
    GuiAgentInterpreterABC,
    GuiAgentInterpreterChatRequestAny,
    GuiAgentInterpreterChatResponseAny,
)


def _get_agent_image_path(agent_name):
    agent_image_filename = "agent_icon.png"
    if agent_name == "AGENT_EXECUTOR":
        agent_image_filename = "agent_executor_icon.png"
    elif agent_name == "SUPERVISOR":
        agent_image_filename = "supervisor_icon.png"

    RESOURCE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../resource"))
    agent_image_path = os.path.join(RESOURCE_DIR, agent_image_filename)

    if os.path.exists(agent_image_path):
        return agent_image_path
    else:
        print("WARN _get_agent_image_path not exist agent_image_path=", agent_image_path)
        return None


def _update_agent_image(agent_name):
    agent_image_path = _get_agent_image_path(agent_name)
    if agent_image_path:
        return agent_image_path
    else:
        return "GuiAgentLoopCore/gui_agent_loop_core/backend/resource/agent_icon.png"


def sandbox_server(interpreter_manager: InterpreterManager):
    with gr.Blocks() as app:
        agent_name = gr.Label(label="Agent Name", value="AGENT_EXECUTOR")
        agent_name_radio = gr.Radio(
            choices=["AGENT_EXECUTOR", "SUPERVISOR"], value="AGENT_EXECUTOR", label="Select Agent"
        )
        agent_image = gr.Image(value=_update_agent_image("AGENT_EXECUTOR"), width=128, height=128, label="Agent Image")
        agent_session = gr.State(interpreter_manager.create_session_instance())
        print("agent_session.session_id=", agent_session.value.session_id)

        def _change_agent(agent_name):
            print("_change_agent agent_name=", agent_name)
            if agent_name == "AGENT_EXECUTOR":
                print("  ->", "SUPERVISOR")
                return "SUPERVISOR"
            else:
                print("  ->", "AGENT_EXECUTOR")
                return "AGENT_EXECUTOR"

        def _notify(agent_name):
            print("_notify agent_name=", agent_name)
            return agent_name

        def _update_image(agent_name):
            print("_update_image agent_name=", agent_name)
            return _update_agent_image(agent_name)

        # agent_name_radio.change(fn=_update_image, inputs=[agent_name_radio], outputs=[agent_image])
        app.load(
            fn=_change_agent,
            inputs=[agent_name],
            outputs=[agent_name_radio],
            every=3,
        )
        agent_name.change(fn=_notify, inputs=[agent_name], outputs=[agent_name_radio])
        agent_name_radio.change(fn=_update_image, inputs=[agent_name_radio], outputs=[agent_image])

    app.queue()
    app.launch(server_name="0.0.0.0", debug=True)


class DummyGuiAgentInterpreter(GuiAgentInterpreterABC):
    def chat_core(
        self,
        request_core: GuiAgentInterpreterChatRequestAny,
        display: bool = False,
        stream: bool = False,
        blocking: bool = False,
    ) -> GuiAgentInterpreterChatResponseAny:
        print("display=", display)
        print("stream=", stream)
        print("blocking=", blocking)
        return request_core


if __name__ == "__main__":
    interpreter_ = DummyGuiAgentInterpreter()
    interpreter_manager_ = InterpreterManager(interpreter_)
    sandbox_server(interpreter_manager_)
