import numpy as np
from scipy.stats import norm


def black_scholes(S, K, T, r, sigma, option_type='call'):
    """
    Price a European option using the Black-Scholes formula.

    Args:
        S: Current stock price
        K: Strike price
        T: Time to expiration in years (e.g. 0.25 = 3 months)
        r: Risk-free interest rate (e.g. 0.05 = 5%)
        sigma: Volatility of the stock (e.g. 0.20 = 20%)
        option_type: 'call' or 'put'

    Returns:
        price: Fair value of the option
    """
    # d1 and d2 are intermediate values in the Black-Scholes formula
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if option_type == 'call':
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:  # put
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

    return price


if __name__ == "__main__":
    # Example: AAPL call option
    S = 150  # Stock price $150
    K = 155  # Strike price $155
    T = 0.25  # 3 months to expiry
    r = 0.05  # 5% risk-free rate
    sigma = 0.20  # 20% volatility

    call_price = black_scholes(S, K, T, r, sigma, 'call')
    put_price = black_scholes(S, K, T, r, sigma, 'put')

    print(f"Call Price: ${call_price:.2f}")
    print(f"Put Price:  ${put_price:.2f}")