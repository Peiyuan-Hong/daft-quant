import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf


def plot_backtest_results(history: pd.DataFrame, trades: pd.DataFrame, data: pd.DataFrame = None):
    """Plot backtest results in one call.

    Includes:
    1. Equity curve
    2. Drawdown
    3. Position size (shares)
    4. Per-trade PnL scatter over time (blue = win, red = loss)

    Args:
        history: DataFrame from backtester history (must contain 'total_assets' and 'position').
        trades:  DataFrame of closed trades (must contain at least 'datetime' and 'pnl').
        data:    Optional OHLCV price DataFrame for potential future extensions (currently unused here).
    """
    if history is None or history.empty:
        print("No history to plot.")
        return

    # Setup figure with 4 rows: equity, drawdown, position, per-trade PnL
    fig = plt.figure(figsize=(14, 10))
    gs = fig.add_gridspec(4, 1, height_ratios=[2, 1, 1, 1])

    # 1. Equity Curve
    ax1 = fig.add_subplot(gs[0])
    ax1.plot(history.index, history['total_assets'], label='Equity', color='blue')
    ax1.set_title('Equity Curve')
    ax1.set_ylabel('Value')
    ax1.grid(True)

    # 2. Drawdown
    ax2 = fig.add_subplot(gs[1], sharex=ax1)
    rolling_max = history['total_assets'].cummax()
    drawdown = (history['total_assets'] - rolling_max) / rolling_max * 100.0
    ax2.fill_between(drawdown.index, drawdown, 0, color='red', alpha=0.3, label='Drawdown')
    ax2.set_title('Drawdown')
    ax2.set_ylabel('%')
    ax2.grid(True)

    # 3. Positions
    ax3 = fig.add_subplot(gs[2], sharex=ax1)
    ax3.plot(history.index, history['position'], label='Position (Shares)', color='orange')
    ax3.set_title('Position Size')
    ax3.set_ylabel('Shares')
    ax3.grid(True)

    # 4. Per-trade PnL scatter (one point per closed trade)
    ax4 = fig.add_subplot(gs[3], sharex=ax1)
    if trades is not None and not trades.empty:
        closed_trades = trades.copy()

        # Prefer an explicit datetime column; fall back to index if necessary
        if 'datetime' in closed_trades.columns:
            x = pd.to_datetime(closed_trades['datetime'])
        else:
            x = closed_trades.index

        pnl = closed_trades.get('pnl')

        if pnl is not None:
            colors = np.where(pnl >= 0, 'blue', 'red')
            ax4.scatter(x, pnl, c=colors, s=25, alpha=0.8, edgecolors='none')
            ax4.axhline(0, color='gray', linestyle='--', linewidth=1)

    ax4.set_title('Per-Trade PnL (Closed Trades)')
    ax4.set_ylabel('PnL')
    ax4.set_xlabel('Time')
    ax4.grid(True)

    plt.tight_layout()
    plt.show()


def plot_candles_with_trades(data: pd.DataFrame, trades: pd.DataFrame):
    """Plot candlestick chart with price history.

    Currently this shows only candles. Trade markers can be
    added later once we standardize raw execution logs.
    """
    if data is None or data.empty:
        print("No price data to plot.")
        return

    # Ensure data has the right columns for mplfinance (Open, High, Low, Close, Volume)
    df = data.copy()
    df.index.name = 'Date'

    mpf.plot(df, type='candle', style='charles', volume=True, title='Price History')


def plot_from_results(results: dict, data: pd.DataFrame = None) -> None:
    """Convenience helper: plot everything from backtester results.

    Usage from notebook:

        results = backtester.get_results()
        from backtest.plotting import plot_from_results
        plot_from_results(results, data)
    """
    history = results.get('history')
    trades = results.get('trades')
    plot_backtest_results(history=history, trades=trades, data=data)
