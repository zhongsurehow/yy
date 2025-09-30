import random
import logging
import math
from pathlib import Path
from typing import List

from .game_loader import GameLoader
from .game_state import GameState
from .player import Player
from .card import Card
from .effect_engine import EffectEngine
from . import five_elements as fe
from . import qimen as qm

class Game:
    """Orchestrates the setup and execution of the game."""

    def __init__(self, player_names: List[str], assets_path_str: str):
        self.game_state = GameState()
        self.player_names = player_names
        self.loader = GameLoader(Path(assets_path_str))
        self.effect_engine = EffectEngine(self.game_state)

    def setup(self, test_cards: List[str] = None):
        """Initializes the game state, with an option to inject specific test cards."""
        logging.info("--- Setting up a new game of Tianji Bian ---")

        all_decks = self.loader.load_all_cards()
        self.game_state.basic_deck = all_decks.get("basic", [])
        self.game_state.celestial_stem_deck = all_decks.get("celestial_stem", [])
        self.game_state.terrestrial_branch_deck = all_decks.get("terrestrial_branch", [])

        random.shuffle(self.game_state.basic_deck)
        random.shuffle(self.game_state.celestial_stem_deck)
        random.shuffle(self.game_state.terrestrial_branch_deck)

        for i, name in enumerate(self.player_names):
            self.game_state.players.append(Player(player_id=str(i + 1), name=name))

        # Set up the game fund based on player count
        self.game_state.game_fund = len(self.game_state.players) * 100
        logging.info(f"Game fund initialized to: {self.game_state.game_fund}")

        # Set initial Qi Men gate layout
        self._update_qimen_gates()

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

        logging.info("Game setup complete.")

    def run_game(self, num_rounds: int = 1):
        """Runs the main game loop for a specified number of rounds."""
        logging.info(f"--- Starting Game Run ({num_rounds} round(s)) ---")

        for i in range(1, num_rounds + 1):
            self.run_round(i)

        logging.info("--- Game Run Finished ---")
        logging.info("Final Player States:")
        for player in self.game_state.players:
            logging.info(f"  - {player}")

    def run_round(self, round_number: int):
        """Executes all phases for a single round of the game."""
        self.game_state.current_turn = round_number
        logging.info(f"***** Round {self.game_state.current_turn} *****")

        self._execute_time_phase()
        self._execute_placement_phase()
        self._execute_movement_phase()
        self._execute_interpretation_phase()
        self._execute_resolution_phase()
        self._execute_upkeep_phase()

    def _execute_time_phase(self):
        self.game_state.set_phase("TIME")
        logging.info("--- Phase: TIME ---")

        # Update Qi Men gates based on the current Ju number
        self._update_qimen_gates()

        # 1. Draw new stem and branch cards
        # (Assuming decks are populated and will be reshuffled if empty in a full implementation)
        if not self.game_state.celestial_stem_deck or not self.game_state.terrestrial_branch_deck:
            logging.error("Celestial Stem or Terrestrial Branch deck is empty. Cannot proceed.")
            return

        self.game_state.current_celestial_stem = self.game_state.celestial_stem_deck.pop()
        self.game_state.current_terrestrial_branch = self.game_state.terrestrial_branch_deck.pop()
        logging.info(f"New Gan-Zhi: {self.game_state.current_celestial_stem.name}, {self.game_state.current_terrestrial_branch.name}")

        # 2. Determine beneficial and harmful elements
        stem_element = fe.get_element_for_stem(self.game_state.current_celestial_stem.card_id.split('_')[-1])
        branch_element = fe.get_element_for_branch(self.game_state.current_terrestrial_branch.card_id.split('_')[-1])

        beneficial_elements = {fe.get_generated_element(stem_element), fe.get_generated_element(branch_element)}
        harmful_elements = {fe.get_overcome_element(stem_element), fe.get_overcome_element(branch_element)}
        logging.info(f"Beneficial Elements: {beneficial_elements}, Harmful Elements: {harmful_elements}")

        # 3. Update all zones on the board
        for zone in self.game_state.game_board.zones.values():
            # Reset previous values
            zone.gold_reward = 0
            zone.gold_penalty = 0

            is_beneficial = zone.five_element in beneficial_elements
            is_harmful = zone.five_element in harmful_elements

            if zone.department == 'tian':
                if is_beneficial:
                    zone.gold_reward += 5
                if is_harmful: # Stagnation rule overrides reward
                    zone.gold_reward = 0

            elif zone.department == 'di':
                if is_beneficial:
                    zone.gold_penalty -= 3
                if is_harmful:
                    zone.gold_penalty += 5
                zone.gold_penalty = max(0, zone.gold_penalty) # Cannot be negative

    def _execute_placement_phase(self):
        self.game_state.set_phase("PLACEMENT")
        for player in self.game_state.players:
            # Simplified: players just play the first basic card they have.
            card_to_play = next((c for c in player.hand if c.card_type == 'basic'), None)
            if card_to_play:
                player.play_card(card_to_play.card_id)
                logging.info(f"{player.name} has placed card {card_to_play.name} face down.")

    def _execute_movement_phase(self):
        self.game_state.set_phase("MOVEMENT")
        logging.info("--- Phase: MOVEMENT ---")

        # Simplified: players move one by one in the current player order
        for player in self.game_state.players:
            # In a full game, we'd check if the player can move (e.g., not stunned)
            valid_moves = self.game_state.game_board.get_valid_moves(player.position)
            if not valid_moves:
                logging.info(f"{player.name} at {player.position} has no valid moves.")
                continue

            # Simplified: auto-select the first valid move
            destination = valid_moves[0]
            original_position = player.position
            player.position = destination
            logging.info(f"{player.name} moves from {original_position} to {destination}.")

            # Check for "Lun Dao"
            other_players_in_zone = [
                p for p in self.game_state.players
                if p.position == destination and p.player_id != player.player_id
            ]

            if other_players_in_zone:
                defender = other_players_in_zone[0] # Simplified: challenge the first player found
                self._trigger_lun_dao(player, defender)

        # After all movements are complete, trigger Qi Men gate effects
        logging.info("--- Triggering Qi Men Gate Effects ---")
        for player in self.game_state.players:
            palace = self.game_state.game_board.get_palace_for_zone(player.position)
            if not palace:
                continue

            gate_name = self.game_state.game_board.qimen_gates.get(palace)
            if gate_name:
                logging.info(f"{player.name} is in {palace.upper()} palace, triggering gate: {gate_name}")
                gate_effect = qm.get_effect_for_gate(gate_name)
                if gate_effect:
                    self.effect_engine.queue_effect(gate_effect, player)

        # Resolve any queued gate effects
        self.effect_engine.resolve_effects()

    def _trigger_lun_dao(self, challenger: Player, defender: Player):
        logging.info(f"--- Lun Dao event triggered between {challenger.name} and {defender.name}! ---")

        # Simplified: each player chooses their first basic card from hand
        challenger_card = next((c for c in challenger.hand if c.card_type == 'basic'), None)
        defender_card = next((c for c in defender.hand if c.card_type == 'basic'), None)

        if not challenger_card or not defender_card:
            logging.warning("Lun Dao cannot proceed, one or both players lack a basic card in hand.")
            return

        logging.info(f"{challenger.name} reveals {challenger_card.name} ({challenger_card.strokes} strokes).")
        logging.info(f"{defender.name} reveals {defender_card.name} ({defender_card.strokes} strokes).")

        winner, loser = (None, None)
        if challenger_card.strokes < defender_card.strokes:
            winner, loser = challenger, defender
        elif defender_card.strokes < challenger_card.strokes:
            winner, loser = defender, challenger

        if winner:
            logging.info(f"{winner.name} wins the Lun Dao!")
            # Direct resource change as a simplification
            amount = min(loser.gold, 5) # Cannot take more than the loser has
            loser.change_resource("gold", -amount)
            winner.change_resource("gold", amount)
            logging.info(f"{winner.name} takes {amount} gold from {loser.name}.")
        else:
            logging.info("The Lun Dao is a draw.")

        # Discard the used cards
        challenger.hand.remove(challenger_card)
        challenger.discard_pile.append(challenger_card)
        defender.hand.remove(defender_card)
        defender.discard_pile.append(defender_card)
        logging.info("Cards used in Lun Dao have been discarded.")

    def _update_qimen_gates(self):
        """Updates the gate layout on the board based on the current Ju number."""
        ju_number = self.game_state.ju_number
        gate_layout = qm.get_gate_layout_for_ju(ju_number)
        if gate_layout:
            self.game_state.game_board.qimen_gates = gate_layout
            logging.info(f"Qi Men gates updated for Ju {ju_number}: {gate_layout}")
        else:
            logging.error(f"Could not find gate layout for Ju {ju_number}")

    def _execute_interpretation_phase(self):
        self.game_state.set_phase("INTERPRETATION")
        # The interpretation order should follow Luo Shu numbers (1-9), then department (Tian->Ren->Di)
        # For now, we'll use a simplified player order.
        logging.info("Players reveal and queue their card effects.")
        for player in self.game_state.players:
            if player.played_card:
                card = player.played_card
                logging.info(f"{player.name} (at {player.position}) reveals {card.name}!")

                player_zone = self.game_state.game_board.get_zone(player.position)
                if not player_zone:
                    logging.warning(f"Player {player.name} is at an invalid position {player.position}")
                    continue

                variant_key = player_zone.department
                variant_effect = card.core_mechanism.get("variants", {}).get(variant_key, {}).get("effect")

                effect_to_queue = variant_effect if variant_effect else card.effect

                if effect_to_queue:
                    self.effect_engine.queue_effect(effect_to_queue, player)
                else:
                    logging.warning(f"Card {card.name} has no valid effect for department '{variant_key}' or a default effect.")

        # After all effects are queued, resolve them based on priority
        self.effect_engine.resolve_effects()

    def _execute_resolution_phase(self):
        self.game_state.set_phase("RESOLUTION")
        logging.info("--- Phase: RESOLUTION ---")
        logging.info("Calculating Tian Bu rewards and Di Bu penalties...")

        for player in self.game_state.players:
            zone = self.game_state.game_board.get_zone(player.position)
            if not zone:
                continue

            # Tian Bu Reward
            if zone.department == 'tian':
                reward = zone.gold_reward
                if reward > 0:
                    player.change_resource("gold", reward)
                    self.game_state.game_fund -= reward
                    logging.info(f"{player.name} in Tian Bu gains {reward} gold. Fund is now {self.game_state.game_fund}.")

            # Di Bu Penalty
            elif zone.department == 'di':
                penalty = zone.gold_penalty
                if penalty > 0:
                    paid_amount = min(player.gold, penalty)
                    player.change_resource("gold", -paid_amount)
                    self.game_state.game_fund += paid_amount
                    logging.info(f"{player.name} in Di Bu pays {paid_amount} gold penalty. Fund is now {self.game_state.game_fund}.")

            # Zhong Gong Penalty
            elif zone.department == 'zhong':
                penalty = math.ceil(player.gold * 0.10)
                player.change_resource("gold", -penalty)
                self.game_state.game_fund += penalty
                logging.info(f"{player.name} in Zhong Gong pays {penalty} gold (10%) penalty. Fund is now {self.game_state.game_fund}.")

    def _execute_upkeep_phase(self):
        self.game_state.set_phase("UPKEEP")
        logging.info("Processing upkeep...")
        for player in self.game_state.players:
            player.tick_statuses()
            player.discard_played_card()
        logging.info("Players discard played cards.")