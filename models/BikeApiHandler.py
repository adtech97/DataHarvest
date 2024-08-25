import requests
from typing import List
from datetime import datetime
from pyspark.sql.types import StructType
from models.ExternalApiHandler import ExternalApiHandler
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType, TimestampType

class BikeApiHandler(ExternalApiHandler):

    def __init__(self) -> None:
        self.host = 'https://data.smartdublin.ie/dublinbikes-api/last_snapshot/'
        self.headers = {'accept':'application/json'}

    def get_table_create_queries(self) -> List[str]:
        stations_create_table_query = """
        CREATE TABLE IF NOT EXISTS bike_stations (
            id INT PRIMARY KEY,
            name VARCHAR(255),
            address VARCHAR(255),
            bike_stands INT,
            latitude REAL,
            longitude REAL
        )
        """
        availability_create_table_query = """
        CREATE TABLE IF NOT EXISTS bike_availability (
            harvest_time TIMESTAMP,
            last_update_time TIMESTAMP,
            station_id INT,
            available_bike_stands INT,
            available_bikes INT,
            status VARCHAR(255)
        )
        """
        return [stations_create_table_query, availability_create_table_query]

    def get_bike_station_table_schema(self) -> StructType:
        bike_station_schema = StructType([
            StructField("id", IntegerType(), True),
            StructField("name", StringType(), True),
            StructField("address", StringType(), True),
            StructField("latitude", FloatType(), True),
            StructField("longitude", FloatType(), True),
            StructField("bike_stands", IntegerType(), True)
        ])
        return bike_station_schema

    def get_bike_availability_table_schema(self) -> StructType:
        bike_availability_schema = StructType([
            StructField("harvest_time", TimestampType(), True),
            StructField("last_update_time", TimestampType(), True),
            StructField("station_id", IntegerType(), True),
            StructField("available_bike_stands", IntegerType(), True),
            StructField("available_bikes", IntegerType(), True),
            StructField("status", StringType(), True)
        ])
        return bike_availability_schema

    def fetch(self) -> List:
        api_response = requests.get(self.host, headers=self.headers)
        bike_raw_data = api_response.json()
        bike_cleaned_data = []
        for data_entry in bike_raw_data:
            harvest_time = datetime.strptime(data_entry['harvest_time'], "%Y-%m-%dT%H:%M:%S")
            last_update_time = datetime.strptime(data_entry['last_update'], "%Y-%m-%dT%H:%M:%S")
            bike_cleaned_data.append({
                'harvest_time': harvest_time,
                'last_update_time': last_update_time,
                'station_id': data_entry['station_id'],
                'available_bike_stands': data_entry['available_bike_stands'],
                'available_bikes': data_entry['available_bikes'],
                'status': data_entry['status']
            })
        return bike_cleaned_data
    
    def generate_spark_dataframes(self, spark_session) -> dict:
        bike_availability_schema = self.get_bike_availability_table_schema()
        bike_availability_data = self.fetch()
        bike_availability_df = spark_session.createDataFrame(bike_availability_data, bike_availability_schema)
        return [{'table_name': 'bike_availability', 'spark_df': bike_availability_df}]
