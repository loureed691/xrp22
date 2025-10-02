# Troubleshooting Guide

Common issues and solutions for the XRP Hedge Bot.

## Installation Issues

### Python Not Found
**Error:** `python: command not found` or `Python is not installed`

**Solutions:**
1. Install Python 3.11+ from https://www.python.org/downloads/
2. During installation, check "Add Python to PATH"
3. Restart your terminal/command prompt
4. Verify: `python --version`

### Pip Install Fails
**Error:** `ERROR: Could not install packages`

**Solutions:**
1. Update pip: `python -m pip install --upgrade pip`
2. Use virtual environment: `python -m venv venv`
3. Activate venv: `venv\Scripts\activate` (Windows)
4. Retry: `pip install -r requirements.txt`

### Virtual Environment Issues
**Error:** Cannot activate virtual environment

**Solutions:**
1. Windows PowerShell: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
2. Use Command Prompt instead of PowerShell
3. Or create new venv: `python -m venv venv`

## Configuration Issues

### Missing .env File
**Error:** `API credentials are required`

**Solutions:**
1. Copy template: `copy .env.example .env`
2. Edit .env with your API credentials
3. Ensure .env is in the same directory as bot.py

### Invalid API Credentials
**Error:** `401 Unauthorized` or `Invalid API credentials`

**Solutions:**
1. Verify API key, secret, and passphrase in .env
2. Check for extra spaces or quotes
3. Ensure API key has futures trading permission
4. Try generating new API keys
5. Verify you're using correct environment (testnet/production)

### API Key Permissions
**Error:** `Insufficient permissions` or `Access denied`

**Solutions:**
1. Go to KuCoin API Management
2. Edit API key permissions
3. Enable: "General" and "Futures Trading"
4. DO NOT enable "Transfer" or "Withdrawal" (for security)
5. Save and restart bot

## Connection Issues

### Cannot Connect to API
**Error:** `Connection timeout` or `Failed to connect`

**Solutions:**
1. Check internet connection
2. Verify KuCoin API status: https://status.kucoin.com/
3. Check firewall/antivirus settings
4. Try testnet first: `USE_TESTNET=true`
5. Check if VPN is interfering

### Rate Limit Errors
**Error:** `429 Too Many Requests` or `Rate limit exceeded`

**Solutions:**
1. Increase bot cycle interval (default is 60s)
2. Wait a few minutes and retry
3. Check if you have multiple bots running
4. Reduce API call frequency

### SSL/Certificate Errors
**Error:** `SSL certificate verify failed`

**Solutions:**
1. Update Python: `python -m pip install --upgrade certifi`
2. Update requests: `pip install --upgrade requests`
3. Check system time is correct
4. Temporarily disable VPN

## Trading Issues

### Bot Not Trading
**Error:** Bot runs but doesn't execute trades

**Possible Causes:**
1. **Insufficient balance**
   - Check: `Available balance` in logs
   - Solution: Add funds to Futures account

2. **Weak signals**
   - Check: `Signal strength` in logs
   - Solution: Signal must be >60 to trade
   - Normal behavior if market is ranging

3. **No market volatility**
   - Solution: Wait for price movement
   - Check different timeframes

4. **Position limits reached**
   - Solution: Close existing positions
   - Or increase balance

### Orders Failing
**Error:** `Order failed` or `Order rejected`

**Solutions:**
1. **Insufficient margin**
   - Reduce position size percent
   - Add more funds
   - Lower leverage

2. **Position size too small**
   - Minimum: 1 contract
   - Increase balance
   - Adjust MAX_POSITION_SIZE_PERCENT

3. **Price movement**
   - Market orders should work
   - Check market liquidity
   - Try testnet first

### Position Not Closing
**Error:** Stop loss/take profit not triggering

**Solutions:**
1. Check position status in KuCoin UI
2. Verify price vs. stop loss level
3. Check logs for close attempts
4. Manually close if needed
5. Restart bot to refresh position state

## Balance Issues

### Balance Not Updating
**Error:** Shows wrong balance

**Solutions:**
1. Check KuCoin account directly
2. Ensure funds are in Futures account (not Main)
3. Transfer from Main to Futures if needed
4. Restart bot to refresh

### Insufficient Balance
**Error:** `Insufficient balance` but you have funds

**Solutions:**
1. Check if funds are in correct account (Futures vs Main)
2. Transfer to Futures account:
   - KuCoin UI → Assets → Transfer
   - From: Main Account
   - To: Futures Account
3. Check if funds are locked in open orders
4. Close unused positions

## Performance Issues

### Bot Running Slow
**Solutions:**
1. Check CPU/memory usage
2. Reduce logging verbosity
3. Increase cycle interval
4. Close other programs
5. Check internet speed

### High Memory Usage
**Solutions:**
1. Restart bot periodically
2. Clear old log files
3. Limit trade history size
4. Check for memory leaks (report if found)

## Data Issues

### No Market Data
**Error:** `Failed to get market data`

**Solutions:**
1. Check KuCoin API status
2. Verify symbol: XRPUSDTM
3. Check internet connection
4. Try testnet to isolate issue

### Indicator Errors
**Error:** `Insufficient data` or calculation errors

**Solutions:**
1. Wait for more candles (needs 30+)
2. Check kline data retrieval
3. Verify time range parameters
4. Review logs for API errors

## Logging Issues

### No Log File
**Error:** bot.log not created

**Solutions:**
1. Check file permissions
2. Run bot from correct directory
3. Check disk space
4. Manually create bot_data/ directory

### Log File Too Large
**Solutions:**
1. Archive old logs: `move bot.log bot_old.log`
2. Reduce logging level (WARNING instead of INFO)
3. Use log rotation (future feature)
4. Clear logs periodically

