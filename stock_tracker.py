from pandas import DataFrame
import pandas as pd
import yfinance as yf
import argparse
import matplotlib.pyplot as plt


class StockTracker:
    def __init__(self, ticker: str, period: str) -> None:
        self.ticker = ticker
        self.period = period

    def get_stock_history(self) -> DataFrame:
        ticker_data = yf.download(self.ticker, period=self.period)
        return ticker_data

    def describe_stock_data(self, stock_data: DataFrame):
        summary = stock_data.describe()
        return summary

    def visualize_historical_prices(self, stock_data: DataFrame):
        plt.figure(figsize=(10, 6))
        plt.plot(stock_data["Close"], label="Closing Price")
        plt.title(f"{self.ticker} Historical Closing Prices")
        plt.xlabel("Date")
        plt.ylabel("Price (USD)")
        plt.legend()
        plt.show()

    def visualize_returns_and_volatility(self, stock_data: DataFrame):
        stock_data["Daily_Return"] = stock_data["Close"].pct_change()
        plt.figure(figsize=(10, 6))
        plt.plot(stock_data["Daily_Return"], label="Daily Returns")
        plt.title(f"{self.ticker} Daily Returns")
        plt.xlabel("Date")
        plt.ylabel("Return")
        plt.legend()
        plt.show()

    def visualize_moving_avg(self, stock_data: DataFrame, period: int):
        ma_column = f"MA_{period}"
        stock_data[ma_column] = stock_data["Close"].rolling(window=period).mean()
        plt.figure(figsize=(10, 6))
        plt.plot(stock_data[ma_column], label=f"{period}-day Moving Average")
        plt.title(f"{self.ticker} Closing Price with {period}-day Moving Average")
        plt.xlabel("Date")
        plt.ylabel("Price(USD)")
        plt.legend()
        plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Track Stock History")
    parser.add_argument(
        "--stock",
        "-s",
        required=True,
        type=str,
        nargs="?",
        help="Stock to track",
    )
    parser.add_argument(
        "--period", "-p", required=True, type=str, nargs="?", help="Period to track"
    )
    args = parser.parse_args()
    tracker = StockTracker(args.stock, args.period)
    stock_data = tracker.get_stock_history()
    tracker.visualize_moving_avg(stock_data, 50)
    exit()
