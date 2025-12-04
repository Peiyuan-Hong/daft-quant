"""
RSI Live Trading Script for 510050.SH (50ETF)
5-Minute Data - Scheduled for Unattended Execution

Configuration:
- Symbol: 510050.SH
- Period: 5m (5-minute bars)
- Strategy: RSI (period=14, overbought=70, oversold=30)
- Account: 40688525 (Paper Trading)

Prerequisites:
- Mini-QMT must be running and logged in BEFORE this script starts
- xtquant must be installed
"""

import sys
import os
import time
from datetime import datetime, timedelta
import logging

# Add project root to path for proper imports
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from src.live_trading.engine import LiveTradeEngine
from src.strategy.rsi_strategy import RSIStrategy

# ============== CONFIGURATION ==============
MINI_QMT_PATH = r"C:\国金QMT交易端模拟\userdata_mini"
ACCOUNT_ID = "40688525"

SYMBOL = "510050.SH"  # 50ETF
PERIOD = "5m"         # 5-minute bars

# RSI Parameters
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70.0
RSI_OVERSOLD = 30.0

# Market Hours (China A-Share)
MARKET_OPEN_MORNING = "09:30"
MARKET_CLOSE_MORNING = "11:30"
MARKET_OPEN_AFTERNOON = "13:00"
MARKET_CLOSE_AFTERNOON = "15:00"

# Log file with date
LOG_FILE = f"live_trading_510050_{datetime.now().strftime('%Y%m%d')}.log"
# ===========================================

def setup_logging():
    """Setup logging to both file and console."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("RSI_Live_510050")

def is_market_hours():
    """Check if current time is within market hours."""
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    
    # Morning session: 09:30 - 11:30
    if MARKET_OPEN_MORNING <= current_time <= MARKET_CLOSE_MORNING:
        return True
    # Afternoon session: 13:00 - 15:00
    if MARKET_OPEN_AFTERNOON <= current_time <= MARKET_CLOSE_AFTERNOON:
        return True
    return False

def wait_for_market_open(logger):
    """Wait until market opens."""
    while not is_market_hours():
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        
        # If before morning open, wait
        if current_time < MARKET_OPEN_MORNING:
            wait_seconds = 30
            logger.info(f"Market not open yet. Current: {current_time}. Waiting {wait_seconds}s...")
            time.sleep(wait_seconds)
        # If in lunch break, wait
        elif MARKET_CLOSE_MORNING < current_time < MARKET_OPEN_AFTERNOON:
            wait_seconds = 60
            logger.info(f"Lunch break. Current: {current_time}. Waiting {wait_seconds}s...")
            time.sleep(wait_seconds)
        # If after close, exit
        elif current_time > MARKET_CLOSE_AFTERNOON:
            logger.info(f"Market closed for today. Exiting.")
            return False
    return True

def main():
    logger = setup_logging()
    
    logger.info("=" * 60)
    logger.info("RSI Live Trading Script Started")
    logger.info(f"Symbol: {SYMBOL}")
    logger.info(f"Period: {PERIOD}")
    logger.info(f"Account: {ACCOUNT_ID} (Paper Trading)")
    logger.info(f"RSI Config: period={RSI_PERIOD}, overbought={RSI_OVERBOUGHT}, oversold={RSI_OVERSOLD}")
    logger.info("=" * 60)
    
    # Wait for market if started early
    if not wait_for_market_open(logger):
        return
    
    logger.info("Market is open. Initializing trading engine...")
    
    # Initialize Strategy
    strategy = RSIStrategy(
        period=RSI_PERIOD,
        overbought=RSI_OVERBOUGHT,
        oversold=RSI_OVERSOLD
    )
    
    # Initialize Engine
    engine = LiveTradeEngine(
        strategy=strategy,
        account_id=ACCOUNT_ID,
        mini_qmt_path=MINI_QMT_PATH,
        symbols=[SYMBOL],
        period=PERIOD,
        log_file=LOG_FILE
    )
    
    # Start Trading
    try:
        logger.info("Connecting to Mini-QMT...")
        if engine.connect():
            logger.info("Connection successful. Starting trading loop...")
            engine.start()
        else:
            logger.error("Failed to connect to Mini-QMT. Is it running and logged in?")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        logger.info("Trading session ended.")

if __name__ == "__main__":
    main()
