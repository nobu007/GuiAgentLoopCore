from typing import Any, Dict, List

from gui_agent_loop_core.converter.base_converter import BaseConverter

# from .conversion_rule import ConversionRule
from .dict_flattener import DictFlattener, MappingRule


class DictFlattenConverter(BaseConverter):
    mapping_rules: List[MappingRule] = []

    def convert(self, raw_dict: Dict[str, Any]) -> Dict[str, str]:
        """
        辞書をフラット化する関数
        """
        flattened_dict = DictFlattener(self.mapping_rules).flatten(raw_dict)
        if "content" not in flattened_dict:
            flattened_dict["content"] = ""
        return flattened_dict


def prepare_test_data():
    mapping_rules = MappingRule.get_default_mapping_rules()

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
        "role": "computer",
        "type": "confirmation",
        "format": "execution",
        "code": "print('Hello, World!')",
        "language": "python",
        "content": "",
    }

    return mapping_rules, raw_dict, expected_output


def prepare_test_data_simple():
    mapping_rules = MappingRule.get_default_mapping_rules()

    raw_dict = {
        "content": {
            "role": "computer",
            "type": "confirmation",
            "format": "execution",
            "content": "already flat str",
        },
    }

    expected_output = {
        "role": "computer",
        "type": "confirmation",
        "format": "execution",
        "content": "already flat str",
    }

    return mapping_rules, raw_dict, expected_output


def test_dict_flatten_converter():
    mapping_rules, raw_dict, expected_output = prepare_test_data()
    converter = DictFlattenConverter(mapping_rules=mapping_rules)

    flattened_dict = converter.convert(raw_dict)
    assert flattened_dict == expected_output

    mapping_rules, raw_dict, expected_output = prepare_test_data_simple()
    flattened_dict = converter.convert(raw_dict)
    assert flattened_dict == expected_output


if __name__ == "__main__":
    test_dict_flatten_converter()
