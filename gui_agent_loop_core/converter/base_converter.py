from typing import List, Optional, Type, Union

from pydantic import BaseModel

CoreAny = Union[str, BaseModel, List[BaseModel]]


class BaseConverter(BaseModel):
    def to_dict_from_core(self, core_any: CoreAny, core_class: Type[BaseModel] = None) -> List[dict]:
        core_list = self.to_core_list_from_core_any(core_any, core_class)
        dict_list = self._to_dict_list_from_core_list(core_list, core_class)
        return dict_list

    def to_core_list_from_core_any(self, core_any: CoreAny, core_class: Type[BaseModel]):
        if isinstance(core_any, str):
            # Handle string input
            return [core_class(content=core_any)]
        elif isinstance(core_any, BaseModel):
            # Handle single model instance input
            return [core_any]
        elif isinstance(core_any, list):
            # Handle list input
            return core_any
        else:
            raise ValueError("Invalid input type. Expected CoreAny (str, BaseModel, or list of BaseModel).")

    def _to_dict_list_from_core_list(self, core_list: List[BaseModel], core_class: Type[BaseModel]) -> dict:
        return [self._to_dict_from_core(core) for core in core_list if isinstance(core, core_class)]

    def _to_dict_from_core(self, core: BaseModel) -> dict:
        return core.model_dump()

    def _to_core_list_from_dict_list(self, core_list: List[BaseModel], core_class: Type[BaseModel]) -> dict:
        return [self._core_to_dict(core) for core in core_list if isinstance(core, core_class)]

    def to_core_from_dict(self, dict_list: List[dict], core_class: Type[BaseModel]) -> List[BaseModel]:
        core_list = [core_class.model_validate(dict_item) for dict_item in dict_list]
        return core_list


def test():
    converter = BaseConverter()

    class UserModel(BaseModel):
        name: Optional[str] = ""
        age: Optional[int] = 0
        content: str

    # Example 1: Convert single model instance
    user = UserModel(name="John", age=30, content="john@example.com")
    dict_list = converter.to_dict_from_core(user, UserModel)
    print("Single model instance:")
    print(dict_list)

    # Example 2: Convert list of model instances
    user_list = [
        UserModel(name="Alice", age=25, content="alice@example.com"),
        UserModel(name="Bob", age=35, content="bob@example.com"),
    ]
    dict_list = converter.to_dict_from_core(user_list, UserModel)
    print("List of model instances:")
    print(dict_list)

    # Example 3: Convert from dict
    dict_list = [
        {"name": "Carol", "age": 28, "content": "carol@example.com"},
        {"name": "Dave", "age": 32, "content": "dave@example.com"},
    ]
    user_list = converter.to_core_from_dict(dict_list, UserModel)
    print("Convert from dict:")
    print(user_list)

    # Example 4: Convert string input
    string_input = "Hello, World!"
    dict_list = converter.to_dict_from_core(string_input, UserModel)
    print("String input:")
    print(dict_list)


if __name__ == "__main__":
    test()
