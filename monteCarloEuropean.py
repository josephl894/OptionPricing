import numpy as np

# Parameters
S0 = 100      # Initial stock price
K = 105       # Strike price
T = 1         # Time to expiration in years
r = 0.05      # Risk-free rate
sigma = 0.2   # Volatility
n = 252       # Number of time steps (e.g., trading days in a year)
m = 10000     # Number of simulated paths
dt = T/n

# Simulate m paths
paths = np.zeros((m, n))
paths[:, 0] = S0

for t in range(1, n):
    rand = np.random.standard_normal(m)  # Random values from standard normal distribution
    paths[:, t] = paths[:, t-1] * np.exp((r - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * rand)

# Calculate payoffs
call_payoffs = np.maximum(paths[:, -1] - K, 0)
put_payoffs = np.maximum(K - paths[:, -1], 0)

# Discount average payoff to get option price
call_price = np.exp(-r * T) * np.mean(call_payoffs)
put_price = np.exp(-r * T) * np.mean(put_payoffs)

print(f"European Call Option Price: {call_price:.2f}")
print(f"European Put Option Price: {put_price:.2f}")