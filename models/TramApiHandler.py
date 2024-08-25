import json
import requests
from typing import List
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from pyspark.sql.types import StructType
from models.ExternalApiHandler import ExternalApiHandler
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType, TimestampType

from dbutils import connectors

class TramApiHandler(ExternalApiHandler):

    def __init__(self) -> None:
        self.host = "http://luasforecasts.rpa.ie/xml/get.ashx"

    def get_tram_stops_table_schema(self) -> StructType:
        tram_stops_schema = StructType([
            StructField("stop_id", StringType(), True),
            StructField("stop_name", StringType(), True),
            StructField("latitude", FloatType(), True),
            StructField("longitude", FloatType(), True)
        ])
        return tram_stops_schema

    def get_tram_arrivals_table_schema(self) -> StructType:
        tram_arrivals_schema = StructType([
            StructField("update_time", TimestampType(), True),
            StructField("batch_id", IntegerType(), True),
            StructField("arrival_time", TimestampType(), True),
            StructField("stop_id", StringType(), True),
            StructField("status", StringType(), True),
            StructField("direction", StringType(), True),
            StructField("destination", StringType(), True)
        ])
        return tram_arrivals_schema

    def get_table_create_queries(self) -> List[str]:
        tram_stops_table_query = """
            CREATE TABLE IF NOT EXISTS tram_stops (
                stop_id VARCHAR(255) PRIMARY KEY,
                stop_name VARCHAR(255),
                latitude REAL,
                longitude REAL
            )
        """
        tram_arrivals_table_query = """
            CREATE TABLE IF NOT EXISTS tram_arrivals (
                update_time TIMESTAMP,
                batch_id INTEGER,
                arrival_time TIMESTAMP,
                stop_id VARCHAR(255),
                direction VARCHAR(255),
                destination VARCHAR(255),
                status VARCHAR(255)
            )
        """
        return [tram_stops_table_query, tram_arrivals_table_query]

    def fetch(self) -> List:

        # Read the tram stops from the JSON file
        with open('data/TramStops.json', 'r') as f:
            tram_stops = json.load(f)
        stop_abv_dict = {stop["name"]: stop["abrev"] for stop in tram_stops}
        direction_dict = {"Inbound": "I", "Outbound": "O"}

        # Fetch the next batch id from the tram_batch_id_seq in database
        db_connection = connectors.db_connectors()
        query = "SELECT nextval('tram_batch_id_seq')"
        db_connection.pg_connect_exec(query)
        batch_id = db_connection.cursor.fetchone()[0]

        # Create an empty list to store the tram arrival estimations
        tram_update_data = []

        # Iterate over each tram stop and fetch tram arrival estimations
        for tram_stop in tram_stops:
            update_time = datetime.now()    
            resp = requests.get(
                self.host,
                params={"action": "forecast", "encrypt": "false", "stop": tram_stop["abrev"]}
            )

            # Parse the XML content
            xml_content = resp.content
            root = ET.fromstring(xml_content)
            update_time = datetime.strptime(root.attrib["created"], "%Y-%m-%dT%H:%M:%S")
            stop_id = root.attrib["stopAbv"]
            stop_message = root.find("message").text
            stop_status_normal = True if "normally" in stop_message else False

            # Iterate over each 'direction' element in the XML
            for direction in root.findall("direction"):
                direction_abv = direction.attrib.get("name", None)
                direction_abv = direction_dict[direction_abv] if direction else None

                # Iterate over each 'tram' element in the 'direction' element
                for tram in direction.findall("tram"):

                    # Calculate the arrival time for the tram
                    due_mins = tram.attrib.get("dueMins", None)
                    arrival_time = None
                    if due_mins:
                        if due_mins == "DUE":
                            arrival_time = update_time
                        else:
                            arrival_time = update_time + timedelta(minutes=int(due_mins))

                    # Fetch the destination of the tram and filter out stations with no service
                    destination = tram.attrib.get("destination", None)
                    try:
                        destination_abv = stop_abv_dict[destination]
                    except KeyError:
                        if destination in ["No Northbound Service", "No Southbound Service"]:
                            continue
                        else:
                            destination_abv = "NA"

                    curr_arrival_dict = {
                        "update_time": update_time,
                        "batch_id": batch_id,
                        "stop_id": stop_id,
                        "arrival_time": arrival_time,
                        "destination": destination_abv,
                        "direction": direction_abv,
                        "status": stop_message if not stop_status_normal else "Normal"
                    }

            tram_update_data.append(curr_arrival_dict)
            
        return tram_update_data
    
    def generate_spark_dataframes(self, spark_session) -> dict:
        data = self.fetch()
        arrivals_df = spark_session.createDataFrame(data, schema=self.get_tram_arrivals_table_schema())
        return [{ 'table_name': 'tram_arrivals', 'spark_df': arrivals_df }]