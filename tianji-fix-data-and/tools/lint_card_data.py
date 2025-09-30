import json
import os
import sys
from typing import Any, Dict, List, Set

# --- Schema Definition (based on card_logic_schema.md v3.1) ---

# Allowed top-level keys in a card JSON
VALID_TOP_LEVEL_KEYS: Set[str] = {
    "id", "name", "symbol", "sequence", "pinyin", "strokes", "type",
    "core_mechanism", "effect", "triggers", "usage_limit", "metadata"
}

# Required top-level keys for every card
REQUIRED_TOP_LEVEL_KEYS: Set[str] = {"id", "name", "type"}

# Allowed card types
VALID_CARD_TYPES: Set[str] = {
    "basic", "function", "natal", "destiny", "stem", "branch", "celestial"
}

# Allowed action types
VALID_ACTIONS: Set[str] = {
    "GAIN_RESOURCE", "LOSE_RESOURCE", "PAY_COST", "DEAL_DAMAGE", "MOVE",
    "SWAP_POSITION", "APPLY_STATUS", "REMOVE_STATUS", "MODIFY_RULE", "CHOICE",
    "LOOKUP", "INTERRUPT", "COPY_EFFECT", "CREATE_ENTITY", "DESTROY_ENTITY",
    "EXECUTE_LATER", "TRIGGER_EVENT", "DISCARD_CARD",
    # 新增支持的动作类型（与 card_logic_schema.md v3.1 保持一致）
    "DRAW_CARD", "PROPOSE_ALLIANCE", "SKIP_PHASE", "SWAP_HAND_CARDS", "SWAP_RESOURCE", "SWAP_DISCARD_PILES", "MODIFY_RESOURCE", "TRANSFER_RESOURCE"
}

# Allowed parameters for each action (simplified for this linter)
# A more robust linter would have detailed checks for each
REQUIRED_ACTION_PARAMS: Dict[str, Set[str]] = {
    "GAIN_RESOURCE": {"target", "resource", "value"},
    "LOSE_RESOURCE": {"target", "resource", "value"},
    "PAY_COST": {"target", "resource", "value"},
    "DEAL_DAMAGE": {"target", "value"},
    "MOVE": {"target", "value"},
    "APPLY_STATUS": {"target", "status_id"},
    "CHOICE": {"target", "options"},
    "EXECUTE_LATER": {"delay", "effect"}
    # ... other actions would be defined here
}

# Allowed trigger conditions
VALID_TRIGGER_CONDITIONS: Set[str] = {
    "ON_BEING_TARGETED", "ON_PLAYER_ACTION", "ON_PHASE_START", "ON_RESOURCE_CHANGE"
}

# --- Linter Logic ---

def lint_card(card_data: Dict[str, Any], card_id: str) -> List[str]:
    """
    Validates a single card's data against the schema.
    Returns a list of error messages.
    """
    errors = []

    # 1. Check for required top-level keys
    for key in REQUIRED_TOP_LEVEL_KEYS:
        if key not in card_data:
            errors.append(f"Missing required top-level key: '{key}'")

    # 2. Check for unknown top-level keys
    for key in card_data:
        if key not in VALID_TOP_LEVEL_KEYS:
            errors.append(f"Unknown top-level key: '{key}'")

    # 3. Validate card type
    card_type = card_data.get('type')
    if card_type and card_type not in VALID_CARD_TYPES:
        errors.append(f"Invalid card type: '{card_type}'")

    # 4. Validate 'id' consistency
    if card_data.get('id') != card_id:
        errors.append(f"Card ID in file '{card_id}' does not match 'id' field in JSON: '{card_data.get('id')}'")

    # 5. Recursively validate effects and actions
    # This is a simplified check. A full implementation would be more deeply nested.
    if 'core_mechanism' in card_data and 'variants' in card_data['core_mechanism']:
        for variant, content in card_data['core_mechanism']['variants'].items():
            if 'effect' in content:
                errors.extend(_validate_effect_object(content['effect'], f"core_mechanism.variants.{variant}"))

    if 'effect' in card_data:
        errors.extend(_validate_effect_object(card_data['effect'], "effect"))

    return errors

def _validate_effect_object(effect: Dict[str, Any], path: str) -> List[str]:
    """Helper to validate an effect object."""
    errors = []
    if not isinstance(effect, dict):
        return [f"Effect at '{path}' is not a valid object."]

    if 'actions' in effect:
        if not isinstance(effect['actions'], list):
            errors.append(f"'{path}.actions' must be a list.")
        else:
            for i, action in enumerate(effect['actions']):
                errors.extend(_validate_action_object(action, f"{path}.actions[{i}]"))

    if 'cost' in effect:
        if not isinstance(effect['cost'], list):
            errors.append(f"'{path}.cost' must be a list.")
        else:
            for i, cost_item in enumerate(effect['cost']):
                 if not all(k in cost_item for k in ['resource', 'value']):
                     errors.append(f"Invalid cost item at '{path}.cost[{i}]'. Must contain 'resource' and 'value'.")

    return errors

