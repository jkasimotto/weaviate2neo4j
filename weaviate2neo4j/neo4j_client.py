from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, ClientError


class Neo4jClient:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def add_nodes(self, nodes):
        with self.driver.session() as session:
            try:
                result = session.execute_write(
                    self._add_nodes, nodes)
                return result
            except ServiceUnavailable as e:
                print("Error: ", e)

    @staticmethod
    def _add_nodes(tx, nodes):
        classname = nodes[0].classname
        property_keys = nodes[0].properties.keys()
        property_string = ", ".join(
            [f"{key}: node.{key}" for key in property_keys])
        query = (
            f"UNWIND $nodes AS node "
            f"MERGE (n:{classname} {{ id: node.id, {property_string} }}) "
        )
        result = tx.run(query, nodes=[node.neo4j_dict for node in nodes])
        return result.consume().counters.nodes_created


    def add_edges(self, edges, row_classname, col_classname):
        with self.driver.session() as session:
            try:
                result = session.execute_write(
                    self._add_edges, edges, row_classname, col_classname)
                return result
            except ServiceUnavailable as e:
                print("Error: ", e)

    @staticmethod
    def _add_edges(tx, edges, row_classname, col_classname):
        query = (
            f"UNWIND $edges AS edge "
            f"MATCH (n1:{row_classname} {{ id: edge.from_id }}), (n2:{col_classname} {{ id: edge.to_id }}) "
            f"MERGE (n1)-[:SIMILAR_TO {{ similarity: edge.weight }}]->(n2) "
            f"MERGE (n2)-[:SIMILAR_TO {{ similarity: edge.weight }}]->(n1) "
        )
        result = tx.run(query, edges=edges)
        return result.consume().counters.relationships_created
