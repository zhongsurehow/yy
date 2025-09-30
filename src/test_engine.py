import unittest
from unittest.mock import MagicMock

# Adjust imports to work with the project structure
from .game_state import GameState
from .player import Player
from .effect_engine import EffectEngine
from .card import Card

class TestEffectEngine(unittest.TestCase):

    def setUp(self):
        """Set up a fresh game state for each test."""
        self.gs = GameState()
        self.p1 = Player(player_id="p1", name="Alice", gold=20, health=100, position="A1")
        self.p2 = Player(player_id="p2", name="Bob", gold=5, health=100, position="A1")
        self.p3 = Player(player_id="p3", name="Charlie", gold=50, health=100, position="B2")
        self.gs.players = [self.p1, self.p2, self.p3]
        self.engine = EffectEngine(self.gs)

    def test_cost_check(self):
        """Verify that a player cannot use an effect they cannot afford."""
        print("\n--- Running Test: test_cost_check ---")
        costly_effect = {
            "cost": [{"resource": "gold", "value": 10}],
            "actions": [{"action": "DEAL_DAMAGE", "params": {"target": "OPPONENT_CHOICE_SINGLE", "value": 10}}]
        }

        # P1 can afford it
        initial_p1_gold = self.p1.gold
        initial_p2_health = self.p2.health
        self.engine.execute_effect(costly_effect, self.p1)
        self.assertEqual(self.p1.gold, initial_p1_gold - 10)
        self.assertEqual(self.p2.health, initial_p2_health - 10)
        print("  - PASSED: Alice paid the cost and the effect executed.")

        # P2 cannot afford it
        initial_p2_gold = self.p2.gold
        initial_p3_health = self.p3.health
        self.engine.execute_effect(costly_effect, self.p2)
        self.assertEqual(self.p2.gold, initial_p2_gold) # Gold should not change
        self.assertEqual(self.p3.health, initial_p3_health) # Health should not change
        print("  - PASSED: Bob could not pay, so the effect was aborted.")

    def test_permanent_status(self):
        """Verify that permanent statuses do not expire."""
        print("\n--- Running Test: test_permanent_status ---")
        perm_status_effect = {
            "actions": [{
                "action": "APPLY_STATUS",
                "params": {"target": "SELF", "status_id": "PERM_SHIELD", "is_permanent": True}
            }]
        }

        self.engine.execute_effect(perm_status_effect, self.p1)
        self.assertIn("PERM_SHIELD", [s['status_id'] for s in self.p1.status_effects])

        # Tick statuses multiple times
        self.p1.tick_statuses()
        self.p1.tick_statuses()

        self.assertIn("PERM_SHIELD", [s['status_id'] for s in self.p1.status_effects])
        print("  - PASSED: Permanent status correctly persisted after ticking.")

    def test_targeting_same_zone(self):
        """Verify targeting players in the same zone."""
        print("\n--- Running Test: test_targeting_same_zone ---")
        zone_effect = {
            "actions": [{
                "action": "LOSE_RESOURCE",
                "params": {"target": "OTHER_PLAYERS_IN_SAME_ZONE", "resource": "gold", "value": 3}
            }]
        }

        initial_p2_gold = self.p2.gold
        initial_p3_gold = self.p3.gold

        self.engine.execute_effect(zone_effect, self.p1)

        # Bob is in the same zone as Alice, so he should be affected
        self.assertEqual(self.p2.gold, initial_p2_gold - 3)
        # Charlie is in a different zone, so he should be unaffected
        self.assertEqual(self.p3.gold, initial_p3_gold)
        print("  - PASSED: Correctly targeted player in the same zone and ignored player in a different zone.")

    def test_copy_effect(self):
        """Verify that COPY_EFFECT works as intended."""
        print("\n--- Running Test: test_copy_effect ---")
        original_effect = {
            "actions": [{"action": "GAIN_RESOURCE", "params": {"target": "SELF", "resource": "gold", "value": 20}}]
        }
        copy_cat_effect = {
            "actions": [{"action": "COPY_EFFECT", "params": {"target": "SELF"}}]
        }

        # P1 uses the original effect
        initial_p1_gold = self.p1.gold
        self.engine.execute_effect(original_effect, self.p1)
        self.assertEqual(self.p1.gold, initial_p1_gold + 20)
        print("  - Verified: Original effect grants 20 gold.")

        # Now, P2 copies the effect
        initial_p2_gold = self.p2.gold
        self.engine.execute_effect(copy_cat_effect, self.p2)
        # P2 should gain 20 gold because it copies the effect, and the target is SELF (relative to P2)
        self.assertEqual(self.p2.gold, initial_p2_gold + 20)
        print("  - PASSED: Bob successfully copied the effect and gained gold.")

if __name__ == '__main__':
    # This allows running the test script directly.
    # To run from the root directory: python -m src.test_engine
    unittest.main()