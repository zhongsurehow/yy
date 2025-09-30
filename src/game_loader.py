import json
import zipfile
from pathlib import Path
from typing import List, Dict

from .card import Card

class GameLoader:
    """Handles loading all game data from a zip archive."""

    def __init__(self, zip_path: Path):
        """Initializes the loader with the path to the zip archive."""
        self.zip_path = zip_path
        if not self.zip_path.exists():
            raise FileNotFoundError(f"Zip archive not found at '{self.zip_path}'")

    def load_all_cards(self) -> Dict[str, List[Card]]:
        """
        Loads all card data directly from the zip archive without extracting.

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
        # The path to the cards inside the zip archive structure
        card_data_prefix = "tianji-fix-data-and/assets/data/cards/"

        print("--- Loading Card Data from Zip Archive ---")

        try:
            with zipfile.ZipFile(self.zip_path, 'r') as z:
                # Find all relevant JSON files within the zip
                json_files = [name for name in z.namelist() if name.startswith(card_data_prefix) and name.endswith('.json')]
                print(f"Found {len(json_files)} card files in the archive.")

                for file_path in json_files:
                    try:
                        with z.open(file_path, 'r') as f:
                            # The file is opened in binary mode, so we must decode it to utf-8
                            data = json.loads(f.read().decode('utf-8'))
                            card = Card.from_json(data)

                            card_type = card.card_type
                            if card_type in decks:
                                decks[card_type].append(card)
                            elif card_type in ["stem", "branch"]: # Group stems and branches into the 'state' deck
                                 decks["state"].append(card)
                            else:
                                print(f"Warning: Card '{card.card_id}' has unknown type '{card_type}'. Skipping.")

                    except json.JSONDecodeError:
                        print(f"Error: Could not decode JSON from {file_path} in zip")
                    except Exception as e:
                        print(f"Error: Failed to load card from {file_path} in zip: {e}")
        except zipfile.BadZipFile:
            print(f"Error: Bad zip file at '{self.zip_path}'")
            return decks
        except Exception as e:
            print(f"An unexpected error occurred while reading the zip file: {e}")
            return decks

        print(f"Loaded {len(decks['basic'])} basic cards.")
        print(f"Loaded {len(decks['function'])} function cards.")
        print(f"Loaded {len(decks['destiny'])} destiny cards.")
        print("------------------------------------------")

        return decks