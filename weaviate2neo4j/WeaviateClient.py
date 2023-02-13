import numpy as np
import weaviate
from weaviate2neo4j.WeaviateObject import WeaviateObject


class WeaviateClient:

    def __init__(self,
                 url: str,
                 username: str,
                 password: str
                 ) -> None:
        self.client = weaviate.Client(url)

    def get_vector_count(self, classname) -> int:
        # {'data': {'Aggregate': {'<classname>': [{'meta': {'count': 36}}]}}}
        return self.client.query.aggregate(classname).with_meta_count().do()['data']['Aggregate'][classname][0]['meta']['count']

    def get_objects(self, classname, properties, batch_size=None, offset=None):
        # ['data']['Get']['<classname>'][<idx>]['_additional'])
        # Return a list of {id: <id>, vector: <vector>} dicts
        query = (self.client.query
                 .get(classname, properties)
                 .with_additional(["id", "vector"])
                 )
        if batch_size:
            query = query.with_limit(batch_size)
        if offset:
            query = query.with_offset(offset)

        result = query.do()
        return list(map(WeaviateObject.from_data_object, result['data']['Get'][classname]))