def _validate_action_object(action: Dict[str, Any], path: str) -> List[str]:
    """Helper to validate an action object."""
    errors = []
    if not isinstance(action, dict):
        return [f"Action at '{path}' is not a valid object."]

    action_type = action.get('action')
    if not action_type:
        errors.append(f"Action at '{path}' is missing the 'action' key.")
    elif action_type not in VALID_ACTIONS:
        errors.append(f"Unknown action type '{action_type}' at '{path}'.")

    # Basic check for parameters
    if 'params' not in action:
        errors.append(f"Action at '{path}' is missing the 'params' key.")

    # Check for required params for known actions
    if action_type in REQUIRED_ACTION_PARAMS:
        missing_params = REQUIRED_ACTION_PARAMS[action_type] - set(action.get('params', {}).keys())
        if missing_params:
            errors.append(f"Action '{action_type}' at '{path}' is missing required params: {missing_params}")

    # --- High-level safety checks / engine contract checks ---
    params = action.get('params', {}) if isinstance(action.get('params', {}), dict) else {}

    # MODIFY_RULE must include scope and rollback info
    if action_type == 'MODIFY_RULE':
        scope = params.get('scope')
        if not scope:
            errors.append(f"MODIFY_RULE at '{path}' must include a 'scope' param (turn/phase/persistent).")
        else:
            if scope not in {'turn', 'phase', 'persistent'}:
                errors.append(f"MODIFY_RULE at '{path}' has invalid scope '{scope}'. Use one of turn/phase/persistent.")
        if not (params.get('rollback_condition') or params.get('duration')):
            errors.append(f"MODIFY_RULE at '{path}' should include 'duration' or 'rollback_condition' to allow safe rollback.")

    # EXECUTE_LATER should have expiry or max_turns to avoid dangling events
    if action_type == 'EXECUTE_LATER':
        if not (params.get('expiry_time') or params.get('max_turns') or params.get('delay')):
            errors.append(f"EXECUTE_LATER at '{path}' should include 'expiry_time', 'max_turns' or 'delay' to avoid dangling events.")
        # Recommend snapshot behavior (warning-level implemented as error to force explicitness)
        if not params.get('snapshot_args') and not params.get('late_resolve'):
            errors.append(f"EXECUTE_LATER at '{path}' should state 'snapshot_args' or 'late_resolve' to clarify resolution semantics.")

    # COPY_EFFECT should declare copy semantics when used
    if action_type == 'COPY_EFFECT':
        copy_sem = params.get('copy_semantics')
        if not copy_sem:
            errors.append(f"COPY_EFFECT at '{path}' must declare 'copy_semantics' (snapshot|reference|forbidden).")
        else:
            if copy_sem not in {'snapshot', 'reference', 'forbidden'}:
                errors.append(f"COPY_EFFECT at '{path}' has invalid copy_semantics '{copy_sem}'. Use snapshot|reference|forbidden.")

    # CREATE_ENTITY should bound creation to avoid infinite loops
    if action_type == 'CREATE_ENTITY':
        if not (params.get('max_instances') or params.get('create_stack_limit')):
            errors.append(f"CREATE_ENTITY at '{path}' should include 'max_instances' or 'create_stack_limit' to prevent runaway creation.")

    # SWAP_* operations must be atomic or declare fallback
    if action_type and action_type.startswith('SWAP'):
        if 'atomic' not in params and 'fallback_policy' not in params:
            errors.append(f"{action_type} at '{path}' must include 'atomic' boolean or 'fallback_policy' to avoid partial swaps.")

    return errors

def main():
    """
    Main execution function.
    Lints a specific file or all files in the assets/data/cards directory.
    """
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        if not os.path.exists(filepath):
            print(f"Error: File not found at '{filepath}'")
            sys.exit(1)
        files_to_lint = [filepath]
    else:
        print("No specific file provided. Searching for all card data files...")
        base_path = 'assets/data/cards'
        if not os.path.exists(base_path):
            print(f"Error: Directory '{base_path}' not found. Run generate_card_data.py first.")
            sys.exit(1)

        files_to_lint = []
        for root, _, files in os.walk(base_path):
            for file in files:
                if file.endswith('.json'):
                    files_to_lint.append(os.path.join(root, file))

    print(f"Found {len(files_to_lint)} JSON file(s) to lint.")
    total_errors = 0

    for filepath in files_to_lint:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            card_id = os.path.splitext(os.path.basename(filepath))[0]
            errors = lint_card(data, card_id)

            # Top-level usage_limit semantics check
            if 'usage_limit' in data:
                ul = data.get('usage_limit')
                if not isinstance(ul, dict):
                    errors.append(f"Top-level 'usage_limit' in {filepath} must be an object with 'reset_timing'.")
                else:
                    if not ul.get('reset_timing'):
                        errors.append(f"Top-level 'usage_limit' in {filepath} must include 'reset_timing' (e.g., end_of_turn).")

            if errors:
                print(f"\n--- Errors found in {filepath}:")
                for error in errors:
                    print(f"  - {error}")
                total_errors += len(errors)
            else:
                print(f"\n--- {filepath}: OK")

        except json.JSONDecodeError as e:
            print(f"\n--- Error decoding JSON in {filepath}:")
            print(f"  - {e}")
            total_errors += 1
        except Exception as e:
            print(f"\n--- An unexpected error occurred with {filepath}:")
            print(f"  - {e}")
            total_errors += 1

    if total_errors > 0:
        print(f"\nLinting complete. Found a total of {total_errors} error(s).")
        sys.exit(1)
    else:
        print("\nLinting complete. All files are valid.")
        sys.exit(0)

if __name__ == "__main__":
    main()