"""
Yahoo Finance API Service using yfinance
FastAPI application to provide stock data for n8n workflows
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import yfinance as yf
from datetime import datetime
import logging
import uvicorn
from curl_cffi import requests as cffi_requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create curl_cffi session for yfinance to avoid blocking
cffi_session = cffi_requests.Session(impersonate="chrome")

# Create FastAPI app
app = FastAPI(
    title="Yahoo Finance API",
    description="API wrapper around yfinance for n8n workflows",
    version="1.0.0"
)


# Pydantic models
class FundamentalData(BaseModel):
    ticker: str
    name: str
    date: str
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    ps_ratio: Optional[float] = None
    peg_ratio: Optional[float] = None
    roe: Optional[float] = None
    roa: Optional[float] = None
    profit_margin: Optional[float] = None
    dividend_yield: Optional[float] = None
    dividend_per_share: Optional[float] = None
    payout_ratio: Optional[float] = None
    revenue_growth: Optional[float] = None
    earnings_growth: Optional[float] = None
    debt_to_equity: Optional[float] = None
    current_ratio: Optional[float] = None
    beta: Optional[float] = None
    analyst_rating: Optional[str] = None
    success: bool = True


class HistoricalDataPoint(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    adjusted_close: float


class HistoricalResponse(BaseModel):
    ticker: str
    period: str
    interval: str
    data: List[HistoricalDataPoint]
    success: bool = True


class QuoteData(BaseModel):
    ticker: str
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    adjusted_close: float
    success: bool = True


class ErrorResponse(BaseModel):
    ticker: str
    success: bool = False
    error: str


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint"""
    return {
        "name": "Yahoo Finance API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health", tags=["Health"])
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/fundamentals/{ticker}", response_model=FundamentalData, tags=["Fundamentals"])
async def get_fundamentals(ticker: str):
    """
    Get fundamental data for a stock ticker

    Args:
        ticker: Stock ticker symbol (e.g., 'MC.PA' for LVMH)

    Returns:
        Fundamental data including P/E, P/B, ROE, dividends, etc.
    """
    try:
        logger.info(f"Fetching fundamentals for {ticker}")

        # Create ticker object with curl_cffi session
        stock = yf.Ticker(ticker, session=cffi_session)

        # Get info
        info = stock.info

        # Extract fundamental data
        fundamentals = {
            'ticker': ticker,
            'name': info.get('longName', ''),
            'date': datetime.now().strftime('%Y-%m-%d'),

            # Valuation ratios
            'pe_ratio': info.get('trailingPE'),
            'pb_ratio': info.get('priceToBook'),
            'ps_ratio': info.get('priceToSalesTrailing12Months'),
            'peg_ratio': info.get('pegRatio'),

            # Profitability
            'roe': info.get('returnOnEquity'),
            'roa': info.get('returnOnAssets'),
            'profit_margin': info.get('profitMargins'),

            # Dividends
            'dividend_yield': info.get('dividendYield'),
            'dividend_per_share': info.get('dividendRate'),
            'payout_ratio': info.get('payoutRatio'),

            # Growth
            'revenue_growth': info.get('revenueGrowth'),
            'earnings_growth': info.get('earningsGrowth'),

            # Debt
            'debt_to_equity': info.get('debtToEquity'),
            'current_ratio': info.get('currentRatio'),

            # Other
            'beta': info.get('beta'),
            'analyst_rating': info.get('recommendationKey'),

            'success': True
        }

        # Convert percentages (ROE, ROA, etc.) from decimal to percentage
        percentage_fields = ['roe', 'roa', 'profit_margin', 'dividend_yield',
                           'revenue_growth', 'earnings_growth']
        for field in percentage_fields:
            if fundamentals.get(field) is not None:
                fundamentals[field] = round(fundamentals[field] * 100, 2)

        logger.info(f"Successfully fetched fundamentals for {ticker}")
        return fundamentals

    except Exception as e:
        logger.error(f"Error fetching fundamentals for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail={
            'ticker': ticker,
            'success': False,
            'error': str(e)
        })


@app.get("/api/historical/{ticker}", response_model=HistoricalResponse, tags=["Historical"])
async def get_historical(
    ticker: str,
    period: str = Query(default='1y', description='Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)'),
    interval: str = Query(default='1d', description='Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)')
):
    """
    Get historical price data for a stock ticker

    Args:
        ticker: Stock ticker symbol
        period: Data period (default: 1y)
        interval: Data interval (default: 1d)

    Returns:
        Historical OHLCV data
    """
    try:
        logger.info(f"Fetching historical data for {ticker} (period={period}, interval={interval})")

        # Create ticker object with curl_cffi session
        stock = yf.Ticker(ticker, session=cffi_session)

        # Get historical data
        hist = stock.history(period=period, interval=interval)

        # Convert to list of dictionaries
        data = []
        for index, row in hist.iterrows():
            data.append({
                'date': index.strftime('%Y-%m-%d'),
                'open': round(row['Open'], 4),
                'high': round(row['High'], 4),
                'low': round(row['Low'], 4),
                'close': round(row['Close'], 4),
                'volume': int(row['Volume']),
                'adjusted_close': round(row['Close'], 4)  # yfinance already adjusts by default
            })

        logger.info(f"Successfully fetched {len(data)} historical data points for {ticker}")

        return {
            'ticker': ticker,
            'period': period,
            'interval': interval,
            'data': data,
            'success': True
        }

    except Exception as e:
        logger.error(f"Error fetching historical data for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail={
            'ticker': ticker,
            'success': False,
            'error': str(e)
        })


@app.get("/api/quote/{ticker}", response_model=QuoteData, tags=["Quote"])
async def get_quote(ticker: str):
    """
    Get current quote data for a stock ticker

    Args:
        ticker: Stock ticker symbol

    Returns:
        Current quote data (OHLCV for latest trading day)
    """
    try:
        logger.info(f"Fetching quote for {ticker}")

        # Create ticker object with curl_cffi session
        stock = yf.Ticker(ticker, session=cffi_session)

        # Get latest data
        hist = stock.history(period='1d')

        if hist.empty:
            raise ValueError(f"No data available for {ticker}")

        latest = hist.iloc[-1]

        quote = {
            'ticker': ticker,
            'date': hist.index[-1].strftime('%Y-%m-%d'),
            'open': round(latest['Open'], 4),
            'high': round(latest['High'], 4),
            'low': round(latest['Low'], 4),
            'close': round(latest['Close'], 4),
            'volume': int(latest['Volume']),
            'adjusted_close': round(latest['Close'], 4),
            'success': True
        }

        logger.info(f"Successfully fetched quote for {ticker}")
        return quote

    except Exception as e:
        logger.error(f"Error fetching quote for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail={
            'ticker': ticker,
            'success': False,
            'error': str(e)
        })


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5099,
        reload=True,
        log_level="info"
    )
