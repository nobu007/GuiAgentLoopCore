import enum


class GuiBackendType(str, enum.Enum):
    GRADIO = "gradio"
    STREAMSYNC = "streamsync"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class GuiComponentName(str, enum.Enum):
    AGENT_NAME = "agent_name"
    AGENT_NAME_RADIO = "agent_name_radio"
    AGENT_IMAGE = "agent_image"
    AGENT_STATE = "agent_state"
    AGENT_SESSION = "agent_session"
    CHATBOT = "chatbot"
    INPUT_TEXTBOX = "input_textbox"
    CHAT_IFACE = "chat_iface"
    OUTPUT_BLOCK = "output_block"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value
