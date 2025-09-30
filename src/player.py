import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any
from .card import Card

@dataclass
class Player:
    """Represents a player in the game."""
    player_id: str
    name: str
    health: int = 200
    gold: int = 100
    yin_yang: int = 0
    position: str | None = None
    is_eliminated: bool = False

    hand: List[Card] = field(default_factory=list)
    status_effects: List[Dict[str, Any]] = field(default_factory=list)

    played_card: Card | None = None
    has_moved: bool = False

    def __repr__(self) -> str:
        statuses = [s.get('status_id') for s in self.status_effects]
        return f"Player(id='{self.player_id}', name='{self.name}', health={self.health}, gold={self.gold}, position='{self.position}', statuses={statuses})"

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the Player object to a dictionary."""
        return {
            "player_id": self.player_id,
            "name": self.name,
            "health": self.health,
            "gold": self.gold,
            "yin_yang": self.yin_yang,
            "position": self.position,
            "is_eliminated": self.is_eliminated,
            "hand": [card.to_dict() for card in self.hand],
            "status_effects": self.status_effects,
            "played_card": self.played_card.to_dict() if self.played_card else None,
        }

    def add_card_to_hand(self, card: Card):
        self.hand.append(card)

    def play_card(self, card_id: str) -> Card | None:
        card_to_play = next((card for card in self.hand if card.card_id == card_id), None)
        if card_to_play:
            self.hand.remove(card_to_play)
            self.played_card = card_to_play
            return card_to_play
        return None

    def can_afford(self, resource_type: str, value: int) -> bool:
        """Checks if the player has enough of a resource."""
        if resource_type == "health":
            return self.health >= value
        elif resource_type == "gold":
            return self.gold >= value
        elif resource_type == "yin_yang":
            return self.yin_yang >= value
        return False

    def change_resource(self, resource_type: str, value: int):
        if resource_type == "health":
            self.health += value
        elif resource_type == "gold":
            self.gold += value
        elif resource_type == "yin_yang":
            self.yin_yang += value
        else:
            logging.warning(f"Unknown resource type '{resource_type}'")

    def add_status(self, status: Dict[str, Any]):
        """Adds a new status effect to the player."""
        self.status_effects.append(status)
        logging.info(f"Status Applied: {status.get('status_id')} to {self.name} for {status.get('duration')} turn(s).")

    def remove_status(self, status_id: str):
        """Removes a status effect by its ID."""
        status_to_remove = next((s for s in self.status_effects if s.get("status_id") == status_id), None)
        if status_to_remove:
            self.status_effects.remove(status_to_remove)
            logging.info(f"Status Removed: {status_id} from {self.name}.")
        else:
            logging.warning(f"Attempted to remove status {status_id}, but it was not found on {self.name}.")

    def tick_statuses(self):
        """Decrements the duration of all temporary statuses and removes expired ones."""
        # We iterate over a copy of the list to allow safe removal
        for status in self.status_effects[:]:
            # Permanent statuses should not have their duration ticked down.
            if status.get('is_permanent', False):
                continue

            if 'duration' in status:
                status['duration'] -= 1
                if status['duration'] <= 0:
                    self.status_effects.remove(status)
                    logging.info(f"Status Expired: {status.get('status_id')} on {self.name}.")