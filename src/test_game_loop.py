import unittest
import logging
from unittest.mock import patch

from src.game import Game
from src.player import Player
from src.card import Card

class TestGameLoop(unittest.TestCase):

    def setUp(self):
        """Set up a new game instance for each test."""
        # Suppress noisy logs for cleaner test output, can be set to INFO for debugging
        logging.basicConfig(level=logging.WARNING)

        # We need a path to the assets directory to load card data
        # Assuming the test is run from the root directory
        self.assets_path = "tianji-fix-data-and/assets"
        self.game = Game(player_names=["Alice", "Bob"], assets_path_str=self.assets_path)
        self.game.setup()

        # For predictable testing, manually set player states
        self.alice = self.game.game_state.get_player("1")
        self.bob = self.game.game_state.get_player("2")
        self.alice.gold = 50
        self.bob.gold = 50

        # Place Alice in a Tian zone and Bob in a Di zone for the resolution phase test
        self.alice.position = "li_tian" # Li palace is 'fire'
        self.bob.position = "kan_di"   # Kan palace is 'water'

    def test_time_and_resolution_phase(self):
        """
        Tests if the Time Phase correctly sets rewards/penalties and
        if the Resolution Phase correctly applies them.
        """
        # --- TIME PHASE ---
        # Manually set Gan-Zhi to get a predictable outcome.
        # Stem: Jia (wood) -> generates Fire (离), overcomes Earth (坤, 艮)
        # Branch: Zi (water) -> generates Wood (震, 巽), overcomes Fire (离)
        # Beneficial for: Fire, Wood. Harmful for: Earth, Fire.
        # Li (fire) is both beneficial and harmful. For Tian bu, harmful (stagnation) wins.
        # Kan (water) is neutral.

        # Correctly populate the decks before calling the phase method
        # This prevents the "deck is empty" error.
        stem_card = Card(card_id="celestial_stem_jia", name="甲", card_type="celestial_stem")
        branch_card = Card(card_id="terrestrial_branch_zi", name="子", card_type="terrestrial_branch")
        self.game.game_state.celestial_stem_deck.append(stem_card)
        self.game.game_state.terrestrial_branch_deck.append(branch_card)

        self.game._execute_time_phase()

        li_tian_zone = self.game.game_state.game_board.get_zone("li_tian")
        kan_di_zone = self.game.game_state.game_board.get_zone("kan_di")

        # Assertions for Time Phase logic
        # li_tian is fire. fire is beneficial (wood->fire) and harmful (water->fire). Harmful wins, so reward is 0.
        self.assertEqual(li_tian_zone.gold_reward, 0)
        # kan_di is water, which is neutral in this case. Penalty should be 0.
        self.assertEqual(kan_di_zone.gold_penalty, 0)

        # --- RESOLUTION PHASE ---
        initial_alice_gold = self.alice.gold
        initial_bob_gold = self.bob.gold

        self.game._execute_resolution_phase()

        # Assertions for Resolution Phase logic
        self.assertEqual(self.alice.gold, initial_alice_gold + li_tian_zone.gold_reward)
        self.assertEqual(self.bob.gold, initial_bob_gold - kan_di_zone.gold_penalty)

    def test_qimen_gate_trigger(self):
        """
        Tests if moving into a palace with a Qi Men gate correctly triggers its effect.
        """
        # Ju 1: Kan palace has 休门 (Rest Gate), which gives +10 health.
        self.game.game_state.ju_number = 1
        self.game._update_qimen_gates() # Force update gates

        # Manually move Bob to a Di zone in the Kan palace
        self.bob.position = "kan_di"
        initial_bob_health = self.bob.health

        # The gate effect is triggered at the end of the movement phase.
        # We call the new, specific method to avoid the random movement.
        self.game._trigger_gate_effects()

        #休门 (+10 health) should have been triggered and resolved.
        self.assertEqual(self.bob.health, initial_bob_health + 10)

if __name__ == '__main__':
    unittest.main()