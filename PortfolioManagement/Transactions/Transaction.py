class Transaction:
    def __init__(self, isin, wkn, amountOfBonds, transactionDate, typeOfTransaction, transactionComment, price, depot, curreny, exchange):
        self.isin = isin
        self.wkn = wkn
        self.amountOfBonds = amountOfBonds
        self.transactionDate = transactionDate
        self.typeOfTransaction = typeOfTransaction
        self.transactionComment = transactionComment
        self.price = price
        self.depot = depot
        self.curreny = curreny
        self.exchange = exchange