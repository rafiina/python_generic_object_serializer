from typing import Any, Protocol, runtime_checkable
import json
import yaml


@runtime_checkable
class IsDictionaryConvertable(Protocol):
    def to_dict(self) -> dict[str, Any]: ...


class DictionaryConvertibleObjectJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, IsDictionaryConvertable):
            return obj.to_dict()
        return super(DictionaryConvertibleObjectJsonEncoder, self).default(obj)


class DictionaryConvertibleSerializer:
    def __init__(self) -> None:
        # mypy doesn't like using protocols this way, but it is legitimate
        # as long as add_multi_representer() doesn't try to instantiate
        # a IsDictionaryConvertable
        # see https://github.com/python/mypy/issues/4717
        yaml.add_multi_representer(IsDictionaryConvertable, self.dictionary_convertible_object_representer)  # type: ignore

    @staticmethod
    def json_dumps(data: Any) -> str:
        return json.dumps(data, cls=DictionaryConvertibleObjectJsonEncoder)

    @staticmethod
    def yaml_dump(data: Any) -> str:
        return yaml.dump(data)

    @staticmethod
    def dictionary_convertible_object_representer(
        dumper: yaml.Dumper, data: IsDictionaryConvertable
    ):
        class_name = type(data).__name__
        serialized_data = data.to_dict()
        return dumper.represent_mapping(f"!{class_name}", serialized_data)


if __name__ == "__main__":

    class Test(IsDictionaryConvertable):
        def to_dict(self) -> dict[str, Any]:
            return {"hello": [1, 2, 3]}

    class Test2(IsDictionaryConvertable):
        def __init__(self) -> None:
            self.test = Test()

        def to_dict(self) -> dict[str, Any]:
            return {"nested": self.test.to_dict()}

    serializer = DictionaryConvertibleSerializer()
    test = Test2()
    print(serializer.json_dumps(test))
    print(serializer.yaml_dump(test))
