import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from datetime import datetime
from implied_vol import implied_volatility

def build_vol_surface(ticker='SPY', n_expiries=6):
    stock = yf.Ticker(ticker)
    S = stock.history(period='1d')['Close'].iloc[-1]
    r = 0.05
    today = datetime.today()

    expiries = stock.options[:n_expiries]
    print(f"{ticker} spot: ${S:.2f}")
    print(f"Building surface across expiries: {list(expiries)}\n")

    records = []

    for expiry in expiries:
        T = (datetime.strptime(expiry, '%Y-%m-%d') - today).days / 365
        if T <= 0:
            continue

        chain = stock.option_chain(expiry)

        # Use puts for OTM (strike < S), calls for OTM (strike > S)
        puts = chain.puts.copy()
        calls = chain.calls.copy()

        puts['mid'] = (puts['bid'] + puts['ask']) / 2
        calls['mid'] = (calls['bid'] + calls['ask']) / 2

        # Filter: liquid and meaningful price
        puts = puts[(puts['bid'] > 0) & (puts['volume'] >= 10) & (puts['mid'] > 0.05)]
        calls = calls[(calls['bid'] > 0) & (calls['volume'] >= 10) & (calls['mid'] > 0.05)]

        # OTM only — puts below spot, calls above spot
        puts = puts[puts['strike'] < S]
        calls = calls[calls['strike'] > S]

        for _, row in puts.iterrows():
            iv = implied_volatility(row['mid'], S, row['strike'], T, r, 'put')
            if iv and 0.01 < iv < 2.0:
                records.append({'expiry': expiry, 'T': T, 'strike': row['strike'],
                                 'moneyness': row['strike'] / S, 'iv': iv, 'type': 'put'})

        for _, row in calls.iterrows():
            iv = implied_volatility(row['mid'], S, row['strike'], T, r, 'call')
            if iv and 0.01 < iv < 2.0:
                records.append({'expiry': expiry, 'T': T, 'strike': row['strike'],
                                 'moneyness': row['strike'] / S, 'iv': iv, 'type': 'call'})

    df = pd.DataFrame(records)
    print(f"Total data points: {len(df)}")
    return df, S

def plot_vol_surface(df):
    fig = plt.figure(figsize=(12, 7))
    ax = fig.add_subplot(111, projection='3d')

    scatter = ax.scatter(df['moneyness'], df['T'], df['iv'] * 100,
                         c=df['iv'] * 100, cmap='RdYlGn_r', s=20)

    ax.set_xlabel('Moneyness (K/S)')
    ax.set_ylabel('Time to Expiry (years)')
    ax.set_zlabel('Implied Volatility (%)')
    ax.set_title('SPY Implied Volatility Surface')
    plt.colorbar(scatter, shrink=0.5, label='IV (%)')
    plt.tight_layout()
    plt.show()

def plot_smile_overlay(df):
    fig, ax = plt.subplots(figsize=(10, 6))
    for expiry, group in df.groupby('expiry'):
        group = group.sort_values('moneyness')
        ax.plot(group['moneyness'], group['iv'] * 100, 'o-', markersize=3, label=expiry)

    ax.axvline(1.0, color='black', linestyle='--', linewidth=0.8, label='ATM')
    ax.set_xlabel('Moneyness (K/S)')
    ax.set_ylabel('Implied Volatility (%)')
    ax.set_title('SPY Vol Smile by Expiry')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    df, S = build_vol_surface('SPY', n_expiries=6)
    plot_vol_surface(df)
    plot_smile_overlay(df)
    print("\nSample data:")
    print(df.head(15).to_string(index=False))