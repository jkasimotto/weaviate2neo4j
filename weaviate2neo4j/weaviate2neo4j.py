import time
from typing import Callable, List, Optional, Union

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from weaviate2neo4j.neo4j_client import Neo4jClient
from weaviate2neo4j.Neo4jNode import Neo4jNode
from weaviate2neo4j.WeaviateClient import WeaviateClient


class Weaviate2Neo4j:
    def __init__(self, config):
        self.config = config
        self.weaviate = WeaviateClient(
            config['weaviate']['url'],
            config['weaviate']['username'],
            config['weaviate']['password']
        )
        self.neo4j = Neo4jClient(
            config['neo4j']['uri'],
            config['neo4j']['username'],
            config['neo4j']['password']
        )

    def cleanup(self):
        self.neo4j.close()

    def convert_batches(self, edge_filter=None, row_batch_size=None, col_batch_size=None):
        row_batch_size = row_batch_size or self.config['weaviate']['row_batch_size']
        col_batch_size = col_batch_size or self.config['weaviate']['col_batch_size']
        try:
            # Get the number of rows and columns
            row_count = self.weaviate.get_vector_count(
                self.config['weaviate']['row_classname'])
            col_count = self.weaviate.get_vector_count(
                self.config['weaviate']['col_classname'])
            print("Row count: {}".format(row_count))
            print("Col count: {}".format(col_count))

            # Add edges to Neo4j
            for row_offset in range(0, row_count, row_batch_size):
                row_objects = self.weaviate.get_objects(
                    self.config['weaviate']['row_classname'],
                    self.config['weaviate']['row_properties'],
                    row_batch_size,
                    row_offset)

                for col_offset in range(0, col_count, col_batch_size):
                    col_objects = self.weaviate.get_objects(
                        self.config['weaviate']['col_classname'],
                        self.config['weaviate']['col_properties'],
                        col_batch_size,
                        col_offset)

                    edges = self._compute_edges(
                        row_objects,
                        col_objects,
                        edge_filter)

                    num_nodes_added = self.neo4j.add_nodes(
                        Neo4jNode.from_weaviate_objects(
                            row_objects,
                            self.config['neo4j']['row_classname']))
                    print("Added {} nodes".format(num_nodes_added))

                    num_nodes_added = self.neo4j.add_nodes(
                        Neo4jNode.from_weaviate_objects(
                            col_objects,
                            self.config['neo4j']['col_classname']))
                    print("Added {} nodes".format(num_nodes_added))

                    num_edges_added = self.neo4j.add_edges(
                        edges,
                        self.config['neo4j']['row_classname'],
                        self.config['neo4j']['col_classname'])
                    print("Added {} edges".format(num_edges_added))
        except Exception as e:
            self.cleanup()
            print(e)
            raise e

    @staticmethod
    def _compute_edges(
        row_dicts,
        col_dicts,
        edge_filter: Optional[Callable[[np.ndarray], np.ndarray]]
    ):
        row_vectors = np.array([row.vector for row in row_dicts])
        col_vectors = np.array([col.vector for col in col_dicts])
        edge_matrix = compute_edge_matrix(
            row_vectors, col_vectors, edge_filter)
        edges = []
        for row_index, row_dict in enumerate(row_dicts):
            for col_index, col_dict in enumerate(col_dicts):
                edge_score = edge_matrix[row_index][col_index]
                if edge_score:
                    edges.append({
                        'from_id': row_dict.id,
                        'to_id': col_dict.id,
                        'weight': edge_score,
                    })
        return edges


def compute_edge_matrix(
    row_vectors: np.ndarray,
    col_vectors: np.ndarray,
    edge_filter: Optional[Callable[[np.ndarray], np.ndarray]]
) -> Union[np.ndarray, List[List[Optional[float]]]]:
    similarities = cosine_similarity(row_vectors, col_vectors)
    similarities = np.clip(similarities, 0, None)
    if edge_filter:
        edge_matrix = np.where(
            np.vectorize(edge_filter)(similarities),
            similarities,
            None)
        return edge_matrix.tolist()
    else:
        return similarities.tolist()
