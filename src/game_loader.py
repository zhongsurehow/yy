import json
from pathlib import Path
from typing import List, Dict

from .card import Card

class GameLoader:
    """Handles loading all game data from the file system."""

    def __init__(self, assets_path: Path):
        """Initializes the loader with the path to the assets directory."""
        self.assets_path = assets_path
        if not self.assets_path.exists():
            raise FileNotFoundError(f"Assets directory not found at '{self.assets_path}'")

    def load_all_cards(self) -> Dict[str, List[Card]]:
        """
        Loads all card data from the `assets/data/cards` subdirectory.

        Returns:
            A dictionary mapping deck type (e.g., "basic", "function") to a list of Card objects.
        """
        decks = {
            "basic": [],
            "function": [],
            "destiny": [],
            "natal": [],
            "state": []
        }
        card_data_path = self.assets_path / "data" / "cards"

        print("--- Loading Card Data from File System ---")
        if not card_data_path.is_dir():
            print(f"Error: Card data path not found at '{card_data_path}'")
            return decks

        # Find all json files recursively
        json_files = list(card_data_path.rglob("*.json"))
        print(f"Found {len(json_files)} card files to load.")

        for file_path in json_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    card = Card.from_json(data)

                    card_type = card.card_type
                    if card_type in decks:
                        decks[card_type].append(card)
                    elif card_type in ["stem", "branch", "celestial"]:
                         decks["state"].append(card)
                    else:
                        print(f"Warning: Card '{card.card_id}' has unknown type '{card_type}'. Skipping.")

            except json.JSONDecodeError:
                print(f"Error: Could not decode JSON from {file_path}")
            except Exception as e:
                print(f"Error: Failed to load card from {file_path}: {e}")

        print(f"Loaded {len(decks['basic'])} basic cards.")
        print(f"Loaded {len(decks['function'])} function cards.")
        print(f"Loaded {len(decks['destiny'])} destiny cards.")
        print("------------------------------------------")

        return decks