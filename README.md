# Options Pricing & Volatility Analysis

A Python implementation of options pricing, Greeks computation, and implied volatility surface analysis using real market data.

## Overview

This project builds an end-to-end options analytics engine from scratch — no options libraries used. Pricing and Greeks are derived directly from the Black-Scholes formula, and implied volatility is recovered numerically using Brent's method. The surface analysis layer pulls live SPY options chain data to analyse the volatility smile, term structure, and 25-delta skew.

## Features

- Black-Scholes pricer for European calls and puts
- Analytical Greeks: Delta, Gamma, Vega, Theta, Rho
- Implied volatility solver via Brent's root-finding method
- Live options chain ingestion via yfinance with liquidity filtering
- Volatility smile visualisation across strikes
- 3D implied volatility surface across strikes and expiries
- ATM IV term structure and 25-delta skew term structure analysis

## Project Structure

| File | Description |
|------|-------------|
| `black_scholes.py` | Black-Scholes pricer for calls and puts |
| `greeks.py` | Analytical Greeks computation |
| `implied_vol.py` | IV solver using Brent's method |
| `payoff.py` | Payoff diagrams at expiry |
| `vol_surface.py` | Vol smile and 3D surface from live data |
| `skew_analysis.py` | ATM IV and 25-delta skew term structure |

## Key Results

**Volatility smile (SPY, June 2026 expiry):** Deep OTM puts trade at 30-50% IV versus 12-14% ATM — reflecting persistent demand for tail hedging and the fat left tail not captured by Black-Scholes.

**25-delta skew term structure:** Put IV exceeds call IV by 2.1 to 3.5 vol points across all expiries, widening with tenor. Short-dated skew is steeper in moneyness terms but carries less total premium than longer-dated contracts.

**ATM IV term structure:** Upward sloping from 12.3% at 2 days to 14.3% at 19 days, consistent with a low-volatility regime with no immediate event risk priced in.

## Limitations

- yfinance data is delayed and bid-ask spreads on deep OTM strikes are wide — illiquid strikes filtered by volume and bid price thresholds
- Black-Scholes assumes constant volatility and log-normal returns; the observed vol smile is direct evidence of these assumptions failing in practice
- American-style early exercise not modelled (SPY options are American)

## Setup

```bash
pip install yfinance numpy scipy matplotlib pandas
python black_scholes.py   # verify pricer
python skew_analysis.py   # run full surface analysis
```

## Skills

Python · NumPy · SciPy · Matplotlib · Options Pricing · Implied Volatility · Quantitative Finance