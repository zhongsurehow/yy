from typing import Dict, Any, List

# Forward-declare GameState to avoid circular import
if False:
    from game_state import GameState
    from player import Player

class EffectEngine:
    """Parses and executes card effect actions."""

    def __init__(self, game_state: 'GameState'):
        self.game_state = game_state

    def execute_effect(self, effect: Dict[str, Any], source_player: 'Player'):
        """Executes a full effect block, including costs, conditions, and actions."""
        actions = effect.get("actions", [])
        for action_data in actions:
            self.execute_action(action_data, source_player)

    def execute_action(self, action_data: Dict[str, Any], source_player: 'Player'):
        """Executes a single action from an effect block."""
        action_type = action_data.get("action")
        params = action_data.get("params", {})

        handler = getattr(self, f"_handle_{action_type.lower()}", self._handle_unimplemented)

        print(f"    - Executing Action: {action_type} for {source_player.name}")
        handler(params, source_player)

    def _get_targets(self, target_str: str, source_player: 'Player') -> List['Player']:
        """Resolves a target string into a list of Player objects."""
        if target_str == "SELF":
            return [source_player]
        elif target_str == "OPPONENT_CHOICE_SINGLE":
            opponents = [p for p in self.game_state.players if p != source_player]
            return [opponents[0]] if opponents else []
        elif target_str == "ALL_PLAYERS":
            return self.game_state.players

        print(f"    - WARNING: Target type '{target_str}' not fully implemented. Defaulting to SELF.")
        return [source_player]

    def _resolve_value(self, value: Any, source_player: 'Player') -> int:
        """Resolves a value that can be an integer or a dynamic dictionary."""
        if isinstance(value, int):
            return value
        if isinstance(value, dict):
            op = value.get("op")
            if op == "COUNT":
                target_str = value.get("target")
                return len(self._get_targets(target_str, source_player))
            # Other ops like 'SUM', 'PLAYER_RESOURCE' would go here
            else:
                print(f"    - WARNING: Dynamic value operator '{op}' not implemented. Defaulting to 0.")
                return 0
        return 0 # Default for unexpected types

    # --- Resource Handlers ---
    def _handle_gain_resource(self, params: Dict[str, Any], source_player: 'Player'):
        targets = self._get_targets(params.get("target", "SELF"), source_player)
        value = self._resolve_value(params.get("value"), source_player)
        resource = params.get("resource")

        for target in targets:
            target.change_resource(resource, value)
            print(f"      - Target: {target.name}, Resource: {resource}, Value: +{value}")

    def _handle_lose_resource(self, params: Dict[str, Any], source_player: 'Player'):
        targets = self._get_targets(params.get("target", "SELF"), source_player)
        value = self._resolve_value(params.get("value"), source_player)
        resource = params.get("resource")

        for target in targets:
            target.change_resource(resource, -value)
            print(f"      - Target: {target.name}, Resource: {resource}, Value: -{value}")

    def _handle_deal_damage(self, params: Dict[str, Any], source_player: 'Player'):
        targets = self._get_targets(params.get("target", "OPPONENT_CHOICE_SINGLE"), source_player)
        value = self._resolve_value(params.get("value"), source_player)

        for target in targets:
            target.change_resource("health", -value)
            print(f"      - Target: {target.name} takes {value} damage!")

    # --- Status Handlers ---
    def _handle_apply_status(self, params: Dict[str, Any], source_player: 'Player'):
        targets = self._get_targets(params.get("target"), source_player)
        status_to_apply = {
            "status_id": params.get("status_id"),
            "duration": params.get("duration", 1),
            "value": params.get("value"),
            "is_permanent": params.get("is_permanent", False)
        }
        for target in targets:
            target.add_status(status_to_apply.copy())

    def _handle_remove_status(self, params: Dict[str, Any], source_player: 'Player'):
        targets = self._get_targets(params.get("target"), source_player)
        status_id_to_remove = params.get("status_id")
        for target in targets:
            target.remove_status(status_id_to_remove)

    # --- Other Handlers ---
    def _handle_move(self, params: Dict[str, Any], source_player: 'Player'):
        print(f"      - Movement action triggered. (Logic to be implemented)")
        source_player.has_moved = True

    def _handle_choice(self, params: Dict[str, Any], source_player: 'Player'):
        options = params.get("options", [])
        if options:
            print("    - Player has a choice. For prototype, auto-selecting first valid option.")
            first_option = options[0]
            if "effect" in first_option:
                self.execute_effect(first_option["effect"], source_player)
        else:
            print("    - WARNING: CHOICE action has no options.")

    def _handle_modify_rule(self, params: Dict[str, Any], source_player: 'Player'):
        print(f"      - Rule modification triggered: {params.get('rule_id')}. (Logic to be implemented)")

    def _handle_unimplemented(self, params: Dict[str, Any], source_player: 'Player', action_type: str = "Unknown"):
        print(f"    - WARNING: Action '{action_type}' is not yet implemented.")