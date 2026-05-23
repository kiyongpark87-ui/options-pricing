import numpy as np
from scipy.optimize import brentq
from black_scholes import black_scholes

def implied_volatility(market_price, S, K, T, r, option_type='call'):
    def objective(sigma):
        return black_scholes(S, K, T, r, sigma, option_type) - market_price

    try:
        iv = brentq(objective, 1e-6, 10.0)
        return round(iv, 4)
    except ValueError:
        return None  # No solution found in range

if __name__ == '__main__':
    from black_scholes import black_scholes

    S, K, T, r, sigma = 100, 110, 1.0, 0.05, 0.20

    call_price = black_scholes(S, K, T, r, sigma, 'call')
    put_price  = black_scholes(S, K, T, r, sigma, 'put')

    call_iv = implied_volatility(call_price, S, K, T, r, 'call')
    put_iv  = implied_volatility(put_price,  S, K, T, r, 'put')

    print(f"Call IV: {call_iv:.2%}")
    print(f"Put IV:  {put_iv:.2%}")