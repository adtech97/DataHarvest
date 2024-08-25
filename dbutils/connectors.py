import configparser
import psycopg2 as pg

class db_connectors:

    def __init__(self):

        config = configparser.ConfigParser()
        config.read('config.ini')

        self.host = config['DATABASE']['HOST']
        self.port = config['DATABASE']['PORT']
        self.db_name = config['DATABASE']['NAME']
        self.db_user = config['DATABASE']['USER']
        self.db_password = config['DATABASE']['PASSWORD']

        self.connection_str = f"host={self.host} port={self.port} dbname={self.db_name} user={self.db_user} password={self.db_password}"
        self.connection_url = f"jdbc:postgresql://{self.host}:{self.port}/{self.db_name}?user={self.db_user}&password={self.db_password}"

    def pg_connect_exec(self, query):
        self.connection = None
        self.cursor = None

        try:
            print("connecting....")
            self.connection = pg.connect(self.connection_str)
            self.cursor = self.connection.cursor()
            print("Executing sql query....")
            self.cursor.execute(query)
            print("Done executing sql query :)")
            print('connection successfull')
        except pg.Error as e:
            print("error connecting to postgress service:", e)
        
    def commit_transaction(self):
        self.connection.commit()
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()