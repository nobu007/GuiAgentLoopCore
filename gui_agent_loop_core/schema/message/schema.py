import enum
import inspect
from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Generator, List, Optional, Type, Union, get_args, get_origin

from langchain.memory import ConversationBufferWindowMemory
from pydantic import BaseModel, validate_call

from gui_agent_loop_core.schema.core.schema import AgentName, InterpreterState


class GuiAgentInterpreterChatMessage(BaseModel):
    """First message to GuiAgentInterpreter"""

    class Type(str, enum.Enum):
        MESSAGE = "message"
        CODE = "code"
        CONFIRMATION = "confirmation"
        CONSOLE = "console"
        IMAGE = "image"
        # TODO: fix

        """May be used for the result of tool calls"""
        FUNCTION = "function"
        """May be used for the return value of function calls"""

        def __str__(self):
            return self.value

        def __repr__(self):
            return self.value

    class Role(str, enum.Enum):
        USER = "user"
        SYSTEM = "system"
        ASSISTANT = "assistant"
        COMPUTER = "computer"

        # TODO: fix
        TOOL = "tool"
        """May be used for the result of tool calls"""
        FUNCTION = "function"
        """May be used for the return value of function calls"""

        def __str__(self):
            return self.value

        def __repr__(self):
            return self.value

    type: Optional[Type] = Type.MESSAGE
    role: Optional[Role] = Role.USER
    content: Optional[str] = ""

    @staticmethod
    def user(content: str) -> "GuiAgentInterpreterChatMessage":
        return GuiAgentInterpreterChatMessage(role=GuiAgentInterpreterChatMessage.Role.USER, content=content)

    @staticmethod
    def system(content: str) -> "GuiAgentInterpreterChatMessage":
        return GuiAgentInterpreterChatMessage(role=GuiAgentInterpreterChatMessage.Role.SYSTEM, content=content)

    def __str__(self):
        return "(GAI msg)role:" + self.role + ", content:" + self.content

    def __repr__(self):
        return "(GAI msg)role:" + self.role + ", content:" + self.content


class GuiAgentInterpreterChatResponse(GuiAgentInterpreterChatMessage):
    """Response message from GuiAgentInterprete"""

    class Format(str, enum.Enum):
        ACTIVE_LINE = "active_line"
        OUTPUT = "output"
        BASE64_PNG = "base64.png"
        EXECUTION = "execution"
        PYTHON = "python"
        # TODO: fix

        def __str__(self):
            return self.value

        def __repr__(self):
            return self.value

    format: Optional[Format] = Format.OUTPUT
    code: Optional[str] = ""  # working change(may nothing set)
    language: Optional[str] = ""  # working change(may nothing set)
    start: Optional[bool] = False  # indicate first frame of chunks
    end: Optional[bool] = False  # indicate last frame of chunks
    agent_name: Optional[AgentName] = AgentName.OTHER

    @staticmethod
    def user(content: str) -> "GuiAgentInterpreterChatResponse":
        return GuiAgentInterpreterChatResponse(role=GuiAgentInterpreterChatMessage.Role.USER, content=content)

    @staticmethod
    def system(content: str) -> "GuiAgentInterpreterChatResponse":
        return GuiAgentInterpreterChatResponse(role=GuiAgentInterpreterChatMessage.Role.SYSTEM, content=content)

    def __str__(self):
        return "(GAI res)role:" + self.role + ", content:" + self.content

    def __repr__(self):
        return "(GAI res)role:" + self.role + ", content:" + self.content


class GuiAgentInterpreterChatRequest(GuiAgentInterpreterChatResponse):
    """Second or later message to GuiAgentInterprete
    This class handle multi turn conversation."""

    @staticmethod
    def user(content: str) -> "GuiAgentInterpreterChatRequest":
        return GuiAgentInterpreterChatRequest(role=GuiAgentInterpreterChatMessage.Role.USER, content=content)

    @staticmethod
    def system(content: str) -> "GuiAgentInterpreterChatRequest":
        return GuiAgentInterpreterChatRequest(role=GuiAgentInterpreterChatMessage.Role.SYSTEM, content=content)

    def __str__(self):
        return "(GAI req)role:" + self.role + ", content:" + self.content

    def __repr__(self):
        return "(GAI req)role:" + self.role + ", content:" + self.content


