import unittest
from typing import List
from datetime import datetime
from pyspark.sql.types import StructType
from models.BusApiHandler import BusApiHandler

class BusApiHandlerTests(unittest.TestCase):

    def setUp(self) -> None:
        self.bus_handler = BusApiHandler()
        return

    def test_get_trips_table_schema(self):
        schema = self.bus_handler.get_trips_table_schema()
        self.assertIsInstance(schema, StructType)

    def test_get_positions_table_schema(self):
        schema = self.bus_handler.get_positions_table_schema()
        self.assertIsInstance(schema, StructType)

    def test_get_table_create_queries(self):
        query = self.bus_handler.get_table_create_queries()
        self.assertIsInstance(query, List)

    def test_fetch(self):
        data = self.bus_handler.fetch()
        self.assertIsInstance(data, dict)
        
        # Ensure the keys 'positions' and 'trips' are lists
        self.assertIn('positions', data)
        self.assertIn('trips', data)
        self.assertIsInstance(data['positions'], list)
        self.assertIsInstance(data['trips'], list)
        
        expected_position_types = {
        'longitude': float,
        'latitude': float,
        'timestamp': datetime,
        'trip_id': str  
        }
        expected_trip_types = {
        'trip_id': str,  
        'start_datetime': datetime,
        'vehicle': str 
        }
        if data['positions']:  # ensure at least one position
            for key, value_type in expected_position_types.items():
                self.assertIn(key, data['positions'][0])
                self.assertIsInstance(data['positions'][0][key], value_type)

   
        if data['trips']:  # ensure at least one trip
            for key, value_type in expected_trip_types.items():
                self.assertIn(key, data['trips'][0])
                self.assertIsInstance(data['trips'][0][key], value_type)
        