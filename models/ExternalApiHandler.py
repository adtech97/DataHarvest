from typing import List

class ExternalApiHandler:

    def __init__(self) -> None:
        pass

    def get_table_create_queries(self) -> List[str]:
        pass

    def create_tables_if_not_exist(self, db_connction) -> None:
        queries = self.get_table_create_queries()
        for query in queries:
            db_connction.pg_connect_exec(query=query)
        db_connction.commit_transaction()

    def fetch(self) -> dict | List | None:
        pass

    def generate_spark_dataframes(self, spark_session) -> dict:
        pass