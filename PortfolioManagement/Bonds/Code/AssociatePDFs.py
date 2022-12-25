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
        self.__onlyFiles = [
            f
            for f in os.listdir(self.__fileDropPath)
            if os.path.isfile(os.path.join(self.__fileDropPath, f))
        ]
        self.__basepath = "/home/PortfolioManagement/PDFs/Transactions"

    def associatePDFsWithTransaction(
        self, transactionId: int, typeOfPDFs: str = "Transaction", comment: str = ""
    ):
        """This function accepts a transactionId (can be retrieved by database or as a return from the TransactionHelper.insertIntoDatabase Method).
        The type of the pdf you want to associate with the transaction (for example Additional Information or the transaction pdf.
        An additional comment.
        This function creates a link between a transaction and the pdfs which are currently in the FileDrop Folder.
        The files in the filedrop folder are moved and renamed to the PDFs folder into the respective Transaction folders
        An entry is written to the database which links the transaction to the pdf"""

        self.__getFilesFromFileDrop()

        # TODO Falls es keine BondId rufe eine Funktion auf, welche die BondIds extrahiert und in die DB einpflegt
        fetchedTransactionResult = self.__getTransaction(transactionId)
        date = fetchedTransactionResult[3]

        fetchedBondId = self.__getBondId(fetchedTransactionResult)

        destinationPath = f"{self.__basepath}/{date.year}/{date.month}/{date.day}"
        self.__createFolderIfDoesntExist(destinationPath)

        self.__iterateOverFileDropAndCreateAssociations(
            transactionId, typeOfPDFs, date, fetchedBondId, destinationPath, comment
        )

    def __getFilesFromFileDrop(self):
        self.__onlyFiles = [
            f
            for f in os.listdir(self.__fileDropPath)
            if os.path.isfile(os.path.join(self.__fileDropPath, f))
        ]

    def __iterateOverFileDropAndCreateAssociations(
        self,
        transactionId,
        typeOfPDFs,
        date,
        fetchedBondId,
        destinationPath,
        comment: str = "",
    ):
        newPath = f"{destinationPath}/TransactionPDF_"

        self.__iterateOverFileAndInsertIntoDatabase(
            date, transactionId, fetchedBondId, newPath, typeOfPDFs, comment
        )

    def __insertAssociationIntoDatabase(
        self, transactionId: int, fetchedBondId: int, pdfId: int
    ):
        insertAssociationSqlStatement = f'INSERT INTO "AssociatedFiles" ( "FKBondId", fkpdfid, "FKTransactionID") VALUES ({fetchedBondId}, {pdfId}, {transactionId})'
        self.__sqlConnection.execute(insertAssociationSqlStatement)

    def __createFolderIfDoesntExist(self, destinationPath):
        if not os.path.exists(destinationPath):
            os.makedirs(destinationPath)

    def __getBondId(self, isin: str):
        getBondIdSqlStatement = (
            f'SELECT "BondID" FROM "Bond" WHERE isin = \'{isin[0]}\' LIMIT 1'
        )
        bondIdResult = self.__sqlConnection.execute(getBondIdSqlStatement)
        fetchedBondId = bondIdResult.fetchall()[0][0]
        return fetchedBondId

    def __getTransaction(self, transactionId: int):
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

    def associatePDFWithBond(
        self, isin: str, typeOfPDFs: str = "Transaction", comment: str = ""
    ):
        """This function accepts a isin (can be retrieved by database).
        This function creates a link/association between a bond and the pdfs which are currently in the FileDrop Folder.
        The files in the filedrop folder are moved and renamed to the PDFs folder into the respective bond folders and an entry is written to the database which links the pdf to a bond"""

        self.__getFilesFromFileDrop()

        filePath = f"/home/PortfolioManagement/PDFs/Bonds/{isin}/General"
        if not os.path.exists(filePath):
            os.makedirs(filePath)

        transactionId = self.__getLatestTransactionIdForBond(isin)
        bondId = self.__getBondId([isin])
        self.__iterateOverFilesAndCreateBondPDFAssociations(
            filePath, transactionId, bondId, typeOfPDFs
        )

    def __iterateOverFilesAndCreateBondPDFAssociations(
        self, filePath, transactionId, bondId, pdfType="General"
    ):
        # TODO the id isn't used correctly in this case → fix that
        newPath = f"{filePath}/GeneralInformation_"

        self.__iterateOverFileAndInsertIntoDatabase(
            date.today(), transactionId, bondId, newPath, pdfType
        )

    def __iterateOverFileAndInsertIntoDatabase(
        self, date: date, transactionId, bondId, newPath, pdfType, comment: str = ""
    ):
        id = 1
        for file in self.__onlyFiles:

            os.rename(os.path.join(self.__fileDropPath, file), f"{newPath}{id}.pdf")
            pdfEntry = PDFEntry(date, pdfType, comment, newPath)
            pdfId = self.__insertPDFIntoDatabase(pdfEntry)
            self.__insertAssociationIntoDatabase(transactionId, bondId, pdfId)
            id = id + 1

    def __getLatestTransactionIdForBond(self, isin: str):

        getLatestTransactionIdSQLStatement = f'SELECT "transactionID" FROM transaction WHERE isin LIKE \'{isin}\' ORDER BY "transactionID" DESC LIMIT 1'
        latestTransactionIdResult = self.__sqlConnection.execute(
            getLatestTransactionIdSQLStatement
        )
        return latestTransactionIdResult.fetchall()[0][0]


# import sqlalchemy

# connectionString = "postgresql+psycopg2://root:password@postgres_db:5432/portfolio"
# engine = sqlalchemy.create_engine(connectionString)
# connection = engine.connect()

# example = AssociatePDFs(connection)

# example.associatePDFWithBond('CH0012032048')
