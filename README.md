# Daft Quant

A Quantitative Trading System for Chinese A-Shares

## Project Overview
This project is a comprehensive quantitative trading system designed to handle the entire lifecycle of algorithmic trading, specifically optimized for **Chinese A-shares**. It covers data acquisition, strategy development, and high-fidelity backtesting.

## Modules Status

### ✅ 1. Data Storage and Acquisition
**Implementation:** `src/data/`
- **Source:** Mini-QMT (`xtquant`).
- **Features:** 
  - Automatic incremental downloading.
  - Local CSV caching for offline access.
  - Support for intraday and daily bars.

### ✅ 2. Strategy Module
**Implementation:** `src/strategy/`
- **Design:** Strategies are **independent signal generators** inheriting from `BaseStrategy`.
- **Key Method:** `on_bar(bar)` returns "buy", "sell", or "hold".
- **Implemented Strategies:**
  - Moving Average Crossover (`MACrossoverStrategy`)
  - RSI Strategy (`RSIStrategy`)
  - Dollar Cost Averaging (`DCAStrategy`)
- **Compatibility:** Same strategy code runs in Backtest and Live Trading.

### ✅ 3. Backtest Module
**Implementation:** `src/backtest/`
- **Engine:** Event-driven backtester (`Backtester`).
- **Features:**
  - **A-Share Rules:** Enforced **T+1** trading logic.
  - **Costs:** Configurable commission, stamp duty (sell-side), and slippage.
  - **Batch Processing:** `BacktestRunner` allows testing multiple stocks/ETFs in one go.
  - **Reporting:** `BacktestReport` generates text summaries and charts (equity curve, drawdown, trade markers).

### ✅ 4. Live Trading Interface
**Implementation:** `src/live_trading/`
- **Engine:** `LiveTradeEngine` connects strategy signals to Mini-QMT execution API.
- **Features:**
  - Real-time market data subscription (bar/tick).
  - Async order placement via `OrderManager`.
  - Position and asset monitoring.
  - Structured logging for audit trail.

### ✅ 5. Risk Management
**Implementation:** `src/risk/`
- **Position Sizing:** `PositionSizer` with configurable methods.
  - `all_in`: Use ~99% of available cash.
  - `fixed_fraction`: Allocate a fraction of cash per trade.
  - `fixed_cash`: Allocate a fixed amount per trade.
- **Config:** Minimum cash reserve, lot size (100 shares for A-shares).

## Project Structure
```
daft-quant/
├── src/
│   ├── backtest/       # Backtest engine, runner, reporting, plotting
│   ├── data/           # Data fetching and storage logic
│   ├── live_trading/   # Live trading engine and order management
│   ├── risk/           # Position sizing and risk management
│   └── strategy/       # Strategy logic (MA, RSI, DCA, etc.)
├── storage/
│   └── data/           # Cached market data (CSV)
├── backtest_reports/   # Generated backtest reports (timestamped)
├── run_analysis.py     # Script to run batch backtests
├── main.py             # Data fetching demo
└── README.md
```

## Quick Start

**1. Run a Backtest:**
Use the provided `run_analysis.py` to test a strategy on a list of tickers.
```bash
python run_analysis.py
```
This will:
1. Fetch data for defined tickers (e.g., '000001.SZ').
2. Run the `MACrossoverStrategy`.
3. Display a performance summary table.

**2. Create a New Strategy:**
Inherit from `BaseStrategy` in `src/strategy/` and implement `on_bar`.
```python
from .base_strategy import BaseStrategy

class MyStrategy(BaseStrategy):
    def on_bar(self, bar):
        if bar['close'] > 20:
            return "buy"
        return "hold"
```
