from pyspark.sql import SparkSession
from cssp import dublin_bikes, dublin_tram
from dbutils import connectors_tram
import time

def process_dublin_bikes(spark):
    dub_bikes = dublin_bikes.DubBikes(None)
    latest_snap = dub_bikes.fetch()
    table_name = "bike_station_data"
    schema = dub_bikes.get_table_schema()
    dubbike_spark_df = spark.createDataFrame(latest_snap, schema=schema)
    dubbike_pandas_df = dubbike_spark_df.toPandas()
    
    conn = connectors_tram.db_connectors(host="postgres-service", db_name="scm-db", db_user='postgres', db_password='sustainable')
    conn.pg_connect_exec(dub_bikes.get_create_table_query())
    insert_data_query = f"INSERT INTO {table_name} ({', '.join(dubbike_pandas_df.columns)}) VALUES"
    values = []
    for index, row in dubbike_pandas_df.iterrows():
        row_values = [" '{}'".format(value.replace("'", "''")) if isinstance(value, str) else str(value) for value in row]
        values.append("({})".format(', '.join(row_values)))

    insert_data_query +=', '.join(values)

def escape_single_quotes(value):
    return value.replace("'", "''")

def process_luas_trams(spark):
    dub_trams = dublin_tram.LuasRealTimeDataHandler()
    latest_tram_snap = dub_trams.fetch()
    table_name = "tram_data"
    schema = dub_trams.get_table_schema()
    tram_spark_df = spark.createDataFrame(latest_tram_snap, schema=schema)
    tram_pandas_df = tram_spark_df.toPandas()
    
    conn = connectors_tram.db_connectors(host="postgres-service", db_name="scm-db", db_user='postgres', db_password='sustainable')
    conn.pg_connect_exec(dub_trams.get_create_table_query())

    insert_data_query = """
    INSERT INTO tram_data (composite_key, arrival_time, day_type, stop, status, direction, destination)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    for index, row in tram_pandas_df.iterrows():
        data = tuple(escape_single_quotes(str(value)) for value in row.values)
        conn.pg_connect_exec(insert_data_query, data)

    
def process_dublin_buses(spark):
    pass

def process_dublin_pedes(spark):
    pass

if __name__ == "__main__":
    interval = 300
    while True:
        spark = SparkSession.builder.appName("RealTimeETL").getOrCreate()
        
        process_luas_trams(spark)

        time.sleep(interval)
        spark.stop()    
