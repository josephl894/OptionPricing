import numpy as np
from scipy.optimize import curve_fit

def polynomial(x, a, b, c):
    return a + b*x + c*x*x
"""
# Parameters
S = 100
K = 105
T = 1
r = 0.05
sigma = 0.2
"""

def generate_path(S,T, r,sigma,n,m):
    dt = T / n
    paths = np.zeros((m, n))
    paths[:, 0] = S

    # Generate price paths
    for t in range(1, n):
        rand = np.random.standard_normal(m)
        paths[:, t] = paths[:, t-1] * np.exp((r - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * rand)

    return paths


def MC_american(S, K, T, r, sigma, n = 252, m = 5000):
    dt = T / n
    paths = generate_path(S,T,r,sigma,n,m)
    
    call_values = np.maximum(paths[:, -1] - K, 0) # intrinsic value at maturity for call
    put_values = np.maximum(K - paths[:, -1], 0)  # intrinsic value at maturity for put

    # call option simulation
    for t in range(n-2, -1, -1):
        # In the money paths for call option
        itm = np.where(paths[:, t] > K)
        
        # Polynomial regression to get continuation values
        x = paths[itm, t].flatten()
        y = call_values[itm] * np.exp(-r * dt)
        try:
            params, _ = curve_fit(polynomial, x, y)
            continuation = polynomial(x, *params)
        except Exception:
            continuation = y 
        
        intrinsic = x - K
        
        # Compare and decide to exercise or not
        call_values[itm] = np.where(intrinsic > continuation, intrinsic, y)

    # put option simulation
    for t in range(n-2, -1, -1):
        # In the money paths
        itm = np.where(paths[:, t] < K)
        
        # Polynomial regression to get continuation values
        x = paths[itm, t].flatten()
        y = put_values[itm] * np.exp(-r * dt)
        try:
            params, _ = curve_fit(polynomial, x, y)
            continuation = polynomial(x, *params)
        except Exception:
            continuation = y 
        
        intrinsic = K - x
        
        # Compare and decide to exercise or not
        put_values[itm] = np.where(intrinsic > continuation, intrinsic, y)

    # Calculate the American put option value
    call_price = np.exp(-r * dt) * np.mean(call_values)
    put_price = np.exp(-r * dt) * np.mean(put_values)
    return (call_price,put_price)