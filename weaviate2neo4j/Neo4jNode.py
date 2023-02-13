from dataclasses import dataclass
from typing import List
from weaviate2neo4j.WeaviateObject import WeaviateObject


@dataclass
class Neo4jNode:
    classname: str
    id: str
    properties: dict

    @classmethod
    def from_weaviate_object(cls, obj: WeaviateObject, classname: str):
        return cls(
            classname=classname,
            id=obj.id,
            properties=obj.properties
        )

    @classmethod
    def from_weaviate_objects(cls, objects: List[WeaviateObject], classname: str):
        return [cls.from_weaviate_object(obj, classname) for obj in objects]
    
    @property
    def cypher(self) -> str:
        return self.to_cypher()
    
    @property
    def neo4j_dict(self) -> dict:
        return {
            "id": self.id,
            **self.properties
        }

    def to_cypher(self) -> str:
        properties_cypher = ", ".join([
            f"{key}: {self._cypher_value(value)}"
            for key, value in self.properties.items()
        ])

        return f"(:{self.classname} {{id: '{self.id}', {properties_cypher}}})"

    def _cypher_value(self, value: any) -> str:
        if isinstance(value, str):
            return f"'{value}'"
        elif isinstance(value, bool):
            return str(value).lower()
        else:
            return str(value)
    
