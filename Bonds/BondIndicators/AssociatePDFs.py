import os

class AssociatePDFs:
    def __init__(self, sqlConnection):
        self.__sqlConnection = sqlConnection
        

    def associatePDFsWithTransaction(self, transactionId: int):
        getTransactionStatement = f'SELECT * from transaction WHERE "transactionID" = {transactionId}'
        transactionResult = self.__sqlConnection.execute(getTransactionStatement)
        fetchedTransactionResult = transactionResult.fetchall()[0]
        date = fetchedTransactionResult[3]
        id = 1
        getBondIdSqlStatement = f'SELECT "BondID" FROM "Bond" WHERE isin = \'{fetchedTransactionResult[0]}\''
        bondIdResult = self.__sqlConnection.execute(getBondIdSqlStatement)
        fetchedBondId = bondIdResult.fetchall()[0][0]
        
        insertAssociationSqlStatement = f'INSERT INTO "AssociatedFiles" ( "FKBondId", fkpdfid, "FKTransactionID") VALUES ({fetchedBondId}, , {transactionId})'
        # use the date of the transaction in order to determine the folder in which the pdfs should be moved
        fileDropPath = "/home/PortfolioManagement/FileDrop"
        basePath = "/home/PortfolioManagement/PDFs/Transactions"
        destinationPath = f"{basePath}/{date.year}/{date.month}/{date.day}"
        if not os.path.exists(destinationPath):
            os.makedirs(destinationPath)
        onlyFiles = [f for f in os.listdir(fileDropPath) if os.path.isfile(os.path.join(fileDropPath, f))]
        for file in onlyFiles:
            os.rename(os.path.join(fileDropPath, file), f'{destinationPath}/TransactionPDF{id}.pdf')
            self.__sqlConnection.execute()
            id += 1
        pass

    def insertPdfsIntoDatabase(self):
        pass

import sqlalchemy
connectionString = "postgresql+psycopg2://root:password@postgres_db:5432/portfolio"
engine = sqlalchemy.create_engine(connectionString)
connection = engine.connect()

example = AssociatePDFs(connection)

example.associatePDFsWithTransaction(40)