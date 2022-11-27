from datetime import date
import datetime
from timeit import Timer
import yfinance as yf


class PriceDataYahoo:
    def __init__(self, isinConverter):
        self.__isinConverter = isinConverter

    def getPriceByIsin(self, isin: str):
        ticker = self.__isinConverter.getTickerForISIN(isin)

        if ticker == "n/a":
            print("ticker cannot be found")
            return self.getPriceByIsinTryAllTicker(isin)

        yfTicker = yf.Ticker(ticker)
        try:
            yfTicker.info.get("regularMarketPrice")
        except:
            return self.getPriceByIsinTryAllTicker(isin)
        return (
            yfTicker.info["regularMarketPrice"]
            if yfTicker.info.get("regularMarketPrice") is not None
            else yfTicker.history(period="1d", interval="1d")["Open"]
            if len(yfTicker.history(period="1d", interval="1d")["Open"]) > 0
            else self.getPriceByIsinTryAllTicker(isin)
        )

    def getPriceByIsinTryAllTicker(self, isin: str):
        tickers = self.__isinConverter.getAllTickerForISIN(isin)
        import time

        for ticker in tickers:
            time.sleep(1)
            yfTicker = yf.Ticker(ticker)
            priceByHistory = (
                yfTicker.history(period="1d", interval="1d")["Open"][0]
                if len(yfTicker.history(period="1d", interval="1d")["Open"]) > 0
                else None
            )
            try:
                regularMarketPrice = yfTicker.info["regularMarketPrice"]
            except:
                regularMarketPrice = None
            if priceByHistory is not None:
                return priceByHistory
            if regularMarketPrice is not None:
                return regularMarketPrice
        return -1

    def getPriceHistory(self, isin: str, fromDate: datetime, toDate: datetime):
        ticker = self.__isinConverter.getTickerForISIN(isin)
        yfTicker = yf.Ticker(ticker)
        history = yfTicker.history(start=fromDate, end=toDate)
        downloadedHistory = yf.download(ticker, start=fromDate, end=toDate)
        historyWithDateString = yfTicker.history(start="2017-01-01", end="2017-04-30")
        print(history)
        print(downloadedHistory)
        return history
