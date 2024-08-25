import time
from dbutils import connectors
from pyspark.sql import SparkSession
from models import TramApiHandler, BusApiHandler, BikeApiHandler,BusRouteApiHAndler


soft_shutdown_flag = False

# A function to write the data to the database
def write_to_database(df, table_name):
    db_connector = connectors.db_connectors()
    print("Connecting")
    df.write\
    .format("jdbc")\
    .option("url", db_connector.connection_url)\
    .option("dbtable", table_name)\
    .option("driver", "org.postgresql.Driver")\
    .mode("append")\
    .save()
    print('Connected')



if __name__ == "__main__":

    interval = 86400

    spark = SparkSession.builder.appName("RealTimeETL").getOrCreate()
    bus_route = BusRouteApiHAndler.BusDataReference()
    create_table_queries = []
    create_table_queries.append(BusRouteApiHAndler.get_routes_create_table_query())
    create_table_queries.append(BusRouteApiHAndler.remove_data_fromTable())
    pg_conn = connectors.db_connectors()
    for query in create_table_queries:
        print(f"Executing query: {query}")
        pg_conn.pg_connect_exec(query=query)
        pg_conn.commit_transaction()
    try:
        while not soft_shutdown_flag:
            bus_route_df = BusRouteApiHAndler.generate_spark_dataframes(bus_route,spark)
            for row in bus_route_df:
                df = row.get('spark_df')
                table_name = row.get('table_name')
                write_to_database(df, table_name)
                print("Bus route data updated successfully.")
            time.sleep(interval)

    except KeyboardInterrupt:
        print("Soft shutdown initiated...")
        soft_shutdown_flag = True

    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        spark.stop()
        print("Application stopped.")




 


  
