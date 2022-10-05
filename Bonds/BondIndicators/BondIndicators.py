from datetime import date, datetime


class BondIndicators:

    def __init__(self, sqlConnection, priceService: PriceData):
        self.__sqlConnection = sqlConnection
        self.priceService = priceService

    def getProfitOrLossDataFrame(self, date: date=date.today()):
        
        profitOrLossDataFrame = []

        for isin in self.__getActiveIsins(date):
            pass

        pass

    def __getActiveIsins(self, date: date="CURRENT_DATE") -> list[str]:
        """This function returns the isins of all active bond positions at the given date"""

        if date != "CURRENT_DATE":
            date = f"'{date}'"

        getAllActiveIsinsSqlStatement = f"""WITH BuySum AS (
                                            SELECT isin, SUM(amountofbonds) AS BuySum
                                            FROM transaction
                                            WHERE LOWER(typeoftransaction) LIKE 'buy'
                                            AND transactiondate <= {date}
                                            GROUP BY isin
                                        ),

                                            SellSum AS (
                                                SELECT isin, SUM(amountofbonds) AS SaleSum
                                                FROM transaction
                                                WHERE LOWER(typeoftransaction) LIKE 'sell'
                                                AND transactiondate <= {date}
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
        
        # Berechne die zu diesem Zeitunkt valide Anzahl an Wertpapieren, die sich im Besitz befunden haben
        # Daraus ergibt sich die totalSumOfPurchase und die valueOfPosition

        totalSumOfPurchases = 0

        for purchase in self.__getAllPurchases(date, isin):
            totalSumOfPurchases += purchase.amount * purchase.price

        valueOfPosition = self.priceService.getPriceByIsin(isin)
        pass

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

        totalProfit = 0

        for purchase in allPurchasesList:
            totalProfit += min(saleToCalculate.amount, purchase.amount) * (saleToCalculate.price - purchase.price)
            saleToCalculateAmountCopy = saleToCalculate.amount
            saleToCalculate.amount = max(saleToCalculate.amount - purchase.amount, 0)
            purchase.amount = max(purchase.amount - saleToCalculateAmountCopy, 0)
            if(saleToCalculate.amount == 0):
                break

        return totalProfit

    def __getAllSalesList(self, transactionDate, isin):
        getAllSalesSqlStatement = f"Select * from transaction where isin LIKE '{isin}' AND typeoftransaction LIKE 'sell' AND transactiondate < '{transactionDate}'"

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

import PriceData.PriceDataInvestiny

priceService = PriceData.PriceDataInvestiny.PriceDataInvestiny(connection)

bondIndicators = BondIndicators(connection, priceService)

bondIndicators.getProfitOrLossForAPosition("US0846707026")