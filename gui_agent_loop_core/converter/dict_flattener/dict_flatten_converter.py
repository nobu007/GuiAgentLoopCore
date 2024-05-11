from typing import Any, Dict

from gui_agent_loop_core.converter.base_converter import BaseConverter

from .content_dict_rule import ContentDictRule
from .conversion_rule import ConversionRule
from .dict_flattener import DictFlattener
from .mapping_rule import MappingRule


class DictFlattenConverter(BaseConverter):
    def convert(self, raw_dict: Dict[str, Any], conversion_rules: Dict[str, ConversionRule]) -> Dict[str, str]:
        """
        辞書をフラット化する関数
        """
        flattened_dict = {}
        DictFlattener().flatten_recursive(raw_dict, conversion_rules, flattened_dict)
        return flattened_dict


def prepare_test_data():
    conversion_rules = {
        "content": ConversionRule(
            target_key="content",
            mapping_rules={
                "type": MappingRule(old_key="type", new_key="type"),
                "format": MappingRule(old_key="format", new_key="format"),
                "content": MappingRule(old_key="content", new_key="code"),
            },
            content_dict_rules={
                "format": ContentDictRule(content_key="format", new_key="language"),
            },
            required_keys={"type": "confirmation"},
        )
    }

    raw_dict = {
        "content": {
            "role": "computer",
            "type": "confirmation",
            "format": "execution",
            "content": {
                "type": "code",
                "format": "python",
                "content": "print('Hello, World!')",
            },
        },
    }

    expected_output = {
        "type": "confirmation",
        "format": "execution",
        "code": "print('Hello, World!')",
        "language": "python",
    }

    return conversion_rules, raw_dict, expected_output


def test_dict_flatten_converter():
    conversion_rules, raw_dict, expected_output = prepare_test_data()
    flattened_dict = DictFlattenConverter().convert(raw_dict, conversion_rules)
    assert flattened_dict == expected_output


if __name__ == "__main__":
    test_dict_flatten_converter()