### UnicodeEncodeError on Windows
**Error:** `UnicodeEncodeError: 'charmap' codec can't encode character '\u2713'`

**Description:**
This error occurs on Windows when the bot tries to log messages containing Unicode characters (like ✓) to the console, which uses cp1252 encoding by default.

**Solutions:**
1. **Automatic Fix (v2.0+):** The bot now handles this automatically
2. **If still occurring:** Update to latest version
3. **Manual workaround:** Set console to UTF-8: `chcp 65001`
4. **Alternative:** Use Windows Terminal (better Unicode support)

**Note:** This has been fixed in bot.py and bot_legacy.py as of the latest update. Log files are written with UTF-8 encoding, and console output gracefully handles encoding errors. See UNICODE_FIX.md for technical details.

## Module Import Errors

### Cannot Import Module
**Error:** `ModuleNotFoundError: No module named 'X'`

**Solutions:**
1. Activate virtual environment
2. Install dependencies: `pip install -r requirements.txt`
3. Check Python version: `python --version`
4. Reinstall specific package: `pip install <package>`

### Import Path Issues
**Error:** `ImportError: attempted relative import with no known parent package`

**Solutions:**
1. Run from project root: `cd /path/to/xrp22`
2. Use absolute paths in imports
3. Check PYTHONPATH environment variable

## Windows-Specific Issues

### Scripts Not Running
**Error:** `.bat` files not working

**Solutions:**
1. Run from Command Prompt (not PowerShell)
2. Right-click → Run as Administrator
3. Check file associations
4. Run Python directly: `python bot.py`

### Path Issues
**Error:** File not found errors

**Solutions:**
1. Use full paths in .env
2. Run scripts from project directory
3. Check backslash vs forward slash
4. Use `cd C:\path\to\xrp22`

### Permission Errors
**Error:** Access denied or permission errors

**Solutions:**
1. Run Command Prompt as Administrator
2. Check antivirus settings
3. Exclude project folder from scanning
4. Check file permissions

## Testnet Issues

### Testnet Not Working
**Error:** Issues with sandbox environment

**Solutions:**
1. Verify URL: `https://api-sandbox-futures.kucoin.com`
2. Use testnet credentials (different from production)
3. Get test funds from faucet
4. Check testnet status
5. Try production API (with caution)

### No Test Funds
**Solutions:**
1. Request from testnet faucet
2. Contact KuCoin support
3. Use different testnet account
4. Start with production (small amount)

## Strategy Issues

### Too Many Losing Trades
**Solutions:**
1. Review signal strength threshold (increase to 70-80)
2. Adjust indicator parameters
3. Reduce position size
4. Tighten stop losses
5. Test on historical data first
6. Consider market conditions

### Not Hedging When Expected
**Solutions:**
1. Check hedge trigger: position losing >2%
2. Verify signal strength for hedge
3. Review hedge_strategy.py logic
4. Check position state
5. Monitor logs for hedge attempts

### Frequent Stop Losses
**Solutions:**
1. Increase STOP_LOSS_PERCENT (e.g., 7%)
2. Reduce LEVERAGE (e.g., 5x or 8x)
3. Use wider Bollinger Bands
4. Adjust RSI thresholds
5. Wait for stronger signals (>70 strength)

## Error Messages Explained

### `ValueError: API credentials are required`
- Missing or invalid .env file
- Solution: Configure .env with valid credentials

### `requests.exceptions.ConnectionError`
- Network connectivity issue
- Solution: Check internet, firewall, VPN

### `json.decoder.JSONDecodeError`
- Invalid API response format
- Solution: Check API endpoint, retry request

### `KeyError: 'data'`
- Unexpected API response structure
- Solution: Check API version, review endpoint

### `ZeroDivisionError`
- Calculation error with invalid data
- Solution: Check data validity, add error handling

### `OSError: [WinError 10048]`
- Port already in use (if using WebSocket)
- Solution: Close other instances, restart system

## Getting Help

If issues persist:

1. **Check Logs:**
   - Review `bot.log` for detailed errors
   - Share relevant log excerpts when seeking help

2. **GitHub Issues:**
   - Search existing issues
   - Create new issue with:
     - Error message
     - Log excerpt
     - Configuration (remove credentials)
     - Steps to reproduce

3. **KuCoin Support:**
   - For API-specific issues
   - Account or balance problems
   - https://support.kucoin.com/

4. **Community:**
   - Share experiences (remove credentials!)
   - Learn from others
   - Contribute solutions

## Prevention Tips

1. **Always test on testnet first**
2. **Start with small amounts**
3. **Monitor bot closely initially**
4. **Keep software updated**
5. **Regular backups of config**
6. **Review logs daily**
7. **Set up alerts for critical errors**
8. **Don't modify code unless you understand it**
9. **Keep API keys secure**
10. **Document any custom changes**

## Emergency Procedures

### Stop Bot Immediately
1. Press `Ctrl+C` in terminal
2. If unresponsive, close terminal
3. Check for running Python processes
4. Kill if necessary: `taskkill /F /IM python.exe`

### Close All Positions
1. Log into KuCoin directly
2. Go to Futures Trading
3. Close positions manually
4. Cancel pending orders
5. Verify in account overview

### Revoke API Access
1. Go to KuCoin API Management
2. Delete or disable API key
3. Bot will stop trading immediately
4. Generate new keys when ready

## Support Checklist

When reporting issues, provide:
- [ ] Python version
- [ ] Operating system
- [ ] Error message (full text)
- [ ] Relevant log lines
- [ ] Configuration (sanitized)
- [ ] Steps to reproduce
- [ ] What you've tried
- [ ] Expected vs actual behavior

This helps maintainers assist you faster!
