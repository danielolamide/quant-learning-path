import argparse
import yfinance as yf


class MACDStrategy:
    def __init__(self, ticker, period):
        self.ticker = ticker
        self.period = period

    def get_stock_history(self):
        ticker_data = yf.download(self.ticker, period=self.period)
        print("Sample few rows\n", ticker_data.head())
        return ticker_data

    def preprocess_data(self, stock_data):
        stock_data = stock_data.resample("W")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Moving Average Convergence Divergence"
    )
    parser.add_argument("--stock", "-s", required=True, type=str, help="Stock to trade")
    parser.add_argument(
        "--period", "-p", required=True, type=str, help="Period to retrieve stock data"
    )
    args = parser.parse_args()
    strategy = MACDStrategy(args.stock, args.period)
