# src/qimen.py

"""
This module defines the data and logic for the Qi Men Dun Jia system,
including the distribution of the Eight Gates (八门) across the palaces
for each Ju (局) and the effects associated with each gate.
"""

# --- Gate Distribution Map (阳遁九局八门分布图) ---
# Maps Ju number -> Palace Name -> Gate ID
YANG_JU_GATE_DISTRIBUTION = {
    1: {"kan": "休", "gen": "生", "zhen": "伤", "xun": "杜", "li": "景", "kun": "死", "dui": "惊", "qian": "开"},
    2: {"kan": "死", "gen": "惊", "zhen": "开", "xun": "休", "li": "生", "kun": "伤", "dui": "杜", "qian": "景"},
    3: {"kan": "景", "gen": "死", "zhen": "惊", "xun": "开", "li": "休", "kun": "生", "dui": "伤", "qian": "杜"},
    4: {"kan": "杜", "gen": "景", "zhen": "死", "xun": "惊", "li": "开", "kun": "休", "dui": "生", "qian": "伤"},
    5: {"kan": "伤", "gen": "杜", "zhen": "景", "xun": "死", "li": "惊", "kun": "开", "dui": "休", "qian": "生"},
    6: {"kan": "开", "gen": "休", "zhen": "生", "xun": "伤", "li": "杜", "kun": "景", "dui": "死", "qian": "惊"},
    7: {"kan": "生", "gen": "伤", "zhen": "杜", "xun": "景", "li": "死", "kun": "惊", "dui": "开", "qian": "休"},
    8: {"kan": "惊", "gen": "开", "zhen": "休", "xun": "生", "li": "伤", "kun": "杜", "dui": "景", "qian": "死"},
    9: {"kan": "伤", "gen": "杜", "zhen": "景", "xun": "死", "li": "惊", "kun": "开", "dui": "休", "qian": "生"},
}

# --- Gate Effects (八门效果) ---
# Defines the effect triggered when a player ends their movement in a palace with a specific gate.

GATE_EFFECTS = {
    # 吉门 (Auspicious Gates)
    "开": {
        "name": "开门 (Open Gate)",
        "effect": {
            "actions": [
                {"action": "GAIN_RESOURCE", "params": {"target": "SELF", "resource": "gold", "value": 5}},
                {"action": "DRAW_CARD", "params": {"target": "SELF", "deck": "function", "count": 1}}
            ]
        }
    },
    "休": {
        "name": "休门 (Rest Gate)",
        "effect": {
            "actions": [
                {"action": "GAIN_RESOURCE", "params": {"target": "SELF", "resource": "health", "value": 10}},
                {"action": "LOSE_RESOURCE", "params": {"target": "SELF", "resource": "yin_yang", "value": 1}} # -1 Yin
            ]
        }
    },
    "生": {
        "name": "生门 (Life Gate)",
        "effect": {
            "actions": [{
                "action": "CHOICE",
                "params": {
                    "target": "SELF",
                    "options": [
                        {"description": "获得10金币", "effect": {"actions": [{"action": "GAIN_RESOURCE", "params": {"target": "SELF", "resource": "gold", "value": 10}}]}},
                        {"description": "回复15生命值", "effect": {"actions": [{"action": "GAIN_RESOURCE", "params": {"target": "SELF", "resource": "health", "value": 15}}]}}
                    ]
                }
            },
            {"action": "LOSE_RESOURCE", "params": {"target": "SELF", "resource": "yin_yang", "value": 1}} # -1 Yin
            ]
        }
    },
    # 中平门 (Neutral Gates)
    "景": {
        "name": "景门 (View Gate)",
        "effect": {
            "actions": [
                {"action": "LOOKUP", "params": {"target": "OPPONENT_CHOICE_SINGLE", "info_type": "hand_cards"}}
            ]
        }
    },
    "杜": {
        "name": "杜门 (Delusion Gate)",
        "effect": {
             "actions": [
                {"action": "APPLY_STATUS", "params": {"target": "SELF", "status_id": "GATE_DU_IMMUNITY", "duration": 1}}
             ]
        }
    },
    # 凶门 (Inauspicious Gates)
    "惊": {
        "name": "惊门 (Fear Gate)",
        "effect": {
            "actions": [
                {"action": "DISCARD_CARD", "params": {"target": "SELF", "deck": "function", "count": 1}}
            ]
        }
    },
    "伤": {
        "name": "伤门 (Harm Gate)",
        "effect": {
            "actions": [
                {"action": "LOSE_RESOURCE", "params": {"target": "SELF", "resource": "health", "value": 10}}
            ]
        }
    },
    "死": {
        "name": "死门 (Death Gate)",
        "effect": {
            "actions": [
                {"action": "LOSE_RESOURCE", "params": {"target": "SELF", "resource": "gold", "value": 10}}
            ]
        }
    },
}

def get_gate_layout_for_ju(ju_number: int) -> dict:
    """Returns the gate distribution for a given Ju number."""
    # The distribution cycles every 9 Ju.
    ju_key = ((ju_number - 1) % 9) + 1
    return YANG_JU_GATE_DISTRIBUTION.get(ju_key, {})

def get_effect_for_gate(gate_name: str) -> dict | None:
    """Returns the effect JSON for a given gate name."""
    return GATE_EFFECTS.get(gate_name, {}).get("effect")