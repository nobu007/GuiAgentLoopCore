from pydantic import BaseModel


class MappingRule(BaseModel):
    old_key: str
    new_key: str


def test_mapping_rule():
    mapping_rule = MappingRule(old_key="old", new_key="new")
    assert mapping_rule.old_key == "old"
    assert mapping_rule.new_key == "new"


if __name__ == "__main__":
    test_mapping_rule()
