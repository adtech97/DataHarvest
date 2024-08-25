import json
from dbutils import connectors
import io
import csv
import zipfile
import requests
import psycopg2
import json
from pyspark.sql.types import StructType, StructField, StringType, FloatType, IntegerType
from pyspark.sql import SparkSession

class BusDataReference:

    def __init__(self):
        self.data_endpoint ='https://www.transportforireland.ie/transitData/Data/GTFS_Dublin_Bus.zip'


    def get_routes_table_schema(self):
            bus_routes_schema = StructType([
                StructField("route_short_name", StringType(), True),
                StructField("route_id", StringType(), True),
                StructField("shape_id", StringType(), True),
                StructField("latitude", FloatType(), True),
                StructField("longitude", FloatType(), True),
                StructField("sequence", IntegerType(), True)
            ])

            return bus_routes_schema




    def download_and_extract_files(self):
        response = requests.get(self.data_endpoint)
        with zipfile.ZipFile(io.BytesIO(response.content), 'r') as zip_ref:
            with zip_ref.open('routes.txt') as routes_file, \
                zip_ref.open('trips.txt') as trips_file, \
                zip_ref.open('shapes.txt') as shapes_file:

                routes_data = self.read_routes_data(routes_file)
                trips_data = self.read_trips_data(trips_file)
                shapes_data = self.read_shapes_data(shapes_file)
                combined_data = self.combine_data(routes_data, trips_data, shapes_data)

                # Define column names
                column_names = ['route_short_name', 'route_id', 'shape_id', 'latitude','longitude','sequence']
                
                # Zip column names with combined data
                combined_data_with_columns = [dict(zip(column_names, row)) for row in combined_data]

                return combined_data_with_columns

    def combine_data(self, routes_data, trips_data, shapes_data):
        combined_data = []
        for route_info in routes_data:
            route_id, route_short_name = route_info
            for pair in trips_data:
                if pair[0] == route_id:
                    shape_id = pair[1]  
                    break
            route_shapes = shapes_data[shape_id]
            for i, point in enumerate(route_shapes, start=1):
                combined_data.append([route_short_name, route_id, shape_id, float(point["lat"]), float(point["lon"]), i])
        return combined_data
    def read_routes_data(self, file):
        routes_data = []
        reader = csv.DictReader(io.TextIOWrapper(file))
        for row in reader:
            route_id = row['route_id']
            route_short_name = row['route_short_name']
            routes_data.append((route_id, route_short_name))
        return routes_data

    def read_trips_data(self, file):
        trips_data = []
        reader = csv.DictReader(io.TextIOWrapper(file))
        for row in reader:
            route_id = row['route_id']
            shape_id = row['shape_id']
            trips_data.append((route_id, shape_id))
        return trips_data

    def read_shapes_data(self, file):
        shapes_data = {}
        reader = csv.DictReader(io.TextIOWrapper(file))
        for row in reader:
            shape_id = row['shape_id']
            shape_pt_lat = row['shape_pt_lat']
            shape_pt_lon = row['shape_pt_lon']
            point = {"lat" : float(shape_pt_lat), "lon": float(shape_pt_lon)}
            if shape_id in shapes_data:
                shapes_data[shape_id].append(point)
            else:
                shapes_data[shape_id] = [point]
        return shapes_data
 
def get_routes_create_table_query():
    query = """
        CREATE TABLE IF NOT EXISTS bus_routes (
            route_short_name VARCHAR(50),
            route_id VARCHAR(50),
            shape_id VARCHAR(50),
            latitude FLOAT,
            longitude FLOAT,
            sequence INTEGER
        );
    """
    return query

def remove_data_fromTable():
    query = """
DELETE FROM bus_routes;
    """
    return query


    
def generate_spark_dataframes(self, spark_session) -> dict:
    api_data = self.download_and_extract_files()
    Bus_route_schema = self.get_routes_table_schema()
    # Create DataFrame
    bus_route_data_df = spark_session.createDataFrame(api_data, Bus_route_schema)   
    return [{'table_name': 'bus_routes', 'spark_df': bus_route_data_df}]






   
