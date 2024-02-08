import argparse
import yfinance as yf
import pandas_ta as ta
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import numpy as np


class MACDStrategy:
    def __init__(self, ticker, period):
        self.ticker = ticker
        self.period = period

    def get_stock_history(self):
        ticker_data = yf.download(self.ticker, period=self.period)
        print("Sample few rows\n", ticker_data.head())
        return ticker_data

    def preprocess_data(self, stock_data):
        return stock_data

    def exec_macd(self, stock_data):
        stock_data.ta.macd(close="Close", fast=12, slow=26, signal=9, append=True)
        stock_data.columns = [x.lower() for x in stock_data.columns]
        return stock_data

    def define_signals(self, stock_data):
        stock_data["signal"] = 0
        stock_data.loc[
            stock_data["macd_12_26_9"] > stock_data["macds_12_26_9"], "signal"
        ] = 1  # Bull
        stock_data.loc[
            stock_data["macd_12_26_9"] < stock_data["macds_12_26_9"], "signal"
        ] = -1  # Bear
        return stock_data

    def backtest_strategy(self, stock_data):
        signals = self.define_signals(stock_data)
        portfolio_value = 1000
        buy_price = 0
        sell_price = 0
        position = 0

        for index, row in signals.iterrows():
            if row["signal"] == 1:
                if position == 0:
                    position = portfolio_value / row["open"]
                    buy_price = row["open"]
                    portfolio_value -= position * buy_price
            elif row["signal"] == -1:
                if position > 0:
                    sell_price = row["open"]
                    portfolio_value += position * sell_price
                    position = 0

        final_portfolio_value = (
            portfolio_value + position * stock_data.iloc[-1]["close"]
        )
        return final_portfolio_value

    def plot_macd(self, stock_data):
        fig = make_subplots(rows=2, cols=1)
        # price lines
        fig.append_trace(
            go.Scatter(
                x=stock_data.index,
                y=stock_data["open"],
                line=dict(color="#ff9900", width=1),
                name="open",
                legendgroup=1,
            ),
            row=1,
            col=1,
        )
        fig.append_trace(
            go.Candlestick(
                x=stock_data.index,
                open=stock_data["open"],
                high=stock_data["high"],
                low=stock_data["low"],
                close=stock_data["close"],
                increasing_line_color="#ff9900",
                decreasing_line_color="black",
                showlegend=False,
            ),
            row=1,
            col=1,
        )

        fig.append_trace(
            go.Scatter(
                x=stock_data.index,
                y=stock_data["macd_12_26_9"],
                line=dict(color="#ff9900", width=2),
                name="macd",
                legendgroup="2",
            ),
            row=2,
            col=1,
        )

        fig.append_trace(
            go.Scatter(
                x=stock_data.index,
                y=stock_data["macds_12_26_9"],
                line=dict(color="#000000", width=2),
                legendgroup=2,
                name="signal",
            ),
            row=2,
            col=1,
        )
        # histogram colors
        colors = np.where(stock_data["macdh_12_26_9"] < 0, "#000", "#ff9900")
        fig.append_trace(
            go.Bar(
                x=stock_data.index,
                y=stock_data["macdh_12_26_9"],
                name="histogram",
                marker_color=colors,
            ),
            row=2,
            col=1,
        )

        fig.show()

    def run_strategy(self):
        stock_data = self.get_stock_history()
        stock_data_w_signals = self.define_signals(self.exec_macd(stock_data))
        portfolio_value = self.backtest_strategy(stock_data_w_signals)
        print(portfolio_value)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""
        Moving Average Convergence Divergence is a trend-following 
        momentum that indicates the relationship between two exponential moving averages.
        MACD = 12-Period EMA - 26-Period EMA
        """
    )
    parser.add_argument("--stock", "-s", required=True, type=str, help="Stock to trade")
    parser.add_argument(
        "--period", "-p", required=True, type=str, help="Period to retrieve stock data"
    )
    args = parser.parse_args()
    strategy = MACDStrategy(args.stock, args.period)
    strategy.run_strategy()
