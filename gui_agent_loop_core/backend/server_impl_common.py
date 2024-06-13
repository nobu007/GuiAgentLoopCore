import os


def get_agent_image_path(agent_name):
    agent_image_filename = "agent_icon.png"
    if agent_name == "AGENT_EXECUTOR":
        agent_image_filename = "agent_executor_icon.png"
    elif agent_name == "SUPERVISOR":
        agent_image_filename = "supervisor_icon.png"

    RESOURCE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "resource"))
    agent_image_path = os.path.join(RESOURCE_DIR, agent_image_filename)

    if os.path.exists(agent_image_path):
        return agent_image_path
    else:
        print("WARN _get_agent_image_path not exist agent_image_path=", agent_image_path)
        return None


def update_agent_image(agent_name):
    agent_image_path = get_agent_image_path(agent_name)
    if agent_image_path:
        return agent_image_path
    else:
        return "GuiAgentLoopCore/gui_agent_loop_core/backend/resource/agent_icon.png"
