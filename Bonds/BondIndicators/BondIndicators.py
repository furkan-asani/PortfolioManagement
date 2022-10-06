__package__ = None
from datetime import date, datetime

import pandas as pd

from PriceDataInvestiny import PriceDataInvestiny


class BondIndicators:

    def __init__(self, sqlConnection, priceService):
        self.__sqlConnection = sqlConnection
        self.priceService = priceService

    def getProfitOrLossDataFrame(self, date: date=date.today())-> pd.DataFrame:
        
        profitOrLossDataFrame = []

        for isin in self.__getActiveIsins(date):
            try:
                profitOrLoss = self.getProfitOrLossForAPosition(isin, date)
            except:
                profitOrLoss = 0
            finally:
                profitOrLossDataFrame.append({"isin": isin, "P/L": profitOrLoss, "date": date.strftime("%d/%m/%Y")})
        
        return pd.DataFrame(profitOrLossDataFrame)

    def getDepotDataFrame(self, date: datetime= date.today(), depot: str='%%')-> pd.DataFrame:
        
        depotDataFrame = []
        
        for isin in self.__getActiveIsins(date, depot):
            profitOrLossData = self.__getProfitOrLossData(isin, date)
            depotDataFrame.append({"isin": isin, "amountOfBonds": profitOrLossData["totalAmountOfBondsForThisPosition"], "valueOfThisPosition": profitOrLossData["valueOfPosition"]})

        return pd.DataFrame(depotDataFrame)

    def getPriceHistoryDataFrame(self, isin: str, dateFrom: date, dateTo: date=date.today()):
        # TODO implement this function -> Basically call the api with the exact parameters and convert the response to a dataframe
        pass

    def __getActiveIsins(self, date: date="CURRENT_DATE", depot: str= "'%%'") -> list[str]:
        """This function returns the isins of all active bond positions at the given date"""

        if date != "CURRENT_DATE":
            date = f"'{date}'"

        if depot != "'%%'":
            depot = f"'{depot}'"

        getAllActiveIsinsSqlStatement = f"""WITH BuySum AS (
                                            SELECT isin, SUM(amountofbonds) AS BuySum
                                            FROM transaction
                                            WHERE LOWER(typeoftransaction) LIKE 'buy'
                                            AND transactiondate <= {date}
                                            AND LOWER(depot) LIKE {depot}
                                            GROUP BY isin
                                        ),

                                            SellSum AS (
                                                SELECT isin, SUM(amountofbonds) AS SaleSum
                                                FROM transaction
                                                WHERE LOWER(typeoftransaction) LIKE 'sell'
                                                AND transactiondate <= {date}
                                                AND LOWER(depot) LIKE {depot}
                                                GROUP BY isin
                                            ),

                                            CoalesceNullValues AS (
                                            SELECT BuySum.isin, BuySum, CASE WHEN SaleSum is null THEN 0 ELSE SaleSum END AS SellSum
                                            FROM BuySum LEFT JOIN SellSum ON BuySum.isin = SellSum.isin

                                            )
                                            SELECT isin
                                            FROM CoalesceNullValues
                                            WHERE isin is not null
                                            AND (buysum - sellsum) > 0
                                            GROUP BY isin;"""

        activeIsinResult = self.__sqlConnection.execute(getAllActiveIsinsSqlStatement)
        fetchedActiveIsins = list(map(lambda isinTuple: isinTuple[0],activeIsinResult.fetchall()))
        return fetchedActiveIsins

    def getProfitOrLossForAPosition(self, isin: str, date: date=date.today())-> float:

        profitOrLossData = self.__getProfitOrLossData(isin, date)

        return profitOrLossData["valueOfPosition"]  - profitOrLossData["totalSumOfPurchases"] 

    def __getProfitOrLossData(self, isin, date):
        """This method returns the necessary data in order to calculate the profit or loss of a position/transaction ..."""
        totalSumOfPurchases = 0
        totalAmountOfBondsForThisPosition = 0

        allPurchases = self.__getAllPurchases(date, isin)

        allSales = self.__getAllSalesList(date, isin, True)

        for purchase in self.__getListOfPurchasesWhichAreHeld(allPurchases, allSales):
            totalSumOfPurchases += purchase.amount * purchase.price
            totalAmountOfBondsForThisPosition += purchase.amount

        valueOfPosition = self.priceService.getPriceByIsin(isin) * totalAmountOfBondsForThisPosition
        return {"totalSumOfPurchases":totalSumOfPurchases,"valueOfPosition": valueOfPosition, "totalAmountOfBondsForThisPosition":totalAmountOfBondsForThisPosition}

    def calculateProfitOrLossForASale(self, transactionId: int):
        # Get all buys until the date of the transaction
        # Get all sales without the referenced sale until the date of the transaction
        # Get the referenced transaction sales data

        getReferencedTransactionDataSQLStatement = f'Select * from transaction where "transactionID" = {transactionId}'

        transactionResult = self.__sqlConnection.execute(getReferencedTransactionDataSQLStatement)
        fetchedTransaction = transactionResult.fetchall()[0]
        
        transactionDate = fetchedTransaction[3]
        isin = fetchedTransaction[0]

        saleToCalculate = Sale(fetchedTransaction[2], fetchedTransaction[6]) 

        allPurchasesList =  self.__getAllPurchases(transactionDate, isin)

        allSalesList = self.__getAllSalesList(transactionDate, isin)

        allPurchasesList = self.__getListOfPurchasesWhichAreHeld(allPurchasesList, allSalesList)

        totalProfit = 0

        for purchase in allPurchasesList:
            totalProfit += min(saleToCalculate.amount, purchase.amount) * (saleToCalculate.price - purchase.price)
            saleToCalculateAmountCopy = saleToCalculate.amount
            saleToCalculate.amount = max(saleToCalculate.amount - purchase.amount, 0)
            purchase.amount = max(purchase.amount - saleToCalculateAmountCopy, 0)
            if(saleToCalculate.amount == 0):
                break

        return totalProfit

    def __getListOfPurchasesWhichAreHeld(self, allPurchasesList: list, allSalesList: list)-> list:
        for sale in allSalesList:
            for purchase in allPurchasesList:
                if(purchase.amount == 0):
                    continue
                purchaseAmountCopy = purchase.amount
                purchase.amount = max(purchase.amount - sale.amount, 0)
                sale.amount = max(sale.amount - purchaseAmountCopy, 0)
                if(purchase.amount == 0):
                    continue
                if(sale.amount == 0):
                    break
        
        allPurchasesListIterator = filter(lambda purchase: (purchase.amount > 0), allPurchasesList)

        allPurchasesList = list(allPurchasesListIterator)
        return allPurchasesList

    def __getAllSalesList(self, transactionDate, isin, inclusiveDate: bool=False):

        operator = "<"

        if inclusiveDate:
            operator = "<="

        getAllSalesSqlStatement = f"Select * from transaction where isin LIKE '{isin}' AND typeoftransaction LIKE 'sell' AND transactiondate {operator} '{transactionDate}'"

        allSales = self.__sqlConnection.execute(getAllSalesSqlStatement)

        fetchedAllSales = allSales.fetchall()

        allSalesList = []

        for sale in fetchedAllSales:
            saleObject = Sale(sale[2], sale[6])
            allSalesList.append(saleObject)

        return allSalesList

    def __getAllPurchases(self, transactionDate, isin)-> list:
        getAllPurchasesSqlStatement = f"Select * from transaction where isin LIKE '{isin}' AND LOWER(typeoftransaction) LIKE 'buy' AND transactiondate <= '{transactionDate}'"

        allPurchases = self.__sqlConnection.execute(getAllPurchasesSqlStatement)

        fetchedAllPurchases = allPurchases.fetchall()

        allPurchasesList = []
        for purchase in fetchedAllPurchases:
            purchaseObject = Purchase(purchase[2], purchase[6])
            allPurchasesList.append(purchaseObject)

        return allPurchasesList

class Transaction:
    def __init__(self, amount, price):
        self.amount = amount
        self.price = price

class Sale(Transaction):
    pass

class Purchase(Transaction):
    pass

import sqlalchemy
connectionString = "postgresql+psycopg2://root:password@postgres_db:5432/portfolio"
engine = sqlalchemy.create_engine(connectionString)
connection = engine.connect()

priceService = PriceDataInvestiny(connection)

bondIndicators = BondIndicators(connection, priceService)

#print(bondIndicators.getProfitOrLossDataFrame())

print(bondIndicators.getDepotDataFrame(depot='dkb'))