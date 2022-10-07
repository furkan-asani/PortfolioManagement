class AssociatePDFs:
    def __init__(self, sqlConnection):
        self.__sqlConnection = sqlConnection
        

    def associatePDFsWithTransaction(self, transactionId: int):
        getTransactionStatement = f'SELECT * from transaction WHERE "transactionID" = {transactionId}'
        transactionResult = self.__sqlConnection.execute(getTransactionStatement)
        fetchedTransactionResult = transactionResult.fetchall()[0]
        # use the date of the transaction in order to determine the folder in which the pdfs should be moved
        pass