from typing import Any, Dict, List, Type, Union

from pydantic import BaseModel

from gui_agent_loop_core.converter.base_converter import BaseConverter
from gui_agent_loop_core.schema.schema import GuiAgentInterpreterChatResponse, GuiAgentInterpreterChatResponseAny

CoreAny = Union[str, BaseModel, List[BaseModel]]


class ResponseConverterStr(BaseConverter):
    def to_str_from_core(
        self,
        core_any: GuiAgentInterpreterChatResponseAny,
        core_class: Type[BaseModel] = GuiAgentInterpreterChatResponseAny,
    ) -> List[str]:
        core_list = super().to_dict_from_core(core_any, core_class)
        str_list = []
        for core in core_list:
            str_list.append(str(core))
        return "\n\n\n".join(str_list)

    def to_core_from_single_str(self, single_str: str) -> GuiAgentInterpreterChatResponse:
        core_request = GuiAgentInterpreterChatResponse(content=single_str)
        return core_request


if __name__ == "__main__":
    pass
