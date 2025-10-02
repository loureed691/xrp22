"""
Telegram Notifications Module
"""
import logging
import requests
from typing import Optional
import os

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Send notifications via Telegram"""
    
    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        """Initialize Telegram notifier
        
        Args:
            bot_token: Telegram bot token
            chat_id: Telegram chat ID to send messages to
        """
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID', '')
        self.enabled = bool(self.bot_token and self.chat_id)
        
        if self.enabled:
            logger.info("Telegram notifications enabled")
        else:
            logger.info("Telegram notifications disabled (no credentials)")
    
    def send_message(self, message: str, parse_mode: str = 'Markdown') -> bool:
        """Send a message via Telegram
        
        Args:
            message: Message text to send
            parse_mode: Parse mode (Markdown or HTML)
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.debug("Telegram message sent successfully")
                return True
            else:
                logger.error(f"Failed to send Telegram message: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False
    
    def notify_trade(self, action: str, side: str, size: int, price: float, reason: str):
        """Notify about a trade execution
        
        Args:
            action: Trade action (open, close, hedge)
            side: Trade side (buy, sell)
            size: Position size
            price: Execution price
            reason: Trade reason
        """
        emoji = "📈" if side == "buy" else "📉"
        message = f"{emoji} *{action.upper()} {side.upper()}*\n\n"
        message += f"Size: `{size}` contracts\n"
        message += f"Price: `${price:.6f}`\n"
        message += f"Reason: {reason}"
        
        self.send_message(message)
    
    def notify_profit_loss(self, pnl: float, balance: float, roi: float):
        """Notify about profit/loss update
        
        Args:
            pnl: Profit/loss amount
            balance: Current balance
            roi: Return on investment percentage
        """
        emoji = "💰" if pnl >= 0 else "📉"
        sign = "+" if pnl >= 0 else ""
        
        message = f"{emoji} *P&L Update*\n\n"
        message += f"PnL: `{sign}${pnl:.2f}`\n"
        message += f"Balance: `${balance:.2f}`\n"
        message += f"ROI: `{sign}{roi:.2f}%`"
        
        self.send_message(message)
    
    def notify_signal(self, action: str, strength: int, reason: str):
        """Notify about trading signal
        
        Args:
            action: Signal action (buy, sell, hold)
            strength: Signal strength (0-100)
            reason: Signal reason
        """
        if action == 'hold':
            return  # Don't spam with hold signals
        
        emoji = "🟢" if action == "buy" else "🔴"
        message = f"{emoji} *Signal: {action.upper()}*\n\n"
        message += f"Strength: `{strength}/100`\n"
        message += f"Reason: {reason}"
        
        self.send_message(message)
    
    def notify_error(self, error_msg: str):
        """Notify about errors
        
        Args:
            error_msg: Error message
        """
        message = f"⚠️ *Error*\n\n`{error_msg}`"
        self.send_message(message)
    
    def notify_startup(self, config_summary: str):
        """Notify about bot startup
        
        Args:
            config_summary: Summary of bot configuration
        """
        message = f"🚀 *Bot Started*\n\n{config_summary}"
        self.send_message(message)
    
    def notify_shutdown(self, final_stats: str):
        """Notify about bot shutdown
        
        Args:
            final_stats: Final statistics summary
        """
        message = f"🛑 *Bot Stopped*\n\n{final_stats}"
        self.send_message(message)
