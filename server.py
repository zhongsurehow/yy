import logging
from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit

from src.game import Game

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__, template_folder='tianji-fix-data-and')
# It's important to set a secret key for session management
app.config['SECRET_KEY'] = 'a_very_secret_key_for_tianji_bian!'
socketio = SocketIO(app)

# --- Game Instance ---
# In a real-world scenario, you'd manage game instances for different rooms/sessions.
# For this prototype, we'll use a single global game instance.
game = Game(player_names=["玩家一", "玩家二"], assets_path_str="tianji-fix-data-and/assets")

@app.route('/')
def index():
    """Serve the main game page."""
    logging.info("Serving game.html")
    # render_template will look in the 'templates' folder, which we've set to 'tianji-fix-data-and'
    return render_template('game.html')

@socketio.on('connect')
def handle_connect():
    """Handle a new client connection."""
    logging.info('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    """Handle a client disconnection."""
    logging.info('Client disconnected')

# --- Game Logic Handlers ---

def broadcast_game_state():
    """Serializes and broadcasts the current game state to all clients."""
    state_dict = game.game_state.to_dict()
    socketio.emit('game_state_update', state_dict)
    logging.info("Game state update broadcasted to all clients.")

@socketio.on('start_game')
def handle_start_game():
    """Handles the start game event from a client."""
    logging.info("Received 'start_game' event.")
    game.setup()
    broadcast_game_state()

@socketio.on('next_round')
def handle_next_round():
    """Handles the next round event from a client."""
    logging.info("Received 'next_round' event.")
    game.run_round(game.game_state.current_turn + 1)
    broadcast_game_state()

@socketio.on('reset_game')
def handle_reset_game():
    """Handles the reset game event from a client."""
    global game
    logging.info("Received 'reset_game' event. Resetting game state.")
    game = Game(player_names=["玩家一", "玩家二"], assets_path_str="tianji-fix-data-and/assets")
    # We don't set up the game here, just reset the object.
    # The client will need to send 'start_game' again.
    # For simplicity, we'll send a basic initial state.
    initial_state = {
        "players": [
            {"name": "玩家一", "health": 200, "gold": 100, "position": None, "is_eliminated": False},
            {"name": "玩家二", "health": 200, "gold": 100, "position": None, "is_eliminated": False}
        ],
        "current_turn": 0,
        "current_phase": "SETUP"
    }
    socketio.emit('game_state_update', initial_state)


if __name__ == '__main__':
    logging.info("Starting Tianji Bian server...")
    # host='0.0.0.0' makes the server accessible from the local network
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)