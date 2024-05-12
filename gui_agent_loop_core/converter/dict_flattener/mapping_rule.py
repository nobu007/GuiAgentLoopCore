from typing import Any, Dict, List, Tuple

from pydantic import BaseModel


class MappingRule(BaseModel):
    old_key: str
    new_key: str
    required_keys: List[Tuple[str, str]] = []
    required_keys_upper: List[Tuple[str, str]] = []

    def apply(self, data: Dict[str, Any], upper_data: Dict[str, Any], flattened_dict: Dict[str, str]):
        """
        マッピングルール＋単純なフラット化を適用する関数
        """
        self._apply_mapping_rule(data, upper_data, flattened_dict)
        self._apply_simple(data, flattened_dict)

    def _apply_mapping_rule(self, data: Dict[str, Any], upper_data: Dict[str, Any], flattened_dict: Dict[str, str]):
        """
        マッピングルールを適用する関数
        """
        if self.old_key in data and self._check_required_keys(data) and self._check_required_keys_upper(upper_data):
            # replace flattened_dict and clear data
            if isinstance(data[self.old_key], str):
                flattened_dict[self.new_key] = data[self.old_key]
                data[self.old_key] = ""

    def _apply_simple(self, data: Dict[str, Any], flattened_dict: Dict[str, str]):
        """
        必要なキーと値のペアがデータ内に存在するかチェックする関数
        """
        for key, value in data.items():
            if isinstance(value, str):
                flattened_dict[key] = value

    def _check_required_keys(self, data: Dict[str, Any]) -> bool:
        """
        必要なキーと値のペアがデータ内に存在するかチェックする関数
        """
        return all(self._check_key_value_pair(data, key, value) for key, value in self.required_keys)

    def _check_required_keys_upper(self, upper_data: Dict[str, Any]) -> bool:
        """
        必要なキーと値のペアが上位のデータ内に存在するかチェックする関数
        """
        return all(self._check_key_value_pair(upper_data, key, value) for key, value in self.required_keys_upper)

    @staticmethod
    def _check_key_value_pair(data: Dict[str, Any], key: str, value: str) -> bool:
        """
        キーと値のペアがデータ内に存在するかチェックする関数
        """
        return key in data and (value == "" or str(data[key]) == value)

    @staticmethod
    def get_default_mapping_rules():
        mapping_rules = [
            MappingRule(
                old_key="content",
                new_key="code",
                required_keys=[("format", "")],
                required_keys_upper=[("type", "confirmation")],
            ),
            MappingRule(
                old_key="format",
                new_key="language",
                required_keys_upper=[("type", "confirmation")],
            ),
        ]
        return mapping_rules


def prepare_test_data():
    mapping_rules = MappingRule.get_default_mapping_rules()
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
        "role": "computer",
        "type": "confirmation",
        "content": "",
        "language": "python",
        "format": "execution",
        "code": "print('Hello, World!')",
    }

    return mapping_rules, data, expected_output


def test_mapping_rule_apply():
    mapping_rules, data, expected_output = prepare_test_data()
    flattened_dict = {}

    # deep side first.
    for rule in mapping_rules:
        rule.apply(data["content"]["content"], data["content"], flattened_dict)
    for rule in mapping_rules:
        rule.apply(data["content"], {}, flattened_dict)
    assert flattened_dict == expected_output


if __name__ == "__main__":
    test_mapping_rule_apply()
