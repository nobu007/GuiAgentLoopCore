"""Main module."""

from gui_agent_loop_core.core.interpreter_manager import InterpreterManager
from gui_agent_loop_core.backend.server_impl_gradio import server


class GuiAgentLoopCore:
    def __init__(self) -> None:
        pass

    def launch_server(self, interpreter):
        interpreter_manager = InterpreterManager(interpreter)
        server(interpreter_manager)
