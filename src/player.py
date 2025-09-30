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

    hand: List[Card] = field(default_factory=list)
    discard_pile: List[Card] = field(default_factory=list)
    status_effects: List[Dict[str, Any]] = field(default_factory=list)

    played_card: Card | None = None
    has_moved: bool = False

    def __repr__(self) -> str:
        statuses = [s.get('status_id') for s in self.status_effects]
        return f"Player(id='{self.player_id}', name='{self.name}', health={self.health}, gold={self.gold}, position='{self.position}', statuses={statuses})"

    def add_card_to_hand(self, card: Card):
        self.hand.append(card)

    def play_card(self, card_id: str) -> Card | None:
        card_to_play = next((card for card in self.hand if card.card_id == card_id), None)
        if card_to_play:
            self.hand.remove(card_to_play)
            self.played_card = card_to_play
            return card_to_play
        return None

    def discard_played_card(self):
        if self.played_card:
            self.discard_pile.append(self.played_card)
            self.played_card = None

    def change_resource(self, resource_type: str, value: int):
        if resource_type == "health":
            self.health += value
        elif resource_type == "gold":
            self.gold += value
        elif resource_type == "yin_yang":
            self.yin_yang += value
        else:
            print(f"Warning: Unknown resource type '{resource_type}'")

    def add_status(self, status: Dict[str, Any]):
        """Adds a new status effect to the player."""
        self.status_effects.append(status)
        print(f"      - Status Applied: {status.get('status_id')} to {self.name} for {status.get('duration')} turn(s).")

    def remove_status(self, status_id: str):
        """Removes a status effect by its ID."""
        status_to_remove = next((s for s in self.status_effects if s.get("status_id") == status_id), None)
        if status_to_remove:
            self.status_effects.remove(status_to_remove)
            print(f"      - Status Removed: {status_id} from {self.name}.")
        else:
            print(f"      - Attempted to remove status {status_id}, but it was not found on {self.name}.")

    def tick_statuses(self):
        """Decrements the duration of all temporary statuses and removes expired ones."""
        # We iterate over a copy of the list to allow safe removal
        for status in self.status_effects[:]:
            if 'duration' in status:
                status['duration'] -= 1
                if status['duration'] <= 0:
                    self.status_effects.remove(status)
                    print(f"  - Status Expired: {status.get('status_id')} on {self.name}.")