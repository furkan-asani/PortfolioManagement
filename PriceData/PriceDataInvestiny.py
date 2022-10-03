from datetime import datetime

from investiny import historical_data
from dateutil.relativedelta import relativedelta
import pandas as pd
import sqlalchemy

class PriceDataInvestiny():

    def __init__(self, sqlConnection):
        self.__sqlConnection = sqlConnection

    def getPriceByIsin(self, isin: str, date: datetime= datetime.today()) -> float:
        
        # Create a date which is the supplied date minus one
        # Convert the date into a string 'm/d/y'
        # get investing id by isin
        # call historical data
        # return the price
        # if historical data doesnt find anything try the database

        fromDate = date - relativedelta(date, days=1)

        dateTimeFormat = "%m/%d/%Y"
        date = date.strftime(dateTimeFormat)
        fromDate = fromDate.strftime(dateTimeFormat)

        try:
            investingId = self.__getInvestingId(isin)
            priceData = historical_data(investing_id=investingId, from_date=fromDate, to_date=date)['open'][0]

        except:

            getLatestPriceSQLStatement = f'SELECT price FROM "Price" WHERE isin LIKE \'{isin}\' ORDER BY "priceDate" DESC LIMIT 1;'
            priceData = self.__sqlConnection.execute(getLatestPriceSQLStatement)
            fetchedPriceData = priceData.fetchall()
            if len(fetchedPriceData) == 0:
                return 0
            return fetchedPriceData[0][0]

        return priceData

    def __getInvestingId(self, isin: str) -> int:
        investingIDsDataFrame = pd.read_csv(filepath_or_buffer='/home/PortfolioManagement/Resources/InvestingIDs.csv')

        investingRecord = investingIDsDataFrame[(investingIDsDataFrame["isin"] == isin) & (investingIDsDataFrame["currency"] == "EUR")].head(1)
        id = investingRecord.iloc[0]["id"]

        return id


connectionString = "postgresql+psycopg2://root:password@postgres_db:5432/portfolio"
engine = sqlalchemy.create_engine(connectionString)
connection = engine.connect()

example = PriceDataInvestiny(connection)

example.getPriceByIsin("IE0005042456")
