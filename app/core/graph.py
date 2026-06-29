from neo4j import GraphDatabase
from config import NEO4J_CONFIG

neo4j_driver = GraphDatabase.driver(
    NEO4J_CONFIG["uri"],
    auth=(
        NEO4J_CONFIG["user"],
        NEO4J_CONFIG["password"]
    )
)