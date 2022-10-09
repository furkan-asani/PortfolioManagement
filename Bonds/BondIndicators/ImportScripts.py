from datetime import date, datetime
from numpy import NaN
import pandas as pd
import Transactions

class ImportOnVista:
    def __init__(self, sqlConnection, transactionHelper: Transactions.TransactionHelper):
        # You may have to adjust this path according to your path and filename
        self.__filePath = '/home/PortfolioManagement/Import/OnVista.csv'
        self.__sqlConnection = sqlConnection
        self.__transactionHelper = transactionHelper

    def readPositionsAndStoreInDatabase(self):
        df = pd.read_csv(filepath_or_buffer=self.__filePath, header=5,delimiter=";")

        for row in df.itertuples():
            isInvalidRow = row[1] is NaN
            if isInvalidRow:
                continue
            
            transaction = self.__insertIntoTransactionTable(row)

            self.__insertIntoBondsTable(row, transaction)

    def __insertIntoTransactionTable(self, row):
        price = row[11]
            
        if row[11] is not float:
            price = float(row[11].replace(",","."))
            
        date = datetime.strptime(row[6], "%d.%m.%Y") 

        transaction = Transactions.Transaction(row[3], row[4], row[1], date, 'buy', '', price, 'OnVista', row[12], row[10])
            
        self.__transactionHelper.insertIntoDatabase(transaction)
        return transaction

    def __insertIntoBondsTable(self, row, transaction):
        insertBondSQLStatement = f'INSERT INTO "Bond" (isin, wkn, "Comment", "Name") VALUES (\'{transaction.isin}\', \'{transaction.wkn}\', \'\', \'{row[2]}\')'

        self.__sqlConnection.execute(insertBondSQLStatement)

class ImportDKB:
    def __init__(self, sqlConnection, transactionHelper: Transactions.TransactionHelper):
        self.__sqlConnection = sqlConnection
        self.__transactionHelper = transactionHelper
        self.__filePath = '/home/PortfolioManagement/Import/dkb.csv'

    def readPositionsAndStoreInDatabase(self):
        df = pd.read_csv(filepath_or_buffer= self.__filePath, header=5, delimiter=";")

        for row in df.itertuples():
            isInvalidValidRow = row[1] is NaN
            if isInvalidValidRow:
                continue

            transaction = self.__insertIntoTransactionTable(row)

            self.__insertIntoBondsTable(row, transaction)
        pass

    def __insertIntoTransactionTable(self, row):
        
        price = row[5]
        if row[5] is not float:
            price = float(row[5].replace(",", "."))
        
        amountOfBonds = row[1]
        if amountOfBonds is not float:
            amountOfBonds = float(row[1].replace(",", "."))

        transaction = Transactions.Transaction(row[3], row[3], amountOfBonds, date.today(), 'buy', '', price, 'DKB', row[7], '')

        self.__transactionHelper.insertIntoDatabase(transaction)

        return transaction

    def __insertIntoBondsTable(self, row, transaction: Transactions.Transaction):
        insertBondSQLStatement = f'INSERT INTO "Bond" (isin, wkn, "Comment", "Name") VALUES (\'{transaction.isin}\', \'{transaction.wkn}\', \'\', \'{row[4]}\')'

        self.__sqlConnection.execute(insertBondSQLStatement)

class ImportConsors:
    def __init__(self, sqlConnection, transactionHelper: Transactions.TransactionHelper):
        self.__sqlConnection = sqlConnection
        self.__transactionHelper = transactionHelper
        self.__filePath = '/home/PortfolioManagement/Import/Consors.xlsx'
        
    def readPositionsAndStoreInDatabase(self):
        df = pd.read_excel(io=self.__filePath, header=6)
        for row in df.itertuples():
            isInvalidRow = row[3] is NaN
            if isInvalidRow:
                continue

            transaction = self.__insertIntoTransactionTable(row)

            self.__insertIntoBondsTable(row, transaction)
            
    def __insertIntoTransactionTable(self, row):
        transaction = Transactions.Transaction('', row[2], row[4], row[12], 'buy', '', row[5], 'Consors', row[6], row[13])

        self.__transactionHelper.insertIntoDatabase(transaction)

        return transaction

    def __insertIntoBondsTable(self, row, transaction: Transactions.Transaction):
        insertBondSQLStatement = f'INSERT INTO "Bond" (isin, wkn, "Comment", "Name") VALUES (\'{transaction.isin}\', \'{transaction.wkn}\', \'\', \'{row[1]}\')'

        self.__sqlConnection.execute(insertBondSQLStatement)


import sqlalchemy

connectionString = "postgresql+psycopg2://root:password@postgres_db:5432/portfolio"
engine = sqlalchemy.create_engine(connectionString)
connection = engine.connect()

transactionHelper = Transactions.TransactionHelper(connection)

example =ImportConsors(connection, transactionHelper)

example.readPositionsAndStoreInDatabase()