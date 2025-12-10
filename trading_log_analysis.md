# Live Trading Log Analysis

## Test History

| Date | Scheduled | Actual Run | Status | Notes |
|------|-----------|------------|--------|-------|
| 2025-12-03 | 09:25 | 19:44:20 | ❌ Missed | Market closed before run |
| 2025-12-04 | 09:25 | 20:09:01 | ❌ Missed | Market closed before run |
| 2025-12-05 | 09:25 | 09:25:10 | ⚠️ Partial | Connected but callback crashed - data format bug |

## Issues Identified

1. **Sleep mode on battery** - Computer sleeps after 3 min on battery
2. **Task requires login** - Task set to "interactive mode only"

## Recommendations

- Keep laptop **plugged in** overnight
- Ensure you're logged in (don't just lock screen - stay logged in)
- Launch Mini-QMT and log in before leaving

## Log Files Location

- `live_trading_510050_YYYYMMDD.log` - Daily trading logs
- Check for entries between 09:25 - 15:00 to confirm successful run

## Success Indicators

A successful run should show:
```
INFO - Market is open. Initializing trading engine...
INFO - Connecting to Mini-QMT...
INFO - Connection successful. Starting trading loop...
INFO - Subscribing to 510050.SH (5m)
```

## Failure Indicators

```
INFO - Market closed for today. Exiting.  <- Script ran too late
ERROR - Failed to connect to Mini-QMT     <- QMT not running
```
