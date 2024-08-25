import json
from dbutils import connectors

def insert_tram_stops():

    db_connection = connectors.db_connectors()
    
    # Create tram_stops table
    query = """
        CREATE TABLE IF NOT EXISTS tram_stops (
            id SERIAL PRIMARY KEY,
            code VARCHAR(255),
            name VARCHAR(255),
            latitude REAL,
            longitude REAL,
            line VARCHAR(255)
        );
    """
    db_connection.pg_connect_exec(query)
    db_connection.commit_transaction()

    # Read the tram stops from the JSON file
    with open('data/TramStops.json', 'r') as f:
        tram_stops = json.load(f)

    # Insert tram stops into the tram_stops table
    db_connection = connectors.db_connectors()
    for stop in tram_stops:
        query = f"""
            INSERT INTO tram_stops (code, name, latitude, longitude, line)
            VALUES ('{stop['abrev']}', '{stop['name'].replace("'", "''")}', {stop['lat']}, {stop['long']}, '{stop['line']}');
        """
        db_connection.pg_connect_exec(query)
        db_connection.commit_transaction()

def insert_bike_stations():

    db_connection = connectors.db_connectors()
    
    # Create bike_stations table
    query = """
        CREATE TABLE IF NOT EXISTS bike_stations (
            id INTEGER PRIMARY KEY,
            name VARCHAR(255),
            latitude REAL,
            longitude REAL,
            capacity INTEGER
        );
    """
    db_connection.pg_connect_exec(query)
    db_connection.commit_transaction()

    # Read the bike stations from the CSV file
    with open('data/BikeStations.csv', 'r') as f:
        bike_stations = f.readlines()

    # Insert bike stations into the bike_stations table
    db_connection = connectors.db_connectors()
    for station in bike_stations[1:]:
        station = station.split(',')
        query = f"""
            INSERT INTO bike_stations (id, name, latitude, longitude, capacity)
            VALUES ({station[0]}, '{station[1].replace("'", "''")}', {station[2]}, {station[3]}, {station[4]});
        """
        db_connection.pg_connect_exec(query)
        db_connection.commit_transaction()

def insert_bike_distances():
    
    db_connection = connectors.db_connectors()
    
    # Create bike_distances table
    query = """
        CREATE TABLE IF NOT EXISTS bike_distances (
            station1 INTEGER,
            station2 INTEGER,
            distance REAL
        );
    """
    db_connection.pg_connect_exec(query)
    db_connection.commit_transaction()

    # Read the bike distances from the CSV file
    with open('data/BikeStationDistances.csv', 'r') as f:
        bike_distances = f.readlines()

    # Insert bike distances into the bike_distances table
    db_connection = connectors.db_connectors()
    for i, distance in enumerate(bike_distances[1:]):
        distance = distance.split(',')
        query = f"""
            INSERT INTO bike_distances (id, station_from_id, station_to_id, distance)
            VALUES ({i}, {distance[0]}, {distance[1]}, {distance[2]});
        """
        db_connection.pg_connect_exec(query)
        db_connection.commit_transaction()

def create_tram_batch_id_sequence():
    db_connection = connectors.db_connectors()
    query = """
        CREATE SEQUENCE IF NOT EXISTS tram_batch_id_seq
            START WITH 1
            INCREMENT BY 1;
    """
    db_connection.pg_connect_exec(query)
    db_connection.commit_transaction()

if __name__ == "__main__":
    create_tram_batch_id_sequence()
    insert_bike_distances()
    insert_bike_stations()
    insert_tram_stops()
