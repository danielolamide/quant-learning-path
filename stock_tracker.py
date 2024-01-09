import yfinance as yf
import argparse


class StockTracker:
    def __init__(self, ticker: str, period: str) -> None:
        self.ticker = ticker
        self.period = period

    def get_stock_history(self):
        ticker = yf.Ticker(self.ticker)
        history = ticker.history(period=self.period)
        return history


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
    print(tracker.get_stock_history())
