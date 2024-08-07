import enum
from typing import Any, Dict, Optional

from langchain_core.prompts.chat import BaseMessagePromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate
from pydantic import BaseModel


class AgentType(str, enum.Enum):
    TOOL_CALLING = "tool_calling"
    STRUCTURED_CHAT = "structured_chat"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class AgentDefinition(BaseModel):
    agent_name: Optional[str] = ""
    agent_type: Optional[AgentType] = AgentType.STRUCTURED_CHAT
    agent_role: Optional[str] = ""
    agent: Optional[Any] = None
    agent_executor: Optional[Any] = None
    prompt: Optional[ChatPromptTemplate] = None
    prompt_dict: Optional[Dict[str, Any]] = None
    message_prompt_template: Optional[BaseMessagePromptTemplate] = None

    def build_prompt(self):
        if self.prompt is None and self.prompt_dict:
            template = self.prompt_dict.get("template")
            if template:
                self.message_prompt_template = HumanMessagePromptTemplate.from_template(template)
