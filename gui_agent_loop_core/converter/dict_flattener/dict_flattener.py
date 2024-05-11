from typing import Any, Dict

from gui_agent_loop_core.converter.base_converter import BaseConverter

from .content_dict_rule import ContentDictRule
from .conversion_rule import ConversionRule
from .conversion_rule_checker import ConversionRuleChecker
from .mapping_rule import MappingRule


class DictFlattener:
    def flatten_recursive(
        self,
        data: Dict[str, Any],
        conversion_rules: Dict[str, ConversionRule],
        flattened_dict: Dict[str, str],
        prefix: str = "",
    ):
        """
        辞書を再帰的にフラット化する関数
        """
        checked_dict = ConversionRuleChecker().check_conversion_rules(data, conversion_rules, prefix)
        flattened_dict.update(checked_dict)
        for key, value in data.items():
            if isinstance(value, dict) and key not in [rule.target_key for rule in conversion_rules.values()]:
                self.flatten_recursive(value, conversion_rules, flattened_dict, f"{prefix}{key}__")
            elif key not in [rule.target_key for rule in conversion_rules.values()]:
                flattened_dict[f"{prefix}{key}"] = str(value)


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

    data = {
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

    return conversion_rules, data, expected_output


def test_dict_flattener():
    conversion_rules, data, expected_output = prepare_test_data()
    flattened_dict = {}
    DictFlattener().flatten_recursive(data, conversion_rules, flattened_dict)
    assert flattened_dict == expected_output


if __name__ == "__main__":
    test_dict_flattener()
