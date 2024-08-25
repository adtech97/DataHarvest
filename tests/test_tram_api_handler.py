import unittest
from typing import List
from pyspark.sql.types import StructType
from models.TramApiHandler import TramApiHandler

class TramApiHandlerTests(unittest.TestCase):

    def setUp(self) -> None:
        self.tram_handler = TramApiHandler()
        return

    def test_get_tram_stations_table_schema(self):
        schema = self.tram_handler.get_tram_stops_table_schema()
        self.assertIsInstance(schema, StructType)

    def test_get_tram_arrivals_table_schema(self):
        schema = self.tram_handler.get_tram_arrivals_table_schema()
        self.assertIsInstance(schema, StructType)

    def test_get_table_create_queries(self):
        query = self.tram_handler.get_table_create_queries()
        self.assertIsInstance(query, List)

    def test_fetch(self):
        data = self.tram_handler.fetch()
        self.assertIsInstance(data, List)