import os

import gradio as gr

from gui_agent_loop_core.core.interpreter_manager import InterpreterManager
from gui_agent_loop_core.schema.backend.schema import GuiBackendType, GuiComponentName
from gui_agent_loop_core.schema.core.schema import AgentName, InterpreterState


def get_gui_common_component(gui_backend_type: GuiBackendType, chat_session: InterpreterManager.ChatSession):
    if gui_backend_type == GuiBackendType.GRADIO:
        agent_name = gr.Label(label="Agent Name", value=AgentName.AGENT_EXECUTOR.value)
        agent_name_radio = gr.Radio(
            choices=[AgentName.AGENT_EXECUTOR.value, AgentName.SUPERVISOR.value],
            value=AgentName.AGENT_EXECUTOR.value,
            label="Select Agent",
        )
        agent_image = gr.Image(
            value=update_agent_image(AgentName.AGENT_EXECUTOR.value), width=128, height=128, label="Agent Image"
        )
        agent_state = gr.Label(label="agent_state", value=InterpreterState.STATE_INIT)
        agent_session = gr.State(chat_session)

        print("agent_session.session_id=", agent_session.value.session_id)

    # callback
    def _notify(agent_name):
        return agent_name

    # on change
    agent_name.change(fn=_notify, inputs=[agent_name], outputs=[agent_name_radio])
    agent_name_radio.change(fn=update_agent_image, inputs=[agent_name_radio], outputs=[agent_image])

    # component_dict
    component_dict = {}
    component_dict[GuiComponentName.AGENT_NAME] = agent_name
    component_dict[GuiComponentName.AGENT_NAME_RADIO] = agent_name_radio
    component_dict[GuiComponentName.AGENT_IMAGE] = agent_image
    component_dict[GuiComponentName.AGENT_STATE] = agent_state
    component_dict[GuiComponentName.AGENT_SESSION] = agent_session

    return component_dict


def get_agent_image_path(agent_name):
    # agent_image_filename
    agent_image_filename = "agent_icon.png"
    if agent_name == AgentName.AGENT_EXECUTOR:
        agent_image_filename = "agent_executor_icon.png"
    elif agent_name == AgentName.SUPERVISOR:
        agent_image_filename = "supervisor_icon.png"
    elif agent_name == AgentName.LLM_PLANNER:
        agent_image_filename = "llm_planner_icon.png"
    elif agent_name == AgentName.THOUGHT:
        agent_image_filename = "thought_icon.png"
    else:
        pass

    # agent_image_path
    RESOURCE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "resource"))
    agent_image_path = os.path.join(RESOURCE_DIR, agent_image_filename)

    if os.path.exists(agent_image_path):
        return agent_image_path
    else:
        print("WARN _get_agent_image_path not exist agent_image_path=", agent_image_path)
        return None


def update_agent_image(agent_name):
    # TODO: use raw image?
    agent_image_path = get_agent_image_path(agent_name)
    if agent_image_path:
        return agent_image_path
    else:
        return ""
