from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class WeaviateObject:
    id: str
    vector: Any
    properties: Dict[str, Any]

    @classmethod
    def from_data_object(cls, data_object: Dict[str, Any]):
        return cls(
            id=data_object['_additional']['id'],
            vector=data_object['_additional']['vector'],
            properties={
                key: data_object[key]
                for key in data_object.keys() if key != '_additional'
            },
        )
