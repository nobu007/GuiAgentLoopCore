import gradio as gr

from gui_agent_loop_core.backend.server_impl_common import get_gui_common_component
from gui_agent_loop_core.core.interpreter_manager import InterpreterManager
from gui_agent_loop_core.schema.backend.schema import GuiBackendType, GuiComponentName
from gui_agent_loop_core.schema.message.schema import (
    AgentName,
    GuiAgentInterpreterABC,
    GuiAgentInterpreterChatMessage,
    GuiAgentInterpreterChatRequestAny,
    GuiAgentInterpreterChatResponse,
    GuiAgentInterpreterChatResponseAny,
)


def sandbox_server(interpreter_manager: InterpreterManager):
    with gr.Blocks() as app:
        component_dict = get_gui_common_component(GuiBackendType.GRADIO, interpreter_manager.create_session_instance())
        agent_name = component_dict[GuiComponentName.AGENT_NAME]
        agent_name_radio = component_dict[GuiComponentName.AGENT_NAME_RADIO]
        agent_image = component_dict[GuiComponentName.AGENT_IMAGE]
        agent_state = component_dict[GuiComponentName.AGENT_STATE]
        agent_session = component_dict[GuiComponentName.AGENT_SESSION]
        print("agent_session.session_id=", agent_session.value.session_id)

        def _change_agent(agent_name):
            print("_change_agent agent_name=", agent_name)
            if agent_name == AgentName.AGENT_EXECUTOR.value:
                return AgentName.SUPERVISOR.value
            else:
                return AgentName.AGENT_EXECUTOR.value

        app.load(
            fn=_change_agent,
            inputs=[agent_name],
            outputs=[agent_name_radio],
            every=3,
        )

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

        response_core = GuiAgentInterpreterChatResponse()
        response_core.role = GuiAgentInterpreterChatMessage.Role.ASSISTANT
        response_core.content = request_core.content + "\nchat_core response."
        return response_core


if __name__ == "__main__":
    interpreter_ = DummyGuiAgentInterpreter()
    interpreter_manager_ = InterpreterManager(interpreter_)
    sandbox_server(interpreter_manager_)
