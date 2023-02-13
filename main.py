from weaviate2neo4j.config import read_config
from weaviate2neo4j.weaviate2neo4j import Weaviate2Neo4j
from dotenv import load_dotenv


# Use neo4j_client object to add nodes and edges to the graph
if __name__ == "__main__":

    # Load environment variables from .env file
    load_dotenv("credentials-1af03722.env")
    load_dotenv("")

    # Get configuration settings
    config = read_config("config.yaml")

    weaviate_2_neo4j = Weaviate2Neo4j(config)
    weaviate_2_neo4j.convert_batches(
        edge_filter=None
    )
    weaviate_2_neo4j.cleanup()


# neo4j_client.add_nodes([{"id": 1}, {"id": 2}], "Memory")
