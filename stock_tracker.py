from pandas import DataFrame
import pandas as pd
import yfinance as yf
import argparse
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima.model import ARIMA
import pmdarima as pm
from typing import Tuple


class StockTracker:
    def __init__(self, ticker: str, period: str) -> None:
        self.ticker = ticker
        self.period = period

    def get_stock_history(self) -> DataFrame:
        ticker_data = yf.download(self.ticker, period=self.period)
        """
        re-sampling a timeseries to a weekly frequency this is benefitial for noise reduction
        """
        print("Sample Few Rows\n", ticker_data.head())
        return ticker_data

    def get_model_data(self, stock_data) -> Tuple:
        """
        Resampling the data to obtain weekly prices
        Open : Get first opening price of the week
        High: Max price of the week
        Low: Min price of the week
        Close: Last price of the week
        Adj Close: Last adjusted close price of the week
        """
        # TODO try resample the data to monthly timeframe to check predictability

        stock_data = stock_data.resample("W").agg(
            {
                "Open": "first",
                "High": "max",
                "Low": "min",
                "Close": "last",
                "Adj Close": "last",
            }
        )
        training_size = int(len(stock_data) * 0.8)
        self.training_data = stock_data[:training_size]
        self.testing_data = stock_data[training_size:]

        return self.training_data, self.testing_data

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

    def fit_model(self, training_data):
        arima_fit = pm.auto_arima(
            training_data["Close"],
            error_action="ignore",
            suppress_warnings=True,
            stepwise=False,
            approximation=False,
            seasonal=False,
        )
        # print(arima_fit.summary())
        return arima_fit

    def forecast_testing_data(self, testing_data: DataFrame):
        testing_data.drop(columns=["Open", "High", "Low", "Adj Close"], inplace=True)
        n_fcast = len(testing_data)
        arima_fit = self.fit_model(self.training_data)
        arima_fcast = arima_fit.predict(
            n_periods=n_fcast, return_conf_int=True, alpha=0.05
        )
        # arima_fcast = [
        #     pd.DataFrame(arima_fcast[0], columns=["prediction"]),
        #     pd.DataFrame(arima_fcast[1], columns=["lower_95", "upper_95"]),
        # ]

        arima_fcast = pd.DataFrame(arima_fcast[0], columns=["prediction"])
        arima_fcast.set_index(testing_data.index)

        plt.figure(figsize=(12, 8))
        plt.plot(testing_data["Close"], label="Actual Closing Prices")
        plt.plot(arima_fcast["prediction"], label="ARIMA Forecast", color="red")
        plt.title(f"{self.ticker} actual stock price  vs  predicted price")
        plt.xlabel("Date")
        plt.ylabel("Price (USD)")
        plt.legend()
        plt.show()

        return

        # p, d, q = 1, 1, 1
        # fit ARIMA model with tuning to maximize AIC score
        # model = ARIMA(stock_data["Close"], order=(p, d, q))
        # results = model.fit()
        #
        # forecast_steps = 10
        # forecast = results.get_forecast(steps=forecast_steps)
        # print(forecast.predicted_mean)
        #
        # plt.figure(figsize=(12, 6))
        # plt.plot(stock_data["Close"], label="Historical Data")
        # # plt.plot(forecast.predicted_mean, color="red", label="Forecast")
        # plt.title(f"ARIMA ({p}, {d}, {q}) Forecast for {self.ticker}")
        # plt.xlabel("Date")
        # plt.ylabel("Closing Price")
        # plt.legend()
        # plt.show()


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
    training_data, testing_data = tracker.get_model_data(stock_data)
    tracker.forecast_testing_data(testing_data)
    exit()
