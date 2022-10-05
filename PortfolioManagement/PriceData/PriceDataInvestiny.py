from datetime import datetime

from investiny import historical_data, search_assets
from dateutil.relativedelta import relativedelta
import pandas as pd
import sqlalchemy

class PriceDataInvestiny():

    def __init__(self, sqlConnection):
        self.__sqlConnection = sqlConnection

    def getPriceByIsinViaInvestingIdCSV(self, isin: str, date: datetime= datetime.today()) -> float:
        
        # Create a date which is the supplied date minus one
        # Convert the date into a string 'm/d/y'
        # get investing id by isin
        # call historical data
        # return the price
        # if historical data doesnt find anything try the database

        date, fromDate = self.__convertDatetimesToDateStringsForInvestPy(date)

        try:
            investingId = self.__getInvestingId(isin)
            priceData = historical_data(investing_id=investingId, from_date=fromDate, to_date=date)['open'][0]

        except:
            return self.__getPriceFromDatabase(isin)       

        return priceData

    def __convertDatetimesToDateStringsForInvestPy(self, date):

        fromDate = date - relativedelta(date, days=1)
        dateTimeFormat = "%m/%d/%Y"
        date = date.strftime(dateTimeFormat)
        fromDate = fromDate.strftime(dateTimeFormat)

        return date,fromDate

    def __getInvestingId(self, isin: str) -> int:
        investingIDsDataFrame = pd.read_csv(filepath_or_buffer='/home/PortfolioManagement/Resources/InvestingIDs.csv')

        investingRecord = investingIDsDataFrame[(investingIDsDataFrame["isin"] == isin) & (investingIDsDataFrame["currency"] == "EUR")].head(1)
        id = investingRecord.iloc[0]["id"]

        return id

    def __getPriceFromDatabase(self, isin) -> float:
        getLatestPriceSQLStatement = f'SELECT price FROM "Price" WHERE isin LIKE \'{isin}\' ORDER BY "priceDate" DESC LIMIT 1;'
        priceData = self.__sqlConnection.execute(getLatestPriceSQLStatement)
        fetchedPriceData = priceData.fetchall()
        if len(fetchedPriceData) == 0:
            return 0
        return fetchedPriceData[0][0]

    def getPriceByIsinViaSearchAssets(self, isin: str, date: datetime=datetime.today()) -> float:
        
        date, fromDate = self.__convertDatetimesToDateStringsForInvestPy(date)
        
        try:
            investingId = self.__getInvestingIdBySearchAssetsApi(isin)
            priceData = historical_data(investing_id=investingId, from_date=fromDate, to_date=date)['open'][0]
        except:

            return self.__getPriceFromDatabase(isin)    
        
        return priceData

    def __getInvestingIdBySearchAssetsApi(self, isin):

        allowedExchanges = ["Frankfurt", "Xetra", "Vienna"]
        returnedResults = search_assets(query=isin)
        returnedResultsIterator = filter(lambda result: result["exchange"] in allowedExchanges, returnedResults)
        returnedResults = list(returnedResultsIterator)
        investingId = returnedResults[0]["ticker"] if returnedResults[0]["ticker"] != None else Exception()
        return investingId

connectionString = "postgresql+psycopg2://root:password@postgres_db:5432/portfolio"
engine = sqlalchemy.create_engine(connectionString)
connection = engine.connect()

example = PriceDataInvestiny(connection)

example.getPriceByIsinViaSearchAssets("IE0005042456")
