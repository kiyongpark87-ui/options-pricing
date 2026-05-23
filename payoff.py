import numpy as np
import matplotlib.pyplot as plt

def plot_payoff(K, premium, option_type='call'):
    S_range = np.linspace(K * 0.5, K * 1.5, 500)

    if option_type == 'call':
        payoff = np.maximum(S_range - K, 0) - premium
    else:
        payoff = np.maximum(K - S_range, 0) - premium

    plt.figure(figsize=(8, 5))
    plt.plot(S_range, payoff, label=f'{option_type.capitalize()} Payoff', color='steelblue', linewidth=2)
    plt.axhline(0, color='black', linewidth=0.8, linestyle='--')
    plt.axvline(K, color='red', linewidth=0.8, linestyle='--', label=f'Strike = {K}')
    plt.fill_between(S_range, payoff, 0, where=(payoff > 0), alpha=0.2, color='green', label='Profit')
    plt.fill_between(S_range, payoff, 0, where=(payoff < 0), alpha=0.2, color='red', label='Loss')
    plt.title(f'{option_type.capitalize()} Option Payoff at Expiry')
    plt.xlabel('Stock Price at Expiry')
    plt.ylabel('Profit / Loss ($)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    plot_payoff(K=110, premium=4.63, option_type='call')
    plot_payoff(K=110, premium=7.70, option_type='put')