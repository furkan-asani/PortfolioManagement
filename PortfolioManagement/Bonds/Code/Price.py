from datetime import date
from re import I

from BondIndicators import BondIndicators
from PriceDataInvestiny import PriceDataInvestiny


class Price:
    def __init__(self, sqlConnection, bondIndicators: BondIndicators, priceService: PriceDataInvestiny):
        self.__sqlConnection = sqlConnection
        self.__bondIndicators = bondIndicators
        self.__priceService = priceService

    def manuallyInsertPriceIntoDatabase(self, isin: str, price: float, date: date=date.today()):
        """This method can be used in order to manually insert a price for a bond.
           \nYou have to supply the isin, the price and the date as a date object"""
        insertPriceSqlStatement = f"INSERT INTO \"Price\" (isin, price, \"priceDate\")   VALUES ('{isin}', {price}, '{date}')"

        self.__sqlConnection.execute(insertPriceSqlStatement)

    def __storePricesForActivePositions(self, fromDate: date=None, toDate: date=date.today()):
        """This function accepts a from and to date and retrieves the price for all active bond positions in your depot. If called with no arguments
        then it will fetch all prices since the last update."""
        
        if(fromDate is None):
            latestDateResult = self.__sqlConnection.execute('SELECT max("priceDate")+1 AS priceDate from "Price"')
            fetchedLatestDate = latestDateResult.fetchall()
            fromDate = fetchedLatestDate[0][0]


        for isin in self.__bondIndicators.getActiveIsins(fromDate):
            priceDataHistoryDataFrame = self.__priceService.getPriceHistory(isin, fromDate, toDate)
            
            for row in priceDataHistoryDataFrame.itertuples():
                isin = row[1]
                date = row[2]
                price = row[3]
                self.manuallyInsertPriceIntoDatabase(isin, price, date)

import sqlalchemy
connectionString = "postgresql+psycopg2://root:password@postgres_db:5432/portfolio"
engine = sqlalchemy.create_engine(connectionString)
connection = engine.connect()

priceService = PriceDataInvestiny(connection)
bondIndicators = BondIndicators(connection, priceService)

example = Price(connection, bondIndicators, priceService)

#example.manuallyInsertPriceIntoDatabase('12345678', 10.4, date(year=2022, month=10, day=7))

#example.storePricesForActivePositions(date(year=2022, month=9, day=1), date(year=2022, month=10, day=1))
example.storePricesForActivePositions()