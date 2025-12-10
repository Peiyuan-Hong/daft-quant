import time
import logging
import traceback
from typing import Dict, Any, List, Optional
import pandas as pd
from datetime import datetime
import random

try:
    from xtquant import xtdata, xttrader, xttype, xtconstant
except ImportError:
    print("Warning: xtquant not found.")

from ..strategy.base_strategy import BaseStrategy
from .order_manager import OrderManager
from .logger import setup_logger

class LiveTradeEngine:
    """
    Core engine for live trading using Mini-QMT.
    Manages data subscription, strategy execution, and order placement.
    """

    def __init__(
        self,
        strategy: BaseStrategy,
        account_id: str,
        mini_qmt_path: str,
        symbols: List[str],
        period: str = '1d',
        log_file: str = 'live_trading.log'
    ):
        """
        Initialize Live Trade Engine.
        
        Args:
            strategy: Instance of BaseStrategy
            account_id: QMT Account ID
            mini_qmt_path: Path to userdata_mini directory (needed for session)
            symbols: List of stocks to trade
            period: '1d' or '1m', etc.
        """
        self.logger = setup_logger("LiveEngine", log_file)
        self.strategy = strategy
        self.account_id = account_id
        self.mini_qmt_path = mini_qmt_path
        self.symbols = symbols
        self.period = period
        
        # Components
        self.xt_trader = None
        self.order_manager = None
        self.running = False
        
        # Initialize Strategy
        self.logger.info("Initializing Strategy...")
        self.strategy.on_init()

    def connect(self):
        """
        Connect to Mini-QMT Trader.
        """
        self.logger.info(f"Connecting to Mini-QMT with account {self.account_id}...")
        
        # Generate Session ID
        session_id = int(time.time())
        
        # Create Trader
        self.xt_trader = xttrader.XtQuantTrader(self.mini_qmt_path, session_id)
        
        # Start Trader
        self.xt_trader.start()
        
        # Connect
        connect_result = self.xt_trader.connect()
        if connect_result == 0:
            self.logger.info("Connected to Mini-QMT successfully.")
        else:
            self.logger.error(f"Connection failed with result: {connect_result}")
            return False
            
        # Subscribe to Account
        acc = xttype.StockAccount(self.account_id)
        self.xt_trader.subscribe(acc)
        
        # Initialize Order Manager
        self.order_manager = OrderManager(self.xt_trader, self.account_id, self.logger)
        
        return True

    def start(self):
        """
        Start the trading loop.
        Subscribes to market data and listens for callbacks.
        """
        if not self.xt_trader:
            if not self.connect():
                return

        self.running = True
        self.logger.info("Starting Live Trading Engine...")
        
        # 1. Subscribe to Market Data
        # We use xtdata.subscribe_quote for real-time Tick/Bar updates
        for symbol in self.symbols:
            self.logger.info(f"Subscribing to {symbol} ({self.period})")
            xtdata.subscribe_quote(symbol, period=self.period, count=-1, callback=self._on_market_data)

        # 2. Main Loop (Keep alive)
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """
        Stop the engine.
        """
        self.running = False
        self.logger.info("Stopping Live Trading Engine...")
        self.strategy.on_stop()
        if self.xt_trader:
            self.xt_trader.stop()

    def _on_market_data(self, data: Dict):
        """
        Callback when new market data arrives.
        Format data and pass to strategy.
        
        xtquant data format for bar subscription (e.g., '5m'):
        {
            'stock_code': [
                [timestamp, open, high, low, close, volume, amount, ...],
                ...
            ]
        }
        
        For tick subscription:
        {
            'stock_code': { 'time': ..., 'lastPrice': ..., ... }
        }
        """
        for symbol, tick_data in data.items():
            if symbol not in self.symbols:
                continue
            
            try:
                # Skip invalid data (xtquant sometimes returns 0 or None)
                if tick_data is None or tick_data == 0 or tick_data == []:
                    self.logger.debug(f"Skipping empty/invalid data for {symbol}: {tick_data}")
                    continue
                
                # Handle bar data (list format) - for period subscriptions like '5m', '1d'
                if isinstance(tick_data, list):
                    if len(tick_data) == 0:
                        continue
                    
                    # Get the latest bar (last element)
                    latest_bar = tick_data[-1]
                    
                    # Bar format: [timestamp, open, high, low, close, volume, amount, ...]
                    if len(latest_bar) < 6:
                        self.logger.warning(f"Invalid bar data length for {symbol}: {len(latest_bar)}")
                        continue
                    
                    timestamp = latest_bar[0]
                    bar = {
                        'datetime': datetime.fromtimestamp(timestamp / 1000) if timestamp > 1e10 else datetime.fromtimestamp(timestamp),
                        'open': float(latest_bar[1]),
                        'high': float(latest_bar[2]),
                        'low': float(latest_bar[3]),
                        'close': float(latest_bar[4]),
                        'volume': float(latest_bar[5])
                    }
                    current_price = bar['close']
                    
                    self.logger.info(f"Bar: {symbol} @ {bar['datetime']} | O:{bar['open']:.3f} H:{bar['high']:.3f} L:{bar['low']:.3f} C:{bar['close']:.3f} V:{bar['volume']:.0f}")
                
                # Handle tick data (dict format)
                elif isinstance(tick_data, dict):
                    current_price = tick_data.get('lastPrice')
                    if not current_price:
                        continue
                    
                    bar = {
                        'datetime': datetime.fromtimestamp(tick_data.get('time', time.time() * 1000) / 1000),
                        'open': tick_data.get('open'),
                        'high': tick_data.get('high'),
                        'low': tick_data.get('low'),
                        'close': current_price,
                        'volume': tick_data.get('volume')
                    }
                else:
                    self.logger.warning(f"Unknown data format for {symbol}: type={type(tick_data)}, value={tick_data}")
                    continue
                
                # Pass to Strategy
                signal = self.strategy.on_bar(bar)
                self._handle_signal(symbol, signal, current_price)
                
            except Exception as e:
                self.logger.error(f"Strategy execution error for {symbol}: {e}")
                self.logger.error(f"Traceback: {traceback.format_exc()}")
                self.logger.error(f"Raw data received: {tick_data}")

    def _handle_signal(self, symbol: str, signal: Any, price: float):
        """
        Execute signal from strategy.
        """
        if signal == "hold":
            return
            
        self.logger.info(f"Received Signal for {symbol}: {signal}")
        
        # Check Assets/Positions
        positions = self.order_manager.get_positions()
        position_map = {p.stock_code: p.volume for p in positions}
        current_pos = position_map.get(symbol, 0)
        
        asset = self.order_manager.get_asset()
        available_cash = asset.cash
        
        if signal == "buy":
            # Simple logic: Buy 100 shares if enough cash
            # In production, size should come from Strategy or Risk Manager
            cost = price * 100
            if available_cash > cost:
                self.order_manager.buy(symbol, price, 100, "LiveStrategy")
            else:
                self.logger.warning(f"Insufficient cash to buy {symbol}. Cash: {available_cash}, Cost: {cost}")
                
        elif signal == "sell":
            if current_pos > 0:
                # Sell all
                self.order_manager.sell(symbol, price, current_pos, "LiveStrategy")
            else:
                self.logger.warning(f"No position to sell for {symbol}")

    def get_portfolio_status(self):
        """
        Print current portfolio status.
        """
        asset = self.order_manager.get_asset()
        self.logger.info(f"Cash: {asset.cash}, Market Value: {asset.market_value}, Total: {asset.total_asset}")
        
        positions = self.order_manager.get_positions()
        for p in positions:
            self.logger.info(f"Position: {p.stock_code}, Vol: {p.volume}, PnL: {p.market_value - (p.open_price * p.volume)}")
