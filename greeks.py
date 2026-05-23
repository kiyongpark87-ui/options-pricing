import numpy as np
from scipy.stats import norm
from black_scholes import black_scholes

def greeks(S, K, T, r, sigma, option_type='call'):
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    delta = norm.cdf(d1) if option_type == 'call' else -norm.cdf(-d1)
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    theta_raw = (- (S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))
                 - r * K * np.exp(-r * T) * (norm.cdf(d2) if option_type == 'call' else -norm.cdf(-d2)))
    theta = theta_raw / 365
    vega = S * norm.pdf(d1) * np.sqrt(T) / 100
    rho_raw = K * T * np.exp(-r * T) * (norm.cdf(d2) if option_type == 'call' else -norm.cdf(-d2))
    rho = rho_raw / 100

    return {
        'delta': round(delta, 4),
        'gamma': round(gamma, 4),
        'theta': round(theta, 4),
        'vega':  round(vega, 4),
        'rho':   round(rho, 4)
    }

if __name__ == '__main__':
    S, K, T, r, sigma = 100, 110, 1.0, 0.05, 0.20
    for opt in ['call', 'put']:
        print(f"\n{opt.upper()} Greeks:")
        g = greeks(S, K, T, r, sigma, opt)
        for name, val in g.items():
            print(f"  {name}: {val}")