# Naming rules
# classList = List[class]
# classs    = class or List[class]
# classAny  = str or class or List[class]
# classAny  = class or Generator or AsyncGenerator ※response only
GuiAgentInterpreterChatMessageList = List[GuiAgentInterpreterChatMessage]
GuiAgentInterpreterChatMessages = Union[GuiAgentInterpreterChatMessage, List[GuiAgentInterpreterChatMessage]]
GuiAgentInterpreterChatMessagesAny = Union[str, GuiAgentInterpreterChatMessage, List[GuiAgentInterpreterChatMessage]]
GuiAgentInterpreterChatResponseGenerator = Generator[GuiAgentInterpreterChatResponse, None, None]
GuiAgentInterpreterChatResponseAny = Union[
    GuiAgentInterpreterChatResponse,
    Generator[GuiAgentInterpreterChatResponse, None, None],
    AsyncGenerator[str, None],
]
GuiAgentInterpreterChatResponseAnyAsync = Union[
    GuiAgentInterpreterChatResponse,
    AsyncGenerator[GuiAgentInterpreterChatResponse, None],
]
GuiAgentInterpreterChatResponseStr = str

GuiAgentInterpreterChatRequestList = List[GuiAgentInterpreterChatRequest]
GuiAgentInterpreterChatRequests = Union[GuiAgentInterpreterChatRequest, List[GuiAgentInterpreterChatRequest]]
GuiAgentInterpreterChatRequestAny = Union[
    str,
    GuiAgentInterpreterChatRequest,
    GuiAgentInterpreterChatRequestList,
]


class GuiAgentInterpreterABC(ABC):
    @validate_call
    @abstractmethod
    def chat_core(
        self,
        request_core: GuiAgentInterpreterChatRequestAny,
        display: bool = False,
        stream: bool = False,
        blocking: bool = False,
    ) -> GuiAgentInterpreterChatResponseAny:
        pass


class GuiAgentInterpreterBase(GuiAgentInterpreterABC):
    def chat_core(
        self,
        request_core: GuiAgentInterpreterChatRequestAny,
        display: bool = False,
        stream: bool = False,
        blocking: bool = False,
    ) -> GuiAgentInterpreterChatResponseAny:
        response = GuiAgentInterpreterChatResponse()
        return response


class GuiAgentInterpreterSampleOK:
    def chat_core(
        self,
        request_core: GuiAgentInterpreterChatRequestAny,
        display: bool = False,
        stream: bool = False,
        blocking: bool = False,
    ) -> GuiAgentInterpreterChatResponseAny:
        response = GuiAgentInterpreterChatResponse()
        return response


class GuiAgentInterpreterSamplePramNG:
    def chat_core(
        self,
        request_core: str,
        display: bool = False,
        stream: bool = False,
        blocking: bool = False,
    ) -> GuiAgentInterpreterChatResponseAny:
        response = GuiAgentInterpreterChatResponse()
        return response


class GuiAgentInterpreterSampleReturnNG:
    def chat_core(
        self,
        request_core: GuiAgentInterpreterChatRequestAny,
        display: bool = False,
        stream: bool = False,
        blocking: bool = False,
    ) -> str:
        return ""


def validate_parameter_signature(
    expected_params: List[inspect.Parameter],
    actual_params: List[inspect.Parameter],
    method_name: str,
):
    """
    Validates the parameter signatures of a method.

    Args:
        expected_params: The expected parameters from the abstract base class.
        actual_params: The actual parameters from the object's method.
        method_name: The name of the method being validated.

    Raises:
        ValueError: If the number of parameters does not match, or the parameter names and annotations do not match.
    """
    # Check if the number of parameters matches
    if len(expected_params) != len(actual_params):
        raise ValueError(
            f"Object.{method_name} has an incompatible number of parameters. Expected: {len(expected_params)}, Actual: {len(actual_params)}"
        )

    # Check if the parameter names and annotations match
    for expected_param, actual_param in zip(expected_params, actual_params):
        if expected_param.name != actual_param.name:
            raise ValueError(
                f"Object.{method_name} has an incompatible parameter name. Expected: {expected_param.name}, Actual: {actual_param.name}"
            )

        expected_annotation = expected_param.annotation
        actual_annotation = actual_param.annotation

        if expected_annotation is inspect.Parameter.empty or actual_annotation is inspect.Parameter.empty:
            continue

        # Check if the expected annotation is Optional
        expected_is_optional = get_origin(expected_annotation) is Optional

        if expected_is_optional:
            # If the expected annotation is Optional, compare the inner type with the actual annotation
            expected_inner_type = get_args(expected_annotation)[0]
            if expected_inner_type != actual_annotation:
                raise ValueError(
                    f'Object.{method_name} parameter "{expected_param.name}" has an incompatible type annotation. Expected: {expected_annotation}, Actual: {actual_annotation}'
                )
        else:
            # If the expected annotation is not Optional, compare the annotations directly
            if expected_annotation != actual_annotation:
                raise ValueError(
                    f'Object.{method_name} parameter "{expected_param.name}" has an incompatible type annotation. Expected: {expected_annotation}, Actual: {actual_annotation}'
                )


