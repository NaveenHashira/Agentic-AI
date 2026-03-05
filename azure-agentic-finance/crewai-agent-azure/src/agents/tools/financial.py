""""
Financial data extraction module.

This module provides Crewai tools for extracting financial data from Yahoo Finance using the yfinance API.

"""

from pydantic import BaseModel, Field
from typing import Type, Any, Dict, Optional
from crewai.tools import BaseTool
import yfinance as yf


## Input schema

class StockAnalysisInput(BaseModel):
    """
    Input schema for the FundamentalAnalysisTool.
    """
    ticker: str = Field(
        ..., 
        description="The stock ticker symbol (e.g., 'AAPL', 'NVDA', 'MSFT')."
        )

class CompareStocksInput(BaseModel):
    """
    Input schema for the CompareStocksTool.
    """
    ticker1: str = Field(
        ..., 
        description="The first stock ticker symbol (e.g., 'AAPL', 'NVDA', 'MSFT')."
        )
    ticker2: str = Field(
        ..., 
        description="The second stock ticker symbol to compare against (e.g., 'AAPL', 'NVDA', 'MSFT')."
        )
    
## Tools definition

class FundamentalAnalysisTool(BaseTool):
    """"
    A Crewai tool for extracting key financials metrics for a given stock

    This tool acts as a screening analyst providing raw data needed 
    to determine whether a stock is overvalued, undervalued, or volatile
    """

    name: str = "Fetch fundamental Metrics"
    description: str = (
        "Fetches key financial metrics for a specific stock ticker." \
        "Useful for qunatitative analysis, Returns JSON-formatted data including" \
        "P/E ratio, Beta, EPS, Market Cap, and 52-week high/low."
    )
    args_schema: Type[BaseModel] = StockAnalysisInput

    def _run(self, ticker: str) -> str:
        """
        Executes the data fetch from Yahoo Finance

        Args:
            ticker (str): The stock ticker symbol to analyze.
        
        Returns:
            str: A stringified JSON-dictionary contained selected metrics,
                or an error message string if the fetch fails.
        """
        try:
            # Initialize the ticker object
            stock = yf.Ticker(ticker)
            info: Dict[str, Any] = stock.info

            # Extract relevant financial metrics
            metrics = {
                "Ticker": ticker.upper(),
                "Current Price": info.get("currentPrice", "N/A"),
                "Market Cap": info.get("marketCap", "N/A"),
                "P/E Ratio (Trailing)": info.get("trailingPE", "N/A"),
                "Forward P/E": info.get("forwardPE", "N/A"),
                "PEG Ratio": info.get("pegRatio", "N/A"),
                "Beta (Volatility)": info.get("beta", "N/A"),
                "EPS (Trailing)": info.get("trailingEps", "N/A"),
                "52 Week High": info.get("fiftyTwoWeekHigh", "N/A"),
                "52 Week Low": info.get("fiftyTwoWeekLow", "N/A"),
                "Analyst Recommendation": info.get("recommendationKey", "none")
            }
            return str(metrics)
        except Exception as e:
            return f"Error fetching data for '{ticker}': {str(e)}"

class CompareStocksTool(BaseTool):
    """
    A Crewai tool for comparing key financial metrics between two stocks.

    This tool provides a side-by-side comparison of selected financial metrics
    for two stock tickers, helping users identify differences in valuation,
    volatility, and growth potential.
    """

    name: str = "Compare two stocks"
    description: str = (
        "Compares key financial metrics between two stock tickers."
    )
    args_schema: Type[BaseModel] = CompareStocksInput

    def _run(self, ticker_a: str, ticker_b: str) -> str:
        """
        Fetches historical data and calculates percentage return.

        Formula: ((Last Price - First Price) / First Price) * 100

        Args:
            ticker_a (str): First stock symbol.
            ticker_b (str): Second stock symbol.

        Returns:
            str: A formatted summary of the 1-year performance comparison.
        """
        try:
            # Download only the 'Close' column for the last 1 year
            tickers = f"{ticker_a} {ticker_b}"
            data = yf.download(tickers, period="1y", progress=False)['Close']
            
            # Helper function to calculate return
            def calculate_return(symbol: str) -> float:
                start_price = data[symbol].iloc[0]
                end_price = data[symbol].iloc[-1]
                return ((end_price - start_price) / start_price) * 100

            perf_a = calculate_return(ticker_a)
            perf_b = calculate_return(ticker_b)

            return (
                f"Performance Comparison (Last 1 Year):\n"
                f"- {ticker_a.upper()}: {perf_a:.2f}%\n"
                f"- {ticker_b.upper()}: {perf_b:.2f}%"
            )

        except Exception as e:
            return f"Error comparing stocks '{ticker_a}' and '{ticker_b}': {str(e)}"