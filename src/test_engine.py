import unittest
import logging
from unittest.mock import MagicMock

# Adjust imports to work with the project structure
from src.game_state import GameState
from src.player import Player
from src.effect_engine import EffectEngine
from src.card import Card

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
        costly_effect = {
            "cost": [{"resource": "gold", "value": 10}],
            "actions": [{"action": "DEAL_DAMAGE", "params": {"target": "OPPONENT_CHOICE_SINGLE", "value": 10}}]
        }

        # P1 can afford it
        initial_p1_gold = self.p1.gold
        initial_p2_health = self.p2.health
        self.engine.queue_effect(costly_effect, self.p1)
        self.engine.resolve_effects()
        self.assertEqual(self.p1.gold, initial_p1_gold - 10)
        self.assertEqual(self.p2.health, initial_p2_health - 10)

        # P2 cannot afford it
        initial_p2_gold = self.p2.gold
        initial_p3_health = self.p3.health
        self.engine.queue_effect(costly_effect, self.p2)
        self.engine.resolve_effects()
        self.assertEqual(self.p2.gold, initial_p2_gold) # Gold should not change
        self.assertEqual(self.p3.health, initial_p3_health) # Health should not change

    def test_permanent_status(self):
        """Verify that permanent statuses do not expire."""
        perm_status_effect = {
            "actions": [{
                "action": "APPLY_STATUS",
                "params": {"target": "SELF", "status_id": "PERM_SHIELD", "is_permanent": True}
            }]
        }

        self.engine.queue_effect(perm_status_effect, self.p1)
        self.engine.resolve_effects()
        self.assertIn("PERM_SHIELD", [s['status_id'] for s in self.p1.status_effects])

        self.p1.tick_statuses()
        self.p1.tick_statuses()

        self.assertIn("PERM_SHIELD", [s['status_id'] for s in self.p1.status_effects])

    def test_targeting_same_zone(self):
        """Verify targeting players in the same zone."""
        zone_effect = {
            "actions": [{
                "action": "LOSE_RESOURCE",
                "params": {"target": "OTHER_PLAYERS_IN_SAME_ZONE", "resource": "gold", "value": 3}
            }]
        }

        initial_p2_gold = self.p2.gold
        initial_p3_gold = self.p3.gold

        self.engine.queue_effect(zone_effect, self.p1)
        self.engine.resolve_effects()

        self.assertEqual(self.p2.gold, initial_p2_gold - 3)
        self.assertEqual(self.p3.gold, initial_p3_gold)

    def test_priority_system(self):
        """Verify that high-priority effects (like CANCEL) execute before low-priority ones."""
        # P1 tries to deal damage to P2 (low priority)
        damage_effect = {
            "actions": [{"action": "DEAL_DAMAGE", "params": {"target": "PLAYER_CHOICE_ANY", "value": 10}}]
        }
        # P3 plays a cancel effect (high priority)
        cancel_effect = {
            "actions": [{"action": "INTERRUPT", "params": {"interrupt_type": "CANCEL"}}]
        }

        initial_p2_health = self.p2.health

        # Queue effects in a non-priority order
        self.engine.queue_effect(damage_effect, self.p1)
        self.engine.queue_effect(cancel_effect, self.p3)

        self.engine.resolve_effects()

        # The cancel effect should have run first, preventing the damage.
        self.assertEqual(self.p2.health, initial_p2_health)

    def test_copy_effect_with_queue(self):
        """Verify COPY_EFFECT works with the new queueing system."""
        original_effect = {
            "actions": [{"action": "GAIN_RESOURCE", "params": {"target": "SELF", "resource": "gold", "value": 20}}]
        }
        copy_cat_effect = {
            "actions": [{"action": "COPY_EFFECT", "params": {"target": "SELF"}}]
        }

        initial_p1_gold = self.p1.gold
        initial_p2_gold = self.p2.gold

        # P1 queues the original effect, P2 queues the copy effect
        self.engine.queue_effect(original_effect, self.p1)
        self.engine.queue_effect(copy_cat_effect, self.p2)

        self.engine.resolve_effects()

        # Both effects should have resolved. P1 gets gold from the original effect.
        self.assertEqual(self.p1.gold, initial_p1_gold + 20)
        # P2 copies the effect and should also get gold.
        self.assertEqual(self.p2.gold, initial_p2_gold + 20)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    unittest.main()