from typing import Any, Dict, List, Optional, Type, Union

from pydantic import BaseModel, ValidationError

from gui_agent_loop_core.converter.conversion_rule import ConversionRule
from gui_agent_loop_core.converter.dict_flatten_converter import DictFlattenConverter
from gui_agent_loop_core.schema.schema import GuiAgentInterpreterChatRequest, GuiAgentInterpreterChatRequestAny

CoreAny = Union[str, BaseModel, List[BaseModel]]


class RequestConverter(DictFlattenConverter):
    def __init__(self, conversion_rules: Dict[str, ConversionRule]):
        self.conversion_rules = conversion_rules

    def to_dict_from_core(
        self, core_any: GuiAgentInterpreterChatRequestAny, core_class: Type[BaseModel] = GuiAgentInterpreterChatRequest
    ) -> List[dict]:
        core_list = super().to_core_list_from_core_any(core_any, core_class)
        dict_list = super()._to_dict_list_from_core_list(core_list, GuiAgentInterpreterChatRequest)
        converted_dict_list = []
        for core, dict_item in zip(core_list, dict_list):
            converted_dict_item = self.convert(dict_item, self.conversion_rules)
            converted_dict_list.append(converted_dict_item)
        return converted_dict_list

    def _to_dict_from_core_custom(self, core: GuiAgentInterpreterChatRequest, dict_item: dict):
        # content
        if core.code:
            dict_item["content"] = {
                "role": "computer",
                "type": "confirmation",
                "format": "execution",
                "content": {
                    "type": "code",
                    "format": core.language,
                    "content": core.code,
                },
            }
        else:
            dict_item["content"] = core.content
        return dict_item

    def preprocess_dict(self, input_dict: Dict[str, Any]) -> Dict[str, str]:
        def flatten_content(content: Any) -> str:
            if isinstance(content, dict):
                if content.get("type") == "code":
                    return ""
                else:
                    return flatten_content(content.get("content", ""))
            else:
                return content

        def preprocess_dict_iter(dict_item: Dict[str, Any], candidate_keys: List[str]) -> Dict[str, str]:
            output_dict = {}
            for key, value in dict_item.items():
                if key in candidate_keys:
                    output_dict[key] = value
                elif key == "content":
                    output_dict[key] = flatten_content(value)
                elif isinstance(value, dict):
                    output_dict[key] = preprocess_dict_iter(value, candidate_keys)
                else:
                    output_dict[key] = value
            return output_dict

        candidate_keys = ["format", "code", "language"]
        return preprocess_dict_iter(input_dict, candidate_keys)

    def to_dict_from_core_custom(self, request: GuiAgentInterpreterChatRequest) -> Dict[str, Any]:
        if request.code:
            return self.preprocess_dict({"content": request.code})
        else:
            return self.preprocess_dict({"content": request.content})


def test_request_converter():
    # Define conversion rules
    conversion_rules = {
        "content": ConversionRule(
            target_key="content",
            mapping_rules={
                "type": DictFlattenConverter.MappingRule(old_key="type", new_key="type"),
                "format": DictFlattenConverter.MappingRule(old_key="format", new_key="format"),
                "content": DictFlattenConverter.MappingRule(old_key="content", new_key="code"),
            },
            content_dict_rules={
                "format": DictFlattenConverter.ContentDictRule(content_key="format", new_key="language"),
            },
            required_keys={"type": "confirmation"},
        )
    }

    converter = RequestConverter(conversion_rules)

    # Example 1: Convert single model instance
    request = GuiAgentInterpreterChatRequest(content="Hello, how can I help you?")
    dict_list = converter.to_dict_from_core(request)
    print("Single model instance:")
    print(dict_list)

    # Example 2: Convert list of model instances
    request_list = [
        GuiAgentInterpreterChatRequest(content="Request 1"),
        GuiAgentInterpreterChatRequest(content="Request 2", code="print('Hello, World!')"),
    ]
    dict_list = converter.to_dict_from_core(request_list)
    print("List of model instances:")
    print(dict_list)

    # Example 3: Convert from dict
    dict_list = [
        {"content": "Request 3"},
        {
            "content": {
                "role": "computer",
                "type": "confirmation",
                "format": "execution",
                "content": {
                    "type": "code",
                    "format": "python",
                    "content": "print('Hello, World!')",
                },
            }
        },
    ]
    request_list = converter.to_core_from_dict(dict_list, GuiAgentInterpreterChatRequest)
    print("Convert from dict:")
    print(request_list)

    # Example 4: Convert string input
    string_input = "Hello, World!"
    dict_list = converter.to_dict_from_core(string_input)
    print("String input:")
    print(dict_list)


if __name__ == "__main__":
    test()
