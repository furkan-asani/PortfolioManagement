from datetime import date
class Transaction:
    def __init__(
        self,
        isin: str,
        wkn: str,
        amountofbonds: float,
        transactiondate: date,
        typeoftransaction: str,
        transactioncomment: str,
        price: float,
        depot: str,
        currency: str,
        exchange: str,
    ):
        self.isin = isin
        self.wkn = wkn
        self.amountofbonds = amountofbonds
        self.transactiondate = transactiondate
        self.typeoftransaction = typeoftransaction
        self.transactioncomment = transactioncomment
        self.price = price
        self.depot = depot
        self.currency = currency
        self.exchange = exchange

class TransactionHelper:
    def __init__(self, sqlConnection):
        self.__sqlConnection = sqlConnection
        
    def insertIntoDatabase(self, transaction: Transaction):
        insertSqlStatement =f"""
            INSERT INTO transaction (isin, wkn, amountofbonds, transactiondate, typeoftransaction, transactioncomment, price, depot, currency, exchange)
            VALUES ('{transaction.isin}', '{transaction.wkn}', {transaction.amountofbonds}, '{transaction.transactiondate}', '{transaction.typeoftransaction}', '{transaction.transactioncomment}', {transaction.price}, '{transaction.depot}', '{transaction.currency}', '{transaction.exchange}')
        """
        self.__sqlConnection.execute(insertSqlStatement)

        getLatestTransactionIdSqlStatement = 'SELECT "transactionID" from transaction ORDER BY transactiondate DESC LIMIT 1'

        latestTransactionIdResult = self.__sqlConnection.execute(getLatestTransactionIdSqlStatement)

        fetchedLatestTransactionId = latestTransactionIdResult.fetchall()

        return fetchedLatestTransactionId[0][0]



import sqlalchemy
connectionString = "postgresql+psycopg2://root:password@postgres_db:5432/portfolio"
engine = sqlalchemy.create_engine(connectionString)
connection = engine.connect()

example = TransactionHelper(connection)

transaction = Transaction('12345678','12345678', 1, date(year=2022, month=10, day=8), 'sell', 'Sample', 35.58, 'DKB', 'EUR', 'Xetra')

example.insertIntoDatabase(transaction=transaction)