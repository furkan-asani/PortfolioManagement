from datetime import date
import os


class PDFEntry:
    def __init__(self, date: date, type: str, comment: str, filepath: str):
        self.date = date
        self.type = type
        self.comment = comment
        self.filepath = filepath


class AssociatePDFs:
    def __init__(self, sqlConnection):
        self.__sqlConnection = sqlConnection
        self.__fileDropPath = "/home/PortfolioManagement/FileDrop"
        self.__onlyFiles = onlyFiles = [
            f
            for f in os.listdir(self.__fileDropPath)
            if os.path.isfile(os.path.join(self.__fileDropPath, f))
        ]
        self.__basepath = "/home/PortfolioManagement/PDFs/Transactions"

    def associatePDFsWithTransaction(
        self, transactionId: int, typeOfPDFs: str = "Transaction", comment: str = ""
    ):
        # TODO Falls es keine BondId rufe eine Funktion auf, welche die BondIds extrahiert und in die DB einpflegt
        fetchedTransactionResult = self.__getTransaction(transactionId)
        date = fetchedTransactionResult[3]

        fetchedBondId = self.__getBondId(fetchedTransactionResult)

        destinationPath = f"{self.__basepath}/{date.year}/{date.month}/{date.day}"
        self.__createFolderIfDoesntExist(destinationPath)

        self.__iterateOverFileDropAndCreateAssociations(
            transactionId, typeOfPDFs, comment, date, fetchedBondId, destinationPath
        )

    def __iterateOverFileDropAndCreateAssociations(
        self, transactionId, typeOfPDFs, comment, date, fetchedBondId, destinationPath
    ):
        id = 1
        for file in self.__onlyFiles:
            newPath = f"{destinationPath}/TransactionPDF_{id}.pdf"
            os.rename(
                os.path.join(self.__fileDropPath, file),
                newPath,
            )
            pdfEntry = PDFEntry(date, typeOfPDFs, comment, newPath)
            pdfId = self.__insertPDFIntoDatabase(pdfEntry)
            self.__insertAssociationIntoDatabase(transactionId, fetchedBondId, pdfId)
            id += 1

    def __insertAssociationIntoDatabase(self, transactionId, fetchedBondId, pdfId):
        insertAssociationSqlStatement = f'INSERT INTO "AssociatedFiles" ( "FKBondId", fkpdfid, "FKTransactionID") VALUES ({fetchedBondId}, {pdfId}, {transactionId})'
        self.__sqlConnection.execute(insertAssociationSqlStatement)

    def __createFolderIfDoesntExist(self, destinationPath):
        if not os.path.exists(destinationPath):
            os.makedirs(destinationPath)

    def __getBondId(self, isin):
        getBondIdSqlStatement = f'SELECT "BondID" FROM "Bond" WHERE isin = \'{isin[0]}\''
        bondIdResult = self.__sqlConnection.execute(getBondIdSqlStatement)
        fetchedBondId = bondIdResult.fetchall()[0][0]
        return fetchedBondId

    def __getTransaction(self, transactionId):
        getTransactionStatement = (
            f'SELECT * from transaction WHERE "transactionID" = {transactionId}'
        )
        transactionResult = self.__sqlConnection.execute(getTransactionStatement)
        fetchedTransactionResult = transactionResult.fetchall()[0]
        return fetchedTransactionResult

    def __insertPDFIntoDatabase(self, pdfEntry: PDFEntry) -> int:

        insertPDFIntoDatabaseSqlStatement = f"INSERT INTO \"PDFs\" (date, type, comment, filepath) VALUES ('{pdfEntry.date}', '{pdfEntry.type}', '{pdfEntry.comment}', '{pdfEntry.filepath}')"
        self.__sqlConnection.execute(insertPDFIntoDatabaseSqlStatement)

        getLatestPDFIdSqlStatement = (
            'SELECT pdfid FROM "PDFs" ORDER By pdfid DESC LIMIT 1'
        )
        latestPDFIdResult = self.__sqlConnection.execute(getLatestPDFIdSqlStatement)
        fetchedLatestPDFId = latestPDFIdResult.fetchall()
        return fetchedLatestPDFId[0][0]


import sqlalchemy

connectionString = "postgresql+psycopg2://root:password@postgres_db:5432/portfolio"
engine = sqlalchemy.create_engine(connectionString)
connection = engine.connect()

example = AssociatePDFs(connection)

example.associatePDFsWithTransaction(40)
