import pandas as pd
import yfinance as yf
from mangum import Mangum
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins, or specify a list of origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

handler = Mangum(app)



@app.get("/")
async def main():
    return {"status":"success","data":"hello"}



# Function to fetch and format candlestick data for lightweight chart
async def get_candlestick_data(symbol: str, timeframe: str = "1m", duration: str = "1d"):
    """
    Fetch historical candlestick data for a given stock symbol from Yahoo Finance.
    
    Args:
        symbol (str): Stock ticker symbol (e.g., "MSFT").
        timeframe (str): Interval for candlestick data (e.g., "1m", "5m").
        duration (str): Duration of the data (e.g., "1d", "5d").
        
    Returns:
        List[dict]: List of candlestick data formatted for lightweight chart.
    """
    # Fetch historical data from Yahoo Finance
    stock = yf.Ticker(symbol)
    df = stock.history(period=duration, interval=timeframe)
    
    # Reset index to access date as a column
    df = df.reset_index()

    # Check column names to ensure compatibility
    print(df.columns)

    # Rename columns to lowercase for consistency
    df.columns = df.columns.str.lower()

    # Create the final format for Lightweight Charts
    chart_data = df[['datetime', 'open', 'high', 'low', 'close']].copy()
    chart_data.rename(columns={'datetime': 'time'}, inplace=True)
    chart_data['time'] = chart_data['time'].apply(lambda x: int(x.timestamp()))  # Convert to timestamp
    
    # Return the data as a list of dictionaries
    return chart_data.to_dict(orient='records')

@app.get("/api/stocks/{symbol}/candlesticks/")
async def get_historical_candlesticks(symbol: str, timeframe: str = "1m", duration: str = "1d"):
    # Get the formatted candlestick data
    data = await get_candlestick_data(symbol, timeframe, duration)
    return {"status":"success","data":data}
