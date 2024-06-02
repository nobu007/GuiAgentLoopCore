from typing import Generator, Tuple

from langchain.memory import ConversationBufferWindowMemory

from gui_agent_loop_core.schema.schema import (
    GuiAgentInterpreterABC,
    GuiAgentInterpreterChatMessage,
    GuiAgentInterpreterChatRequest,
    GuiAgentInterpreterChatRequestList,
    GuiAgentInterpreterChatResponse,
    GuiAgentInterpreterChatResponseAny,
    GuiAgentInterpreterChatResponseAnyAsync,
    GuiAgentInterpreterChatResponseGenerator,
    GuiAgentInterpreterManagerBase,
    InterpreterState,
)
from gui_agent_loop_core.util.message_format import show_data_debug
from gui_agent_loop_core.util.message_process import process_messages_gradio


class InterpreterManager(GuiAgentInterpreterManagerBase):
    def __init__(self, interpreter):
        super().__init__(interpreter)
        self.memory = ConversationBufferWindowMemory(
            k=10,
            memory_key="history",
            input_key="input",
            output_key="output",
            return_messages=True,
        )
        self.last_user_message_content = "N/A"
        self.current_state = InterpreterState.STATE_INIT
        self.agent_name = ""

    # チャットボットの応答を生成する関数
    def chat(self, new_query: str, is_auto=False) -> Generator[Tuple[str], Tuple[str], None]:
        show_data_debug(new_query, "new_query")
        if not new_query:
            print("skip no input")
            return

        # store last_user_message_content
        if not is_auto:
            self.last_user_message_content = new_query

        # Start a separate task for processing messages
        self.current_state = InterpreterState.STATE_RUNNING
        print("chat self.current_state=", self.current_state)
        response = ""
        for chunk in process_messages_gradio(self.last_user_message_content, new_query, self.interpreter, self.memory):
            response += chunk.content
            self.agent_name = chunk.agent_name
            yield response

        # 最終的な応答を履歴に追加する
        self.current_state = InterpreterState.STATE_STOP
        print("chat self.current_state=", self.current_state)
        response += "\n処理完了！"
        yield response

    def auto_chat(self) -> Generator[Tuple[str], Tuple[str], None]:
        print("auto_chat self.current_state=", self.current_state)
        if self.current_state == InterpreterState.STATE_STOP:
            # シミュレートされた入力を生成する
            simulated_input = "会話履歴で状況を確認してから自動的に処理を続けてください。"
            self.current_state = InterpreterState.STATE_RUNNING
            yield from self.chat(simulated_input, is_auto=True)
        elif self.current_state == InterpreterState.STATE_RUNNING:
            yield "実行中です。処理完了後に自動実行を継続します。"
        else:
            yield "自動実行するには初回のユーザ指示を出してください。"

    def change_state_running(self):
        self.current_state = InterpreterState.STATE_RUNNING
        return self.current_state

    def update_state_view(self):
        print("update_state_view self.current_state=", self.current_state)
        return self.current_state

    def update_agent_name_view(self):
        print("update_agent_name_view self.agent_name=", self.agent_name)
        return self.agent_name
