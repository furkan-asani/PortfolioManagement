import pandas as pd
import Transactions

class ImportOnVista:
    
    def __init__(self, sqlConnection, transactionHelper: Transactions.TransactionHelper):
        # You may have to adjust this path according to your path and filename
        self.__filePath = '/home/PortfolioManagement/Import/OnVista.csv'
        self.__sqlConnection = sqlConnection
        transactionHelper

    def readPositionsAndStoreInDatabase(self):
        df = pd.read_csv(filepath_or_buffer=self.__filePath, header=5,delimiter=";")

        for row in df.itertuples():
            
            pass

    pass

import sqlalchemy

connectionString = "postgresql+psycopg2://root:password@postgres_db:5432/portfolio"
engine = sqlalchemy.create_engine(connectionString)
connection = engine.connect()

example =ImportOnVista(connection)

example.readPositionsAndStoreInDatabase()