# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI-based wrapper around the `yfinance` library that provides a REST API for accessing Yahoo Finance data. The service is designed for integration with n8n workflows and provides three main endpoints:
- Fundamental data (P/E, P/B, ROE, dividends, etc.)
- Historical price data (OHLCV)
- Current quote data

The API automatically handles Yahoo Finance's authentication via yfinance, which manages crumb/cookie mechanisms transparently.

## Common Commands

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API server (port 5099)
python main.py

# Or run with uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 5099

# Run tests
python test_api.py
```

### Docker Deployment

```bash
# Build and start service
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop service
docker-compose down
```

### Testing Individual Endpoints

```bash
# Health check
curl http://localhost:5099/health

# Get fundamentals for a ticker
curl http://localhost:5099/api/fundamentals/MC.PA

# Get historical data
curl "http://localhost:5099/api/historical/MC.PA?period=1y&interval=1d"

# Get current quote
curl http://localhost:5099/api/quote/MC.PA
```

## Architecture

### Single-File Application (main.py)

The entire API is contained in `main.py` with the following structure:

1. **Pydantic Models** (lines 31-88): Define response schemas
   - `FundamentalData`: All fundamental metrics for a ticker
   - `HistoricalDataPoint` + `HistoricalResponse`: Historical OHLCV data
   - `QuoteData`: Current quote information
   - `ErrorResponse`: Error handling

2. **API Endpoints**:
   - `/health` (line 101): Health check
   - `/api/fundamentals/{ticker}` (line 110): Fetches fundamental data from `yf.Ticker().info`
   - `/api/historical/{ticker}` (line 186): Fetches historical data using `yf.Ticker().history()`
   - `/api/quote/{ticker}` (line 244): Fetches latest quote (uses history with period='1d')

3. **Data Transformation**:
   - Percentage fields (ROE, ROA, profit_margin, etc.) are converted from decimal to percentage (0.15 → 15.0) at lines 168-172
   - Prices are rounded to 4 decimal places
   - Volumes are converted to integers

### Test Suite (test_api.py)

- Tests all endpoints against multiple tickers (MC.PA, AIR.PA, OR.PA)
- Connects to `http://localhost:5099` by default
- Run after starting the API to verify functionality

### Port Configuration

- API runs on port **5099** (configured in both main.py:297 and docker-compose.yml:8)
- Note: The README.md mentions port 5000 but the actual implementation uses 5099

### n8n Integration

When integrating with n8n:
- If n8n is in Docker on the same network: Use `http://yahoo-finance-api:5099`
- If n8n is running locally: Use `http://localhost:5099`
- Set timeouts to at least 30 seconds for API calls

### Error Handling

All endpoints catch exceptions and return HTTPException with status_code=500 containing:
- `ticker`: The requested ticker symbol
- `success`: false
- `error`: Error message string

### yfinance Behavior

- The `yfinance` library handles all Yahoo Finance authentication automatically
- Some tickers may not have all fundamental data available (returns `null` for missing fields)
- Historical data returns adjusted prices by default
- The library may be subject to Yahoo Finance rate limiting