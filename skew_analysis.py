import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from implied_vol import implied_volatility

def get_atm_iv(chain_puts, chain_calls, S, T, r, option_type_put='put', option_type_call='call'):
    """Find the IV of the strike closest to ATM."""
    puts = chain_puts.copy()
    calls = chain_calls.copy()
    puts['mid'] = (puts['bid'] + puts['ask']) / 2
    calls['mid'] = (calls['bid'] + calls['ask']) / 2

    # Closest strike to spot
    all_strikes = pd.concat([puts[['strike', 'mid']], calls[['strike', 'mid']]])
    atm_strike = all_strikes.iloc[(all_strikes['strike'] - S).abs().argsort()[:1]]['strike'].values[0]

    # Try put first, then call
    row = puts[puts['strike'] == atm_strike]
    if len(row) > 0 and row['mid'].values[0] > 0.05:
        iv = implied_volatility(row['mid'].values[0], S, atm_strike, T, r, 'put')
        if iv:
            return iv

    row = calls[calls['strike'] == atm_strike]
    if len(row) > 0 and row['mid'].values[0] > 0.05:
        iv = implied_volatility(row['mid'].values[0], S, atm_strike, T, r, 'call')
        if iv:
            return iv
    return None

def get_delta_approx_strike(S, T, r, sigma, delta_target=0.25, option_type='put'):
    from scipy.stats import norm
    from scipy.optimize import brentq

    def delta_diff(K):
        if K <= 0:
            return -999
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        if option_type == 'put':
            return abs(norm.cdf(-d1)) - delta_target
        else:
            return norm.cdf(d1) - delta_target

    try:
        return brentq(delta_diff, S * 0.7, S * 0.99) if option_type == 'put' else brentq(delta_diff, S * 1.01, S * 1.3)
    except Exception as e:
        print(f"  brentq failed for {option_type}: {e}")
        # Fallback: use fixed moneyness approximation
        if option_type == 'put':
            return S * (1 - sigma * np.sqrt(T) * 0.674)  # 0.674 ≈ N^-1(0.75)
        else:
            return S * (1 + sigma * np.sqrt(T) * 0.674)

def build_skew_table(ticker='SPY', n_expiries=6):
    stock = yf.Ticker(ticker)
    S = stock.history(period='1d')['Close'].iloc[-1]
    r = 0.05
    today = datetime.today()
    expiries = stock.options[:n_expiries]

    results = []
    print(f"{ticker} spot: ${S:.2f}\n")
    print(f"{'Expiry':<12} {'T (days)':<10} {'ATM IV':<10} {'25d Put IV':<12} {'25d Call IV':<13} {'Skew (P-C)':<12}")
    print("-" * 70)

    for expiry in expiries:
        T = (datetime.strptime(expiry, '%Y-%m-%d') - today).days / 365
        if T <= 0:
            continue

        chain = stock.option_chain(expiry)
        puts = chain.puts.copy()
        calls = chain.calls.copy()
        puts['mid'] = (puts['bid'] + puts['ask']) / 2
        calls['mid'] = (calls['bid'] + calls['ask']) / 2

        # ATM IV
        atm_iv = get_atm_iv(puts, calls, S, T, r)
        if not atm_iv:
            continue

        # 25-delta strikes
        put_strike_25d = get_delta_approx_strike(S, T, r, atm_iv, 0.25, 'put')
        call_strike_25d = get_delta_approx_strike(S, T, r, atm_iv, 0.25, 'call')

        def get_iv_near_strike(df, target_strike, opt_type):
            # Looser filter — just require positive bid
            df = df[df['bid'] > 0].copy()
            if len(df) == 0:
                return None
            closest = df.iloc[(df['strike'] - target_strike).abs().argsort()[:1]]
            row = closest.iloc[0]
            if row['mid'] < 0.01:
                return None
            return implied_volatility(row['mid'], S, row['strike'], T, r, opt_type)

        put_iv_25d = get_iv_near_strike(puts, put_strike_25d, 'put') if put_strike_25d else None
        call_iv_25d = get_iv_near_strike(calls, call_strike_25d, 'call') if call_strike_25d else None

        skew = (put_iv_25d - call_iv_25d) if (put_iv_25d and call_iv_25d) else None

        print(f"{expiry:<12} {T*365:<10.0f} {atm_iv*100:<10.2f} "
              f"{put_iv_25d*100 if put_iv_25d else 0:<12.2f} "
              f"{call_iv_25d*100 if call_iv_25d else 0:<13.2f} "
              f"{skew*100 if skew else 0:<12.2f}")

        results.append({
            'expiry': expiry, 'T_days': T * 365,
            'atm_iv': atm_iv, 'put_iv_25d': put_iv_25d,
            'call_iv_25d': call_iv_25d, 'skew': skew
        })

    return pd.DataFrame(results)

def plot_skew_term_structure(df):
    df = df.dropna(subset=['skew'])
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # ATM IV term structure
    axes[0].plot(df['T_days'], df['atm_iv'] * 100, 'b-o', markersize=6)
    axes[0].set_xlabel('Days to Expiry')
    axes[0].set_ylabel('ATM Implied Volatility (%)')
    axes[0].set_title('ATM IV Term Structure')
    axes[0].grid(True, alpha=0.3)

    # 25d Skew term structure
    axes[1].plot(df['T_days'], df['skew'] * 100, 'r-o', markersize=6, label='25d Skew (Put - Call)')
    axes[1].axhline(0, color='black', linewidth=0.8, linestyle='--')
    axes[1].set_xlabel('Days to Expiry')
    axes[1].set_ylabel('Skew (vol points)')
    axes[1].set_title('25-Delta Skew Term Structure')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.suptitle('SPY Volatility Term Structure Analysis', fontsize=13)
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    df = build_skew_table('SPY', n_expiries=6)
    plot_skew_term_structure(df)