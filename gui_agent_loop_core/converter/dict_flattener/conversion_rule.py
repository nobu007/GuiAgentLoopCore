from typing import Any, Dict

from pydantic import BaseModel

from .content_dict_rule import ContentDictRule
from .mapping_rule import MappingRule


class ConversionRule(BaseModel):
    target_key: str
    mapping_rules: Dict[str, MappingRule] = {}
    content_dict_rules: Dict[str, ContentDictRule] = {}
    required_keys: Dict[str, Any] = {}

    def apply(self, data: Dict[str, Any], flattened_dict: Dict[str, str], prefix: str = ""):
        """
        変換則を適用する関数
        """
        if self.target_key in data and self.check_constraints(data):
            self._apply_mapping_rules(data, flattened_dict)
            self._apply_content_dict_rules(data, flattened_dict)

    def _apply_mapping_rules(self, data: Dict[str, Any], flattened_dict: Dict[str, str]):
        """
        mapping_rulesに基づいて変換を適用する関数
        """
        for mapping_rule in self.mapping_rules.values():
            if mapping_rule.old_key in data[self.target_key]:
                if (
                    isinstance(data[self.target_key][mapping_rule.old_key], dict)
                    and "content" in data[self.target_key][mapping_rule.old_key]
                ):
                    flattened_dict[mapping_rule.new_key] = str(data[self.target_key][mapping_rule.old_key]["content"])
                else:
                    flattened_dict[mapping_rule.new_key] = str(data[self.target_key][mapping_rule.old_key])

    def _apply_content_dict_rules(self, data: Dict[str, Any], flattened_dict: Dict[str, str]):
        """
        content_dict_rulesに基づいて変換を適用する関数
        """
        for content_dict_rule in self.content_dict_rules.values():
            if content_dict_rule.content_key in data[self.target_key]["content"]:
                flattened_dict[content_dict_rule.new_key] = str(
                    data[self.target_key]["content"][content_dict_rule.content_key]
                )

    def check_constraints(self, data: Dict[str, Any]) -> bool:
        """
        制約条件をチェックする関数
        """
        for required_key, required_value in self.required_keys.items():
            if required_key not in data[self.target_key] or (
                required_value is not None and data[self.target_key][required_key] != required_value
            ):
                return False
        return True


def test_conversion_rule():
    conversion_rule = ConversionRule(
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

    flattened_dict = {}
    conversion_rule.apply(data, flattened_dict)

    assert flattened_dict == {
        "type": "confirmation",
        "format": "execution",
        "code": "print('Hello, World!')",
        "language": "python",
    }


if __name__ == "__main__":
    test_conversion_rule()
