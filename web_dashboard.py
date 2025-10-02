"""
Web Dashboard for Monitoring Trading Bot
"""
import logging
from flask import Flask, render_template, jsonify
from datetime import datetime
import json
import os
from threading import Thread

logger = logging.getLogger(__name__)

class WebDashboard:
    """Web dashboard for bot monitoring"""
    
    def __init__(self, bot_instance=None):
        """Initialize web dashboard
        
        Args:
            bot_instance: Reference to the main bot instance
        """
        self.app = Flask(__name__)
        self.bot = bot_instance
        self.setup_routes()
        
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            """Main dashboard page"""
            return render_template('dashboard.html')
        
        @self.app.route('/api/status')
        def get_status():
            """Get bot status"""
            if not self.bot:
                return jsonify({'error': 'Bot not initialized'}), 503
            
            return jsonify({
                'running': self.bot.running,
                'total_trades': self.bot.total_trades,
                'winning_trades': self.bot.winning_trades,
                'losing_trades': self.bot.losing_trades,
                'win_rate': (self.bot.winning_trades / max(1, self.bot.winning_trades + self.bot.losing_trades)) * 100,
                'total_profit': self.bot.total_profit,
                'current_balance': self.bot.current_balance,
                'initial_balance': self.bot.initial_balance,
                'profit_percent': ((self.bot.current_balance - self.bot.initial_balance) / self.bot.initial_balance) * 100
            })
        
        @self.app.route('/api/trades')
        def get_trades():
            """Get trade history"""
            trades = []
            history_file = 'bot_data/trade_history.jsonl'
            
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    for line in f:
                        if line.strip():
                            trades.append(json.loads(line))
            
            # Return last 50 trades
            return jsonify(trades[-50:])
        
        @self.app.route('/api/positions')
        def get_positions():
            """Get current positions"""
            if not self.bot:
                return jsonify({'error': 'Bot not initialized'}), 503
            
            positions = []
            if hasattr(self.bot, 'positions'):
                for symbol, position in self.bot.positions.items():
                    if position:
                        positions.append({
                            'symbol': symbol,
                            'qty': position.get('currentQty', 0),
                            'entry_price': position.get('avgEntryPrice', 0),
                            'unrealized_pnl': position.get('unrealisedPnl', 0),
                            'leverage': position.get('realLeverage', 0)
                        })
            
            return jsonify(positions)
        
        @self.app.route('/health')
        def health_check():
            """Health check endpoint for monitoring"""
            if not self.bot:
                return jsonify({
                    'status': 'error',
                    'message': 'Bot not initialized'
                }), 503
            
            health_status = {
                'status': 'healthy' if self.bot.running else 'stopped',
                'running': self.bot.running,
                'timestamp': datetime.now().isoformat(),
                'total_trades': self.bot.total_trades,
                'current_balance': self.bot.current_balance,
            }
            
            # Add uptime if available
            if hasattr(self.bot, 'start_time'):
                uptime_seconds = (datetime.now() - self.bot.start_time).total_seconds()
                health_status['uptime_seconds'] = uptime_seconds
            
            return jsonify(health_status)
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the web dashboard
        
        Args:
            host: Host to bind to (default: 0.0.0.0)
            port: Port to bind to (default: 5000)
            debug: Enable debug mode (default: False)
        """
        logger.info(f"Starting web dashboard on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug, use_reloader=False)
    
    def run_async(self, host='0.0.0.0', port=5000):
        """Run the web dashboard in a separate thread
        
        Args:
            host: Host to bind to (default: 0.0.0.0)
            port: Port to bind to (default: 5000)
        """
        thread = Thread(target=self.run, args=(host, port, False), daemon=True)
        thread.start()
        logger.info(f"Web dashboard running in background on {host}:{port}")
        return thread
