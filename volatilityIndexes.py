import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime,timedelta


def calculate_historical_volatility_index(ticker, duration): #duration in days
    # Fetch historical data
    today = datetime.today()
    initialDate = today - timedelta(days = int(duration))
    data = yf.download(ticker, start=initialDate.strftime("%Y-%m-%d"), end=today.strftime("%Y-%m-%d"))['Adj Close']
    
    # Calculate daily returns
    daily_returns = data.pct_change().dropna()
    
    # Calculate the standard deviation of returns
    daily_volatility = daily_returns.std()
    
    # Annualize volatility
    annualized_volatility = daily_volatility * np.sqrt(duration)
    
    return annualized_volatility

#Might be useful for future applications
"""
def calculate_implied_volatility_index(ticker,duration, option_type): 
    expirations = pd.to_datetime(yf.Ticker(ticker).options)
    target_expiration = pd.Timestamp.now().normalize() + pd.Timedelta(days=duration)

    #using a 2-day buffer to account for weekends and holidays
    options_chain = yf.Ticker(ticker).option_chain((expirations >= (target_expiration - pd.Timedelta(days=3))) and
                                                    (expirations <= (target_expiration + pd.Timedelta(days=3)))) 
    
    calls, puts = options_chain.calls, options_chain.puts
    
    if option_type == 'call':
        eligible_options = calls
    elif option_type == 'put':
        eligible_options = puts

    # For simplicity, the average implied volatility is used
    average_iv = np.mean(eligible_options['impliedVolatility'])

    return average_iv
    """
