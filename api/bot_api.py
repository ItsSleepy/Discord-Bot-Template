"""
Web API for Bot Statistics
Provides a simple Flask API to serve bot stats to the website
"""

from flask import Flask, jsonify
from flask_cors import CORS
import threading
from datetime import datetime

class BotAPI:
    def __init__(self, bot):
        self.bot = bot
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for website access
        
        self.setup_routes()
        
    def setup_routes(self):
        @self.app.route('/api/status', methods=['GET'])
        def get_status():
            """Return simple bot status for website footer"""
            try:
                stats = {
                    'online': self.bot.is_ready(),
                    'servers': len(self.bot.guilds),
                    'users': sum(guild.member_count for guild in self.bot.guilds),
                    'latency': round(self.bot.latency * 1000),  # ms
                    'timestamp': datetime.now().isoformat()
                }
                return jsonify(stats)
            except Exception as e:
                return jsonify({
                    'online': False,
                    'error': str(e)
                }), 200  # Still return 200 to show offline status
        
        @self.app.route('/api/stats', methods=['GET'])
        def get_stats():
            """Return bot statistics"""
            try:
                import psutil
                import os
                
                # Calculate uptime
                uptime = datetime.now() - self.bot.start_time
                uptime_seconds = uptime.total_seconds()
                days = int(uptime_seconds // 86400)
                hours = int((uptime_seconds % 86400) // 3600)
                minutes = int((uptime_seconds % 3600) // 60)
                uptime_str = f"{days}d {hours}h {minutes}m"
                
                # Get memory usage
                process = psutil.Process(os.getpid())
                memory_mb = round(process.memory_info().rss / 1024 / 1024)
                
                # Check database status
                try:
                    # Test database connection
                    if hasattr(self.bot, 'db'):
                        self.bot.db.execute("SELECT 1")
                        db_status = "Online"
                    else:
                        db_status = "Online"
                except:
                    db_status = "Offline"
                
                stats = {
                    'status': 'online',
                    'servers': len(self.bot.guilds),
                    'users': sum(guild.member_count for guild in self.bot.guilds),
                    'commands': len(self.bot.tree.get_commands()),
                    'uptime': uptime_str,
                    'latency': round(self.bot.latency * 1000),  # ms
                    'memory': memory_mb,  # MB
                    'database_status': db_status,
                    'timestamp': datetime.now().isoformat()
                }
                
                return jsonify(stats)
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'bot_ready': self.bot.is_ready(),
                'timestamp': datetime.now().isoformat()
            })
    
    def run(self):
        """Run the Flask server in a separate thread"""
        thread = threading.Thread(target=self._run_server, daemon=True)
        thread.start()
    
    def _run_server(self):
        """Internal method to run Flask server"""
        try:
            import logging
            log = logging.getLogger('werkzeug')
            log.setLevel(logging.WARNING)  # Show warnings and errors
            
            print("=" * 50)
            print("Starting Flask API Server...")
            print(f"Server will be available at: http://localhost:5000")
            print(f"Status endpoint: http://localhost:5000/api/status")
            print(f"Stats endpoint: http://localhost:5000/api/stats")
            print("=" * 50)
            
            self.app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
        except Exception as e:
            print(f"ERROR starting Flask server: {e}")
            import traceback
            traceback.print_exc()

