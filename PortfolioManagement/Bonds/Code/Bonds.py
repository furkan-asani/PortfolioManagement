import sqlalchemy
import investiny.info

from PriceDataInvestiny import PriceDataInvestiny

class Bonds:
    def __init__(self, sqlConnection, priceService):
        self.__sqlConnection = sqlConnection
        self.priceService = priceService
        self.identifyNewBonds()

    def identifyNewBonds(self):
        
        identifyNewBondsInTransactionSqlStatement = 'SELECT DISTINCT ISIN FROM transaction WHERE isin NOT IN (SELECT DISTINCT ISIN FROM "Bond")'

        newBondsResult = self.__sqlConnection.execute(identifyNewBondsInTransactionSqlStatement)
        fetchedNewBonds = newBondsResult.fetchall()
        mappedNewBonds = list(map(lambda bond: bond[0], fetchedNewBonds))
        self.mappedNewBonds = mappedNewBonds
        return mappedNewBonds

    def getNameByIsin(self):
        for isin in self.mappedNewBonds:
            bondInformation = self.priceService.getBondInformation(isin)
            name = bondInformation[0]["name"]
        pass

connectionString = "postgresql+psycopg2://root:password@postgres_db:5432/portfolio"
engine = sqlalchemy.create_engine(connectionString)
connection = engine.connect()
priceService = PriceDataInvestiny(connection)
bonds = Bonds(connection, priceService)

bonds.getNameByIsin()
print(bonds.identifyNewBonds())