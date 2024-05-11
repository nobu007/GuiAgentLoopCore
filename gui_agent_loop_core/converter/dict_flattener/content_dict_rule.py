from pydantic import BaseModel


class ContentDictRule(BaseModel):
    content_key: str
    new_key: str


def prepare_content_dict_rule():
    return [
        ({"content_key": "format", "new_key": "language"}, "format", "language"),
        ({"content_key": "old_key", "new_key": "new_key"}, "old_key", "new_key"),
    ]


def test_content_dict_rule():
    test_data = prepare_content_dict_rule()
    for input_data, expected_content_key, expected_new_key in test_data:
        content_dict_rule = ContentDictRule(**input_data)
        assert content_dict_rule.content_key == expected_content_key
        assert content_dict_rule.new_key == expected_new_key


if __name__ == "__main__":
    test_content_dict_rule()
