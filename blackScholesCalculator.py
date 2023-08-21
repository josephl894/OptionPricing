import math
from scipy.stats import norm
from datetime import datetime, date
from pandas import DataFrame


"""
Test Inputs
S = 100       # stock price
K = 105       # Strike price
T = 1         # Time to expiration in years
r = 0.05      # Risk-free interest rate (annualized)
sigma = 0.2   # Volatility of the stock (annualized)
"""


def black_scholes(S, K, T, r, sigma):
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    
    callPrice = S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    putPrice = K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

    return (callPrice,putPrice)

# stock price
while True:
    S = input("What is the current stock price? ")
    try:
        S = float(S)
        break
    except:
        print("input a number.")

# strike price
while True:
    K = input("What is the strike price? ")
    try:
        K = float(K)
        break
    except:
        print("input a number. ")


# expiration date
while True:
    expiration_date = input("What is the expiration date? (mm-dd-yyyy) ")
    try:
        expiration_date = datetime.strptime(expiration_date, "%m-%d-%Y")
    except ValueError as e:
        print("error: %s\nTry again." % (e,))
    else:
        break
T = (expiration_date - datetime.utcnow()).days / 365


# risk-free interest rate
while True:
    r = input("What is the risk-free interest rate(%)? ")
    try:
        r = float(r) / 100
        break
    except:
        print("input a number.")
        

# volatility
while True:
    sigma = input("What is the volatility(%)? "); 
    try:
        sigma = float(sigma) / 100
        break
    except:
        print("input a number.")

price = black_scholes(S, K, T, r, sigma)
print("Call option premium: ", price[0], '\n')
print("Put option premium: ", price[1])