def validate_return_signature(
    expected_signature: inspect.Signature,
    actual_signature: inspect.Signature,
    method_name: str,
):
    """
    Validates the return signature of a method.

    Args:
        expected_signature: The expected signature from the abstract base class.
        actual_signature: The actual signature from the object's method.
        method_name: The name of the method being validated.

    Raises:
        ValueError: If the return annotation does not match.
    """
    expected_return_annotation = expected_signature.return_annotation
    actual_return_annotation = actual_signature.return_annotation

    if expected_return_annotation != actual_return_annotation:
        if expected_return_annotation is inspect.Signature.empty or actual_return_annotation is inspect.Signature.empty:
            return
        raise ValueError(
            f"Object.{method_name} has an incompatible return annotation. Expected: {expected_return_annotation}, Actual: {actual_return_annotation}"
        )


def validate_method_signature(obj: Any, abc_class: Type, method_name: str):
    """
    Validates the signature of a method in an object against the signature of a method in an abstract base class.

    Args:
        obj: The object to validate.
        abc_class: The abstract base class to compare against.
        method_name: The name of the method to validate.

    Raises:
        ValueError: If the object does not have the specified method, the method is not callable,
                    the parameter signatures do not match, or the return signature does not match.
    """
    if not hasattr(obj, method_name):
        raise ValueError(f"Object must have a {method_name} method")

    method = getattr(obj, method_name)
    if not callable(method):
        raise ValueError(f"Object.{method_name} must be callable")

    # Get the signature of the ABC's method
    expected_signature = inspect.signature(getattr(abc_class, method_name))

    # Get the signature of the object's method
    actual_signature = inspect.signature(method)

    # Adjust the number of parameters for member functions
    expected_params = list(expected_signature.parameters.values())
    if expected_params[0].name == "self":
        expected_params = expected_params[1:]

    actual_params = list(actual_signature.parameters.values())
    if actual_params[0].name == "self":
        actual_params = actual_params[1:]

    # Validate the parameter signatures
    validate_parameter_signature(expected_params, actual_params, method_name)

    # Validate the return signature
    validate_return_signature(expected_signature, actual_signature, method_name)


class GuiAgentInterpreterManagerBase(BaseModel):
    _interpreter: Optional[GuiAgentInterpreterABC] = None
    memory: Optional[Any] = None  # TODO: change BaseChatMessageHistory(but error occur)
    last_user_message_content: Optional[str] = None
    current_state: InterpreterState = InterpreterState.STATE_INIT
    agent_name: Optional[str] = ""
    chat_manager: Optional[Any] = None
    secret_key: Optional[str] = ""

    def __init__(self, interpreter: GuiAgentInterpreterABC):
        validate_method_signature(interpreter, GuiAgentInterpreterABC, "chat_core")

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

    class ConfigDict:
        arbitrary_types_allowed = True
        validate_assignment = True


if __name__ == "__main__":
    # TODO: move to unittest
    interpreter_param_ng = GuiAgentInterpreterSamplePramNG()
    interpreter_return_ng = GuiAgentInterpreterSampleReturnNG()
    interpreter_ok = GuiAgentInterpreterSampleOK()
    manager = GuiAgentInterpreterManagerBase(interpreter_ok)
    manager._interpreter = interpreter_return_ng  # This is OK. But W0212:protected-access is occur.
    print(manager)
