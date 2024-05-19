from typing import Any, Dict, List

from gui_agent_loop_core.converter.dict_flattener.mapping_rule import MappingRule


class DictFlattener:
    def __init__(self, mapping_rules: List[MappingRule]):
        self.mapping_rules = mapping_rules

    def flatten(self, data: Dict[str, Any], upper_data: Dict[str, Any] = None) -> Dict[str, str]:
        """
        辞書をフラット化する関数(初回)
        """
        if upper_data is None:
            upper_data = {}

        flattened_dict = {}
        self._flatten(data, upper_data, flattened_dict)
        return flattened_dict

    def _flatten(
        self,
        data: Dict[str, Any],
        upper_data: Dict[str, Any],
        flattened_dict: Dict[str, str],
    ) -> Dict[str, str]:
        """
        辞書をフラット化する関数
        """
        # deep side first
        self._flatten_recursive(data, flattened_dict)
        self._apply_mapping_rules(data, upper_data, flattened_dict)
        return flattened_dict

    def _apply_mapping_rules(
        self,
        data: Dict[str, Any],
        upper_data: Dict[str, Any],
        flattened_dict: Dict[str, str],
    ):
        """
        mapping_rule.applyする関数
        """
        for mapping_rule in self.mapping_rules:
            mapping_rule.apply(data, upper_data, flattened_dict)

    def _flatten_recursive(
        self,
        data: Dict[str, Any],
        flattened_dict: Dict[str, str],
    ):
        """
        辞書を再帰的にフラット化する関数
        """
        for _, value in data.items():
            if isinstance(value, dict):
                self._flatten(value, data, flattened_dict)


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


def test_dict_flattener():
    mapping_rules, data, expected_output = prepare_test_data()
    flattened_dict = DictFlattener(mapping_rules).flatten(data)
    assert flattened_dict == expected_output


if __name__ == "__main__":
    test_dict_flattener()
