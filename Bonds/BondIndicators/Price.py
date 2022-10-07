from datetime import date


class Price:
    def __init__(self, sqlConnection):
        self.__sqlConnection = sqlConnection

    def manuallyInsertPriceIntoDatabase(self, isin: str, price: float, date: date=date.today()):
        """This method can be used in order to manually insert a price for a bond.
           \nYou have to supply the isin, the price and the date as a date object"""
        insertPriceSqlStatement = f"INSERT INTO \"Price\" (isin, price, \"priceDate\")   VALUES ('{isin}', {price}, '{date}')"

        self.__sqlConnection.execute(insertPriceSqlStatement)

import sqlalchemy
connectionString = "postgresql+psycopg2://root:password@postgres_db:5432/portfolio"
engine = sqlalchemy.create_engine(connectionString)
connection = engine.connect()

example = Price(connection)

example.manuallyInsertPriceIntoDatabase('12345678', 10.4, date(year=2022, month=10, day=7))