from pandas import DataFrame
import pandas as pd
import yfinance as yf
import argparse
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima.model import ARIMA


class StockTracker:
    def __init__(self, ticker: str, period: str) -> None:
        self.ticker = ticker
        self.period = period

    def get_stock_history(self) -> DataFrame:
        ticker_data = yf.download(self.ticker, period=self.period)
        """
        re-index timeseries to business-daily frequency and include the parameter method=ffill
        as missing timestamps will be added and missing stock data will be set to NaN
        """
        ticker_data = ticker_data.asfreq("B", method="ffill")
        print("Sample Few Rows\n", ticker_data.head())
        print("Data Info:", ticker_data.info())
        # great for dealing with null values in time series
        # ticker_data= ticker_data.ffill()
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

    def test_stationarity(self, stock_data: DataFrame):
        result = adfuller(stock_data["Close"], autolag="AIC")
        print("ADF Statistic", result[0])
        print("p-value", result[1])
        print("Critical Values", result[4])

    def forecast_stock(self, stock_data: DataFrame):
        p, d, q = 1, 1, 1
        # freq = pd.infer_freq(stock_data.index)
        # fit ARIMA model
        model = ARIMA(stock_data["Close"], order=(p, d, q))
        results = model.fit()

        forecast_steps = 100
        forecast = results.get_forecast(steps=forecast_steps)
        print(forecast.predicted_mean)

        plt.figure(figsize=(12, 6))
        plt.plot(stock_data["Close"], label="Historical Data")
        # plt.plot(forecast.predicted_mean, color="red", label="Forecast")
        plt.title(f"ARIMA ({p}, {d}, {q}) Forecast for {self.ticker}")
        plt.xlabel("Date")
        plt.ylabel("Closing Price")
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
    tracker.forecast_stock(stock_data)
    exit()
