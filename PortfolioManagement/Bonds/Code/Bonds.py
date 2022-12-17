import sqlalchemy
import investiny.info

from PriceDataInvestiny import PriceDataInvestiny


class Bonds:
    def __init__(self, sqlConnection, priceService, isinToSymbolConverter):
        self.__sqlConnection = sqlConnection
        self.priceService = priceService
        self.__isinToSymbolConverter = isinToSymbolConverter
        self.identifyNewBonds()

    def identifyNewBonds(self):

        identifyNewBondsInTransactionSqlStatement = 'SELECT DISTINCT ISIN FROM transaction WHERE isin NOT IN (SELECT DISTINCT ISIN FROM "Bond")'

        newBondsResult = self.__sqlConnection.execute(
            identifyNewBondsInTransactionSqlStatement
        )
        fetchedNewBonds = newBondsResult.fetchall()
        mappedNewBonds = list(map(lambda bond: bond[0], fetchedNewBonds))
        self.mappedNewBonds = mappedNewBonds
        return mappedNewBonds

    def getNameByIsin(self):
        for isin in self.mappedNewBonds:
            name = self.__isinToSymbolConverter.getNameForIsin(isin)
            
            return name

    def storeSymbolForBond(self, isin: str):
        symbol = self.__isinToSymbolConverter.getTickerForISIN(isin)
        if symbol != "n/a":
            self.__sqlConnection.execute(
                f"UPDATE \"Bond\" SET SYMBOL = '{symbol}' WHERE isin LIKE '{isin}'"
            )


connectionString = "postgresql+psycopg2://root:password@postgres_db:5432/portfolio"
engine = sqlalchemy.create_engine(connectionString)
connection = engine.connect()
priceService = PriceDataInvestiny(connection)
# bonds = Bonds(connection, priceService)

# bonds.getNameByIsin()
# print(bonds.identifyNewBonds())
