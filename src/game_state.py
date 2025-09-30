import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any

from .card import Card
from .player import Player
from .game_board import GameBoard

@dataclass
class GameState:
    """Manages the entire state of the game."""
    players: List[Player] = field(default_factory=list)
    game_board: GameBoard = field(default_factory=GameBoard)

    # Deck piles
    basic_deck: List[Card] = field(default_factory=list)
    function_deck: List[Card] = field(default_factory=list)
    destiny_deck: List[Card] = field(default_factory=list)

    # Game flow
    current_turn: int = 1
    current_phase: str = "SETUP" # e.g., SETUP, TIME, PLACEMENT, MOVEMENT, etc.
    active_player_index: int = 0

    # Rule and effect tracking
    active_rules: Dict[str, Any] = field(default_factory=dict)
    last_resolved_effect: Dict[str, Any] | None = None
    interrupt_flags: Dict[str, bool] = field(default_factory=dict)
    effect_queue: List[Dict[str, Any]] = field(default_factory=list)

    def get_player(self, player_id: str) -> Player | None:
        """Finds a player by their ID."""
        return next((p for p in self.players if p.player_id == player_id), None)

    def get_active_player(self) -> Player:
        """Returns the player whose turn it is."""
        return self.players[self.active_player_index]

    def advance_to_next_player(self):
        """Advances the turn to the next player."""
        self.active_player_index = (self.active_player_index + 1) % len(self.players)
        if self.active_player_index == 0:
            self.current_turn += 1
            logging.info(f"--- Starting Turn {self.current_turn} ---")

    def set_phase(self, phase_name: str):
        """Sets the current game phase."""
        self.current_phase = phase_name
        logging.info(f"== Phase: {phase_name} ==")

    def __repr__(self) -> str:
        return f"GameState(Turn={self.current_turn}, Phase='{self.current_phase}', ActivePlayer='{self.get_active_player().name}')"