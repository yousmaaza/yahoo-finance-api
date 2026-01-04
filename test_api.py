"""
Test script for Yahoo Finance API
Run this after starting the API to verify it's working correctly
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:5099"


def test_health():
    """Test health endpoint"""
    print("\n🏥 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_fundamentals(ticker: str = "MC.PA"):
    """Test fundamentals endpoint"""
    print(f"\n📊 Testing fundamentals for {ticker}...")
    response = requests.get(f"{BASE_URL}/api/fundamentals/{ticker}")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success! Got data for {data.get('name', 'Unknown')}")
        print(f"   P/E Ratio: {data.get('pe_ratio')}")
        print(f"   ROE: {data.get('roe')}%")
        print(f"   Dividend Yield: {data.get('dividend_yield')}%")
    else:
        print(f"❌ Error: {response.text}")

    return response.status_code == 200


def test_historical(ticker: str = "MC.PA", period: str = "5d"):
    """Test historical endpoint"""
    print(f"\n📈 Testing historical data for {ticker} (period={period})...")
    response = requests.get(f"{BASE_URL}/api/historical/{ticker}?period={period}&interval=1d")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success! Got {len(data.get('data', []))} data points")
        if data.get('data'):
            latest = data['data'][-1]
            print(f"   Latest close: {latest.get('close')} on {latest.get('date')}")
    else:
        print(f"❌ Error: {response.text}")

    return response.status_code == 200


def test_quote(ticker: str = "MC.PA"):
    """Test quote endpoint"""
    print(f"\n💰 Testing quote for {ticker}...")
    response = requests.get(f"{BASE_URL}/api/quote/{ticker}")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success! Quote for {data.get('date')}")
        print(f"   Open: {data.get('open')}")
        print(f"   High: {data.get('high')}")
        print(f"   Low: {data.get('low')}")
        print(f"   Close: {data.get('close')}")
        print(f"   Volume: {data.get('volume'):,}")
    else:
        print(f"❌ Error: {response.text}")

    return response.status_code == 200


def main():
    """Run all tests"""
    print("=" * 60)
    print("Yahoo Finance API - Test Suite")
    print("=" * 60)

    # Test tickers
    tickers = ["MC.PA", "AIR.PA", "OR.PA"]

    results = {
        "health": False,
        "fundamentals": [],
        "historical": [],
        "quote": []
    }

    # Test health
    try:
        results["health"] = test_health()
    except Exception as e:
        print(f"❌ Health check failed: {e}")

    # Test each ticker
    for ticker in tickers:
        try:
            results["fundamentals"].append(test_fundamentals(ticker))
            results["historical"].append(test_historical(ticker))
            results["quote"].append(test_quote(ticker))
        except Exception as e:
            print(f"❌ Tests failed for {ticker}: {e}")

    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Summary")
    print("=" * 60)
    print(f"Health: {'✅ PASS' if results['health'] else '❌ FAIL'}")
    print(f"Fundamentals: {sum(results['fundamentals'])}/{len(results['fundamentals'])} passed")
    print(f"Historical: {sum(results['historical'])}/{len(results['historical'])} passed")
    print(f"Quote: {sum(results['quote'])}/{len(results['quote'])} passed")

    total_tests = 1 + len(results['fundamentals']) + len(results['historical']) + len(results['quote'])
    passed_tests = (1 if results['health'] else 0) + sum(results['fundamentals']) + sum(results['historical']) + sum(results['quote'])

    print(f"\n🎯 Total: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        print("✅ All tests passed! API is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    main()