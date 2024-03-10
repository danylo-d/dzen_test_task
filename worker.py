import os

import pika
import json
from neo4j import GraphDatabase

neo4j_uri = "bolt://neo4j:7687"
neo4j_user = "neo4j"
neo4j_password = os.environ["NEO4J_AUTH"].split("/")[1]


class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.__uri = uri
        self.__user = user
        self.__password = password
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(
                self.__uri, auth=(self.__user, self.__password)
            )
        except Exception as e:
            print("Failed to create the driver:", e)

    def close(self):
        if self.__driver is not None:
            self.__driver.close()

    def execute_query(self, query, parameters=None):
        with self.__driver.session() as session:
            result = session.run(query, parameters)
            return [record for record in result]


neo4j_conn = Neo4jConnection(neo4j_uri, neo4j_user, neo4j_password)


def process_metric_data(ch, method, properties, body):
    data = json.loads(body)
    print(f"Received data: {data}")

    query = """
    MERGE (user:User {id: $user_id})
    MERGE (comment:Comment {id: $comment_id})
    CREATE (user)-[:PERFORMED]->(action:Action {type: $action})
    CREATE (action)-[:ON]->(comment)
    """

    parameters = {
        "user_id": data["user_id"],
        "comment_id": data["comment_id"],
        "action": data["action"],
    }
    neo4j_conn.execute_query(query, parameters)


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="rabbitmq", port=5672)
    )
    channel = connection.channel()

    channel.queue_declare(queue="metrics_queue")

    channel.basic_consume(
        queue="metrics_queue", on_message_callback=process_metric_data, auto_ack=True
    )

    print(" [*] Waiting for messages. To exit press CTRL+C")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Interrupted")
        connection.close()


if __name__ == "__main__":
    main()
