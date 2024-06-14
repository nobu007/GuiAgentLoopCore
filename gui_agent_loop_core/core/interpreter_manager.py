import uuid
from typing import Generator, Tuple

import jwt
from langchain.memory import ConversationBufferWindowMemory

from gui_agent_loop_core.schema.message.schema import AgentName, GuiAgentInterpreterManagerBase, InterpreterState
from gui_agent_loop_core.util.message_format import show_data_debug
from gui_agent_loop_core.util.message_process import process_messages_gradio


class InterpreterManager(GuiAgentInterpreterManagerBase):
    class ChatSession:
        def __init__(self, session_id):
            self.session_id = session_id
            self.messages = []

        def add_message(self, message):
            self.messages.append(message)

        def get_messages(self):
            return self.messages

    class ChatManager:
        def __init__(self):
            self.sessions = {}

        def create_session(self):
            session_id = str(uuid.uuid4())
            session = InterpreterManager.ChatSession(session_id)
            self.sessions[session_id] = session
            return session

        def get_session(self, session_id):
            return self.sessions.get(session_id)

    def create_session_instance(self):
        session = self.chat_manager.create_session()
        return session

    def create_jwt_session_token(self):
        session = self.create_session_instance()
        session_id = session.session_id

        # セッションIDをJWTに埋め込む
        token = jwt.encode({'session_id': session_id}, self.secret_key, algorithm='HS256')

        return token

    def jwt_decode_session(self):
        # JWTをデコードしてセッションIDを取得
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        session_id = payload['session_id']
        return payload

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
        self.current_state: InterpreterState = InterpreterState.STATE_INIT
        self.agent_name: AgentName = AgentName.OTHER

        # session
        self.chat_manager = InterpreterManager.ChatManager()
        self.secret_key = 'jwt_secret_key_2571'  # JWTの署名に使用するシークレットキー

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
            print("chat chunk.agent_name=", chunk.agent_name)
            if chunk.agent_name != str(AgentName.OTHER):
                self.agent_name = chunk.agent_name
                print("chat agent_name=", self.agent_name)
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
