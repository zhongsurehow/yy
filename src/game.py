import random
from pathlib import Path
from typing import List

from .game_loader import GameLoader
from .game_state import GameState
from .player import Player
from .card import Card
from .effect_engine import EffectEngine

class Game:
    """Orchestrates the setup and execution of the game."""

    def __init__(self, player_names: List[str], zip_path_str: str):
        self.game_state = GameState()
        self.player_names = player_names
        self.loader = GameLoader(Path(zip_path_str))
        self.effect_engine = EffectEngine(self.game_state)

    def setup(self, test_cards: List[str] = None):
        """Initializes the game state, with an option to inject specific test cards."""
        print("\n--- Setting up a new game of Tianji Bian ---")

        all_decks = self.loader.load_all_cards()
        self.game_state.basic_deck = all_decks.get("basic", [])

        random.shuffle(self.game_state.basic_deck)

        for i, name in enumerate(self.player_names):
            self.game_state.players.append(Player(player_id=str(i + 1), name=name))

        # Manually set player positions for specific testing
        ren_zones = [zone.zone_id for zone in self.game_state.game_board.zones.values() if zone.department == 'ren']
        tian_zones = [zone.zone_id for zone in self.game_state.game_board.zones.values() if zone.department == 'tian']

        if ren_zones:
            self.game_state.players[0].position = ren_zones[0]
        if tian_zones and len(self.game_state.players) > 1:
            self.game_state.players[1].position = tian_zones[0]
        if ren_zones and len(self.game_state.players) > 2:
             self.game_state.players[2].position = ren_zones[1]


        if test_cards:
            for i, player in enumerate(self.game_state.players):
                if i < len(test_cards):
                    card_id_to_find = test_cards[i]
                    test_card = next((c for c in self.game_state.basic_deck if c.card_id == card_id_to_find), None)
                    if test_card:
                        player.add_card_to_hand(test_card)
                        self.game_state.basic_deck.remove(test_card)

        for player in self.game_state.players:
            while len(player.hand) < 7 and self.game_state.basic_deck:
                player.add_card_to_hand(self.game_state.basic_deck.pop())

        print("\nGame setup complete.")

    def run(self, num_turns: int = 1):
        """Runs the main game loop for a specified number of turns."""
        print(f"\n--- Starting Game Run ({num_turns} turn(s)) ---")

        for turn in range(1, num_turns + 1):
            self.game_state.current_turn = turn
            print(f"\n***** Turn {self.game_state.current_turn} *****")

            self._execute_time_phase()
            self._execute_placement_phase()
            self._execute_movement_phase()
            self._execute_interpretation_phase()
            self._execute_resolution_phase()
            self._execute_upkeep_phase()

        print("\n--- Game Run Finished ---")
        print("Final Player States:")
        for player in self.game_state.players:
            print(f"  - {player}")

    def _execute_time_phase(self):
        self.game_state.set_phase("TIME")
        print("  - Updating celestial stems and branches...")

    def _execute_placement_phase(self):
        self.game_state.set_phase("PLACEMENT")
        for player in self.game_state.players:
            card_to_play = next((c for c in player.hand if c.card_type == 'basic'), None)
            if card_to_play:
                player.play_card(card_to_play.card_id)
                print(f"  - {player.name} has placed card {card_to_play.name} face down.")

    def _execute_movement_phase(self):
        self.game_state.set_phase("MOVEMENT")
        print("  - Players move (simulated).")

    def _execute_interpretation_phase(self):
        self.game_state.set_phase("INTERPRETATION")
        for player in self.game_state.players:
            if player.played_card:
                card = player.played_card
                print(f"\n  - {player.name} (at {player.position}) reveals {card.name}!")

                player_zone = self.game_state.game_board.get_zone(player.position)
                if not player_zone:
                    continue

                variant_key = player_zone.department
                variant_effect = card.core_mechanism.get("variants", {}).get(variant_key, {}).get("effect")

                if variant_effect:
                    self.effect_engine.execute_effect(variant_effect, player)
                elif card.effect:
                    self.effect_engine.execute_effect(card.effect, player)

    def _execute_resolution_phase(self):
        self.game_state.set_phase("RESOLUTION")
        print("\n  - Calculating Tian Bu rewards and Di Bu penalties...")

    def _execute_upkeep_phase(self):
        self.game_state.set_phase("UPKEEP")
        print("  - Processing upkeep...")
        for player in self.game_state.players:
            player.tick_statuses()
            player.discard_played_card()
        print("  - Players discard played cards.")