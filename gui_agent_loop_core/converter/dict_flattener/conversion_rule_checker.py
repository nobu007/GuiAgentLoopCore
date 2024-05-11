from typing import Any, Dict

from .content_dict_rule import ContentDictRule
from .conversion_rule import ConversionRule
from .mapping_rule import MappingRule


class ConversionRuleChecker:
    def check_conversion_rules(
        self, data: Dict[str, Any], conversion_rules: Dict[str, ConversionRule], prefix: str = ""
    ) -> Dict[str, str]:
        """
        変換則をチェックし、チェックに合格した項目を別の辞書に格納する関数
        """
        checked_dict = {}
        for rule in conversion_rules.values():
            if rule.target_key in data and rule.check_constraints(data):
                rule.apply(data, checked_dict, prefix)
        return checked_dict


def test_conversion_rule_checker():
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

    checked_dict = ConversionRuleChecker().check_conversion_rules(data, conversion_rules)

    assert checked_dict == {
        "type": "confirmation",
        "format": "execution",
        "code": "print('Hello, World!')",
        "language": "python",
    }


if __name__ == "__main__":
    test_conversion_rule_checker()
