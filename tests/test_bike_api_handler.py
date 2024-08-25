import unittest
from typing import List
from datetime import datetime
from pyspark.sql.types import StructType
from models.BikeApiHandler import BikeApiHandler

class BikeApiHandlerTests(unittest.TestCase):

    def setUp(self) -> None:
        self.bike_handler = BikeApiHandler()
        return

    def test_get_bike_station_table_schema(self):
        schema = self.bike_handler.get_bike_station_table_schema()
        self.assertIsInstance(schema, StructType)

    def test_get_bike_availability_table_schema(self):
        schema = self.bike_handler.get_bike_availability_table_schema()
        self.assertIsInstance(schema, StructType)    

    def test_get_table_create_query(self):
        query = self.bike_handler.get_table_create_queries()
        self.assertIsInstance(query, List)

    def test_fetch(self):
        data = self.bike_handler.fetch()
        self.assertIsInstance(data, List)
        
        expected_types = {
            'harvest_time': datetime,
            'last_update_time': datetime,
            'station_id': int,
            'available_bike_stands': int,
            'available_bikes':int,
            'status':str
        }
        for inner_dict in data:
            self.assertIsInstance(inner_dict, dict)
            for key, value in inner_dict.items():
                self.assertIsInstance(value, expected_types[key])