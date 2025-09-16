from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
import json
import sys
import os
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, Any, List
import uuid

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuration
PORT = int(os.getenv('PORT', 3002))
HOST = os.getenv('HOST', '0.0.0.0')
MAX_HISTORY_SIZE = 50

# Data structure for webhook requests
@dataclass
class WebhookRequest:
    timestamp: str
    method: str
    headers: Dict[str, str]
    payload: Dict[str, Any]
    source_ip: str
    request_id: str

# Global in-memory storage for webhook requests
webhook_history: List[WebhookRequest] = []

def add_webhook_to_history(webhook_request: WebhookRequest):
    """Add a webhook request to history, maintaining the maximum size limit."""
    global webhook_history
    webhook_history.insert(0, webhook_request)  # Add to beginning for chronological order
    
    # Keep only the last MAX_HISTORY_SIZE requests
    if len(webhook_history) > MAX_HISTORY_SIZE:
        webhook_history = webhook_history[:MAX_HISTORY_SIZE]

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/', methods=['GET'])
def serve_ui():
    """Serve the webhook UI interface."""
    return render_template('index.html')

@app.route('/', methods=['POST'])
def echo_json():
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        payload = request.get_json()
        
        # Create webhook request data structure
        webhook_request = WebhookRequest(
            timestamp=datetime.utcnow().isoformat() + 'Z',
            method=request.method,
            headers=dict(request.headers),
            payload=payload,
            source_ip=request.remote_addr or 'unknown',
            request_id=str(uuid.uuid4())
        )
        
        # Store in memory
        add_webhook_to_history(webhook_request)
        
        # Broadcast to all connected SocketIO clients
        socketio.emit('new_webhook', {
            'request': asdict(webhook_request),
            'total_count': len(webhook_history)
        })
        
        # Print formatted JSON to terminal with flush (existing behavior)
        print("\n=== Received JSON Payload ===", flush=True)
        print(json.dumps(payload, indent=2), flush=True)
        print("===========================\n", flush=True)
        sys.stdout.flush()  # Force flush stdout
        
        return jsonify(payload), 200
    except Exception as e:
        app.logger.error(f"Error processing request: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# SocketIO event handlers
@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print(f"Client connected: {request.sid}", flush=True)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print(f"Client disconnected: {request.sid}", flush=True)

@socketio.on('get_history')
def handle_get_history():
    """Send current webhook history to the requesting client."""
    emit('history_data', {
        'requests': [asdict(req) for req in webhook_history],
        'total_count': len(webhook_history)
    })

@socketio.on('clear_history')
def handle_clear_history():
    """Clear the webhook history."""
    global webhook_history
    webhook_history.clear()
    
    # Broadcast to all clients that history was cleared
    socketio.emit('history_cleared', {
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })
    
    print("Webhook history cleared", flush=True)

if __name__ == '__main__':
    # Force stdout to be unbuffered
    sys.stdout.reconfigure(line_buffering=True)
    socketio.run(app, host=HOST, port=PORT)
