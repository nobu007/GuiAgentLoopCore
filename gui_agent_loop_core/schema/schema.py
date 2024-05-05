import enum
import inspect
from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, Optional, Type, TypeVar, Union, get_args

from langchain.memory import ConversationBufferWindowMemory
from langchain.memory.chat_memory import BaseChatMessageHistory
from pydantic import BaseModel, Field, model_validator, validate_call


class ChatMessage(BaseModel):
    class Role(str, enum.Enum):
        USER = "user"
        SYSTEM = "system"
        ASSISTANT = "assistant"

        TOOL = "tool"
        """May be used for the result of tool calls"""
        FUNCTION = "function"
        """May be used for the return value of function calls"""

    role: Role
    content: str

    @staticmethod
    def user(content: str) -> "ChatMessage":
        return ChatMessage(role=ChatMessage.Role.USER, content=content)

    @staticmethod
    def system(content: str) -> "ChatMessage":
        return ChatMessage(role=ChatMessage.Role.SYSTEM, content=content)


ChatMessagesAny = Union[str, ChatMessage, list[ChatMessage]]
ChatMessagesFix = list[ChatMessage]
ChatMessages = Union[ChatMessage, list[ChatMessage]]


class InterpreterState(str, enum.Enum):
    STATE_INIT = "init"
    STATE_RUNNING = "running"
    STATE_STOP = "stop"


class GuiAgentInterpreterABC(ABC):
    @validate_call
    @abstractmethod
    def chat(
        self, message: ChatMessages, display: bool = False, stream: bool = False, blocking: bool = False
    ) -> ChatMessages:
        pass


class GuiAgentInterpreterBase(GuiAgentInterpreterABC):
    def chat(
        self, message: ChatMessages, display: bool = False, stream: bool = False, blocking: bool = False
    ) -> ChatMessages:
        return message


class GuiAgentInterpreterSampleNG:
    def chat(self, message: str, display: bool = False, stream: bool = False, blocking: bool = False) -> ChatMessages:
        return message


class GuiAgentInterpreterSampleOK:
    def chat(
        self, message: ChatMessages, display: bool = False, stream: bool = False, blocking: bool = False
    ) -> ChatMessages:
        return message


def validate_method_signature(obj: Any, abc_class: Type, method_name: str):
    """
    Validates the signature of a method in an object against the signature of a method in an abstract base class.

    Args:
        obj: The object to validate.
        abc_class: The abstract base class to compare against.
        method_name: The name of the method to validate.

    Raises:
        ValueError: If the object does not have the specified method, the method is not callable,
                    the number of parameters does not match, or the parameter names and annotations do not match.
    """
    if not hasattr(obj, method_name):
        raise ValueError(f'Object must have a {method_name} method')

    method = getattr(obj, method_name)
    if not callable(method):
        raise ValueError(f'Object.{method_name} must be callable')

    # Get the signature of the ABC's method
    expected_signature = inspect.signature(getattr(abc_class, method_name))

    # Get the signature of the object's method
    actual_signature = inspect.signature(method)

    # Adjust the number of parameters for member functions
    expected_params = list(expected_signature.parameters.values())
    if expected_params[0].name == 'self':
        expected_params = expected_params[1:]

    actual_params = list(actual_signature.parameters.values())
    if actual_params[0].name == 'self':
        actual_params = actual_params[1:]

    # Check if the number of parameters matches
    if len(expected_params) != len(actual_params):
        raise ValueError(
            f'Object.{method_name} has an incompatible number of parameters. Expected: {len(expected_params)}, Actual: {len(actual_params)}'
        )

    # Check if the parameter names and annotations match
    for expected_param, actual_param in zip(expected_params, actual_params):
        if expected_param.name != actual_param.name:
            raise ValueError(
                f'Object.{method_name} has an incompatible parameter name. Expected: {expected_param.name}, Actual: {actual_param.name}'
            )

        if expected_param.annotation != actual_param.annotation:
            if (
                expected_param.annotation is inspect.Parameter.empty
                or actual_param.annotation is inspect.Parameter.empty
            ):
                continue
            raise ValueError(
                f'Object.{method_name} parameter "{expected_param.name}" has an incompatible type annotation. Expected: {expected_param.annotation}, Actual: {actual_param.annotation}'
            )


class GuiAgentInterpreterManagerBase(BaseModel):
    _interpreter: Optional[GuiAgentInterpreterABC] = None
    memory: Optional[Any] = None  # TODO: change BaseChatMessageHistory(but error occur)
    last_user_message_content: Optional[str] = None

    current_state: InterpreterState = InterpreterState.STATE_INIT

    def __init__(self, interpreter: GuiAgentInterpreterABC):
        validate_method_signature(interpreter, GuiAgentInterpreterABC, 'chat')

        super().__init__()
        self._interpreter = interpreter
        self.memory = ConversationBufferWindowMemory(
            k=10,
            memory_key="history",
            input_key="input",
            output_key="output",
            return_messages=True,
        )
        self.last_user_message_content = ""
        self.current_state = InterpreterState.STATE_INIT

    @property
    def interpreter(self):
        # read_only. should not use self._interpreter directly.
        return self._interpreter

    @validate_call
    def chat(self, new_query: str, is_auto: bool = False) -> str:
        print("is_auto=", is_auto)
        return new_query

    @validate_call
    def auto_chat(self) -> str:
        return ""

    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True


if __name__ == "__main__":
    interpreter_ng = GuiAgentInterpreterSampleNG()
    interpreter_ok = GuiAgentInterpreterSampleOK()
    manager = GuiAgentInterpreterManagerBase(interpreter_ok)
    manager._interpreter = interpreter_ng  # This is OK. But W0212:protected-access is occur.
    print(manager)
