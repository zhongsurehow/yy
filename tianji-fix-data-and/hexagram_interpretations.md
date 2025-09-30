**版本: 3.0 (Data-Driven Update)**
**说明:** 本文档是游戏卡牌逻辑的 **单一事实来源 (Single Source of Truth)**。每张卡牌的描述下方都包含一个 `json` 代码块，该代码块定义了卡牌在游戏引擎中的确切行为。

**开发者指南:**
- **要修改卡牌逻辑，请直接修改本文档中的 `json` 代码块。**
- **修改完成后，请运行 `python tools/generate_card_data.py` 脚本。**
- 该脚本会自动解析本文档，提取所有 `json` 数据，并重新生成位于 `assets/data/cards/` 目录下的所有游戏数据文件。
- **请勿手动编辑 `assets/data/cards/` 目录下的任何 `.json` 文件**，因为它们会在脚本运行时被覆盖。

---

### **第一卦：《乾》 ☰☰ - 天**
**核心机制：【天道酬勤】**
- **效果：** 你可以选择是否发动【天道酬勤】。若发动，你必须**支付** 10 金币和 5 生命值作为**代价**。成功支付后，在本轮的【解读阶段】，你所有效果造成的**伤害**、获得的**金币**和恢复的**生命值**，其基础数值翻倍。
- **爻辞变量：**
  - **地部 (蓄力):** 发动【天道酬勤】时，支付的**代价**减半（5金币，3生命值，向上取整）。
  - **人部 (精进):** 除了核心效果，你还可以立即执行一次额外移动（1格）。
  - **天部 (君威):** 你可以指定一名**正式盟友**，使其也获得【天道酬勤】状态，持续一轮。作为此效果的一部分，在【归整阶段】的“回合结束时效果结算”步骤，你必须弃掉一张手牌。

```json
{
  "id": "basic_01_qian",
  "name": "乾",
  "symbol": "☰☰",
  "sequence": 1,
  "pinyin": "qian",
  "strokes": 12,
  "type": "basic",
  "core_mechanism": {
    "name": "天道酬勤",
    "description": "支付10金币和5生命值，在本轮的【解读阶段】，你爻辞效果中所有正向收益（获得金币、恢复生命、造成伤害）的数值翻倍。",
    "variants": {
      "di": {
        "name": "蓄力",
        "description": "你在【地部】发动【天道酬勤】时，支付的成本减半（只需5金币和3生命值）。",
        "effect": {
          "actions": [
            {
              "action": "CHOICE",
              "params": {
                "target": "SELF",
                "options": [
                  {
                    "description": "发动【天道酬勤】",
                    "cost": [
                      { "resource": "gold", "value": 5 },
                      { "resource": "health", "value": 3 }
                    ],
                    "effect": {
                      "actions": [
                        {
                          "action": "APPLY_STATUS",
                          "params": { "target": "SELF", "status_id": "POSITIVE_GAIN_DOUBLED", "duration": 1 }
                        }
                      ]
                    }
                  },
                  { "description": "不发动" }
                ]
              }
            }
          ]
        }
      },
      "ren": {
        "name": "精进",
        "description": "你在【人部】发动【天道酬勤】时，除了收益翻倍，你还可以立即额外移动一格。",
        "effect": {
          "actions": [
            {
              "action": "CHOICE",
              "params": {
                "target": "SELF",
                "options": [
                  {
                    "description": "发动【天道酬勤】并移动",
                    "cost": [
                      { "resource": "gold", "value": 10 },
                      { "resource": "health", "value": 5 }
                    ],
                    "effect": {
                      "actions": [
                        {
                          "action": "APPLY_STATUS",
                          "params": { "target": "SELF", "status_id": "POSITIVE_GAIN_DOUBLED", "duration": 1 }
                        },
                        {
                          "action": "MOVE",
                          "params": { "target": "SELF", "value": 1, "move_type": "NORMAL" }
                        }
                      ]
                    }
                  },
                  { "description": "不发动" }
                ]
              }
            }
          ]
        }
      },
      "tian": {
        "name": "君威",
        "description": "你在【天部】发动【天道酬勤】时，你可以指定一名盟友，使其也获得本轮收益翻倍的效果。",
        "effect": {
          "actions": [
            {
              "action": "CHOICE",
              "params": {
                "target": "SELF",
                "options": [
                  {
                    "description": "为自己和盟友发动【天道酬勤】",
                    "cost": [
                      { "resource": "gold", "value": 10 },
                      { "resource": "health", "value": 5 }
                    ],
                    "effect": {
                      "actions": [
                        {
                          "action": "APPLY_STATUS",
                          "params": { "target": "SELF", "status_id": "POSITIVE_GAIN_DOUBLED", "duration": 1 }
                        },
                        {
                          "action": "APPLY_STATUS",
                          "params": { "target": "ALLY_FORMAL_SINGLE", "status_id": "POSITIVE_GAIN_DOUBLED", "duration": 1 }
                        },
                        {
                          "action": "EXECUTE_LATER",
                          "params": {
                            "delay": "END_OF_TURN",
                            "expiry_time": "1 ROUND",
                            "effect": {
                              "actions": [
                                { "action": "DISCARD_CARD", "params": { "target": "SELF", "count": 1 } }
                              ]
                            }
                          }
                        }
                      ]
                    }
                  },
                  { "description": "不发动" }
                ]
              }
            }
          ]
        }
      }
    }
  }
}
```

---
### **第二卦：《坤》 ☷☷ - 地**
**核心机制：【厚德载物】**
- **效果：** 若你在本轮的【移动阶段】未进行移动，则在【解读阶段】发动此效果时，你可以选择**取消**你爻辞效果中所有负面部分（如支付代价、承受伤害等），只执行其正面部分。
- **爻辞变量：**
  - **地部 (固守):** 你额外获得 **【IMMUNE_COMBAT_DAMAGE (1)】** 状态（免疫下一次战斗伤害）。
  - **人部 (收敛):** 你可以改为**复制**本轮在你之前**上一位行动的玩家**已解读的**基础**爻辞效果（不含任何功能牌或状态修正）。你**必须支付**其原始的**代价**，但可以取消后续的其他负面部分（如生命值损失、弃牌等）。
  - **天部 (滋养):** 你可以将【厚德载物】的**目标**从“你自己”变为一名**正式盟友**。

```json
{
  "id": "basic_02_kun",
  "name": "坤",
  "symbol": "☷☷",
  "sequence": 2,
  "pinyin": "kun",
  "strokes": 6,
  "type": "basic",
  "core_mechanism": {
    "name": "厚德载物",
    "description": "若你本轮未移动，你可以选择取消你下个爻辞效果中的所有负面部分，只执行其正面部分。",
    "variants": {
      "di": {
        "name": "固守",
        "description": "若你本轮未移动，你获得【厚德载物】效果，并额外获得【免疫下一次战斗伤害】。",
        "effect": {
          "condition": { "op": "PLAYER_HAS_FLAG", "params": { "flag": "HAS_NOT_MOVED_THIS_TURN" } },
          "actions": [
            { "action": "APPLY_STATUS", "params": { "target": "SELF", "status_id": "EFFECT_MODIFIER_CANCEL_NEGATIVE", "duration": 1 } },
            { "action": "APPLY_STATUS", "params": { "target": "SELF", "status_id": "IMMUNE_COMBAT_DAMAGE", "value": 1, "duration": 1 } }
          ]
        }
      },
      "ren": {
        "name": "收敛",
        "description": "若你本轮未移动，你可以改为复制上一位行动的玩家已结算的基础爻辞效果，并取消其负面部分。",
        "effect": {
          "condition": { "op": "PLAYER_HAS_FLAG", "params": { "flag": "HAS_NOT_MOVED_THIS_TURN" } },
          "actions": [
            {
              "action": "COPY_EFFECT",
              "params": {
                "target": "SELF",
                "source_effect": { "type": "LAST_BASIC_CARD_EFFECT_PLAYED", "player_scope": "LAST_ACTED_PLAYER" },
                "modifications": { "remove_negative_parts": true }
              }
            }
          ]
        }
      },
      "tian": {
        "name": "滋养",
        "description": "若你本轮未移动，你可以将【厚德载物】效果赋予一名盟友。",
        "effect": {
          "condition": { "op": "PLAYER_HAS_FLAG", "params": { "flag": "HAS_NOT_MOVED_THIS_TURN" } },
          "actions": [
            {
              "action": "APPLY_STATUS",
              "params": { "target": "ALLY_FORMAL_SINGLE", "status_id": "EFFECT_MODIFIER_CANCEL_NEGATIVE", "duration": 1 }
            }
          ]
        }
      }
    }
  }
}
```

---

### **第三卦：《屯》 ☵☳ - 难**
**核心机制：【盘桓待机】**
- **效果：** 在你所在的区域创建-一个【屯】实体，持续**最多3轮**。在【屯】实体被移除前，你不能再次打出《屯》。该实体具有以下属性：
  - **迷雾：** 任何棋子不能进入此区域。你的棋子可以自由离开，实体将留在原地。
  - **引爆：** 在你的【解读阶段】开始时，若你的棋子位于该区域，你可以选择“引爆”该实体，立即触发其爻辞效果，并移除该实体。
- **爻辞变量：**
  - **地部 (建侯):** 引爆时，你可以移动到一个相邻的空区域，并在此处创建一个永久的【前哨】实体（你每次进入或离开，获得2金币）。
  - **人部 (求助):** 引爆时，你可以与一名**正式盟友**交换任意数量的手牌。
  - **天部 (甘霖):** 引爆时，你获得15金币，但你的阴阳指示条强制向【阳】移动2点。

```json
{
  "id": "basic_03_tun",
  "name": "屯",
  "symbol": "☵☳",
  "sequence": 3,
  "pinyin": "tun",
  "strokes": 7,
  "type": "basic",
  "effect": {
    "condition": { "op": "IS_ENTITY_ON_BOARD", "params": { "entity_type": "ENTITY_TUN", "count": 0 } },
    "actions": [
      {
        "action": "CREATE_ENTITY",
        "params": {
          "entity_type": "ENTITY_TUN",
          "position": "SELF",
          "owner": "SELF",
          "properties": {
            "name": "屯",
            "duration": 3,
            "blocks_movement": { "for": "ALL_PLAYERS", "exceptions": ["OWNER_CAN_LEAVE"] },
            "detonation_card_id": "basic_03_tun"
          }
        }
      }
    ]
  },
  "core_mechanism": {
    "name": "盘桓待机 (引爆)",
    "description": "引爆【屯】实体时触发。你必须在【屯】所在的区域才能引爆。",
    "variants": {
      "di": {
        "name": "建侯",
        "effect": {
          "actions": [
            { "action": "DESTROY_ENTITY", "params": { "target_entity_type": "ENTITY_TUN", "position": "SELF" } },
            { "action": "MOVE", "params": { "target": "SELF", "destination": "ADJACENT_EMPTY", "value": 1 } },
            { "action": "CREATE_ENTITY", "params": { "entity_type": "ENTITY_OUTPOST", "position": "SELF", "owner": "SELF", "is_permanent": true, "properties": { "name": "前哨", "on_enter_effect": { "actions": [{"action": "GAIN_RESOURCE", "params": {"target": "EVENT_SOURCE_PLAYER", "resource": "gold", "value": 2}}]}, "on_leave_effect": {"actions": [{"action": "GAIN_RESOURCE", "params": {"target": "EVENT_SOURCE_PLAYER", "resource": "gold", "value": 2}}]} } } }
          ]
        }
      },
      "ren": {
        "name": "求助",
        "effect": {
          "actions": [
            { "action": "DESTROY_ENTITY", "params": { "target_entity_type": "ENTITY_TUN", "position": "SELF" } },
            { "action": "SWAP_HAND_CARDS", "params": { "target": "SELF", "other_player": "ALLY_FORMAL_SINGLE_CHOICE", "atomic": true } }
          ]
        }
      },
      "tian": {
        "name": "甘霖",
        "effect": {
          "actions": [
            { "action": "DESTROY_ENTITY", "params": { "target_entity_type": "ENTITY_TUN", "position": "SELF" } },
            { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "gold", "value": 15 } },
            { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "YIN_YANG_GAUGE", "value": 2 } }
          ]
        }
      }
    }
  }
}
```

---
### **第四卦：《蒙》 ☶☵ - 昧**
**核心机制：【启蒙之雾】**
- **效果：** 指定一名其他玩家。该玩家翻开其【基础牌】后，效果不立即结算。你代其选择一项：
  1. **【教化】:** 该玩家正常结算其效果。
  2. **【惩戒】:** 该玩家的效果被**无效化**，改为**损失** 5点生命值。
- **爻辞变量：**
  - **地部 (引导):** 若你选择【教化】，你复制其效果总收益的50%（向下取整）。
  - **人部 (约束):** 若你选择【惩戒】，“生命值损失”提升为8点。
  - **天部 (反制):** 若你选择【惩戒】，你可以将被无效化的效果，转而对**另一名其他玩家**施放。

```json
{
  "id": "basic_04_meng",
  "name": "蒙",
  "symbol": "☶☵",
  "sequence": 4,
  "pinyin": "meng",
  "strokes": 13,
  "type": "basic",
  "core_mechanism": {
    "name": "启蒙之雾",
    "description": "指定一名其他玩家，在该玩家解读基础牌时，你为其选择【教化】或【惩戒】。",
    "variants": {
      "di": {
        "name": "引导",
        "effect": {
          "actions": [
            {
              "action": "APPLY_STATUS",
              "params": {
                "target": "OPPONENT_CHOICE_SINGLE",
                "status_id": "MONTORIAL_FOG",
                "duration": 1,
                "value": {
                  "teach_effect": { "action": "COPY_EFFECT", "params": { "target": "SELF", "source_effect": { "type": "INTERRUPTED_EFFECT" }, "modifications": { "only_gains": true, "multiplier": 0.5 } } },
                  "discipline_effect": { "action": "LOSE_RESOURCE", "params": { "target": "EVENT_SOURCE_PLAYER", "resource": "health", "value": 5 } }
                }
              }
            }
          ]
        }
      },
      "ren": {
        "name": "约束",
        "effect": {
          "actions": [
            {
              "action": "APPLY_STATUS",
              "params": {
                "target": "OPPONENT_CHOICE_SINGLE",
                "status_id": "MONTORIAL_FOG",
                "duration": 1,
                "value": {
                  "discipline_effect": { "action": "LOSE_RESOURCE", "params": { "target": "EVENT_SOURCE_PLAYER", "resource": "health", "value": 8 } }
                }
              }
            }
          ]
        }
      },
      "tian": {
        "name": "反制",
        "effect": {
          "actions": [
            {
              "action": "APPLY_STATUS",
              "params": {
                "target": "OPPONENT_CHOICE_SINGLE",
                "status_id": "MONTORIAL_FOG",
                "duration": 1,
                "value": {
                  "discipline_effect": { "action": "COPY_EFFECT", "params": { "target": "OPPONENT_CHOICE_SINGLE", "source_effect": { "type": "INTERRUPTED_EFFECT" } } }
                }
              }
            }
          ]
        }
      }
    }
  }
}
```

---

### **第五卦：《需》 ☵☰ - 待**
**核心机制：【云中之需】**
- **效果：** 跳过你本轮的【解读阶段】。在下一轮你的【归整阶段】“回合结束时效果结算”步骤，你获得10金币和2张基础牌。
- **爻辞变量：**
  - **地部 (静待):** 在等待期间，你获得【IMMUNITY_GENERAL_NEGATIVE (1)】状态。
  - **人部 (险待):** 最终奖励提升至15金币和3张牌。但若你在等待期间受到任何**伤害**，此效果被取消。
  - **天部 (宴待):** 最终奖励变为20金币。你可以将其中最多一半分享给一名**正式盟友**。

```json
{
  "id": "basic_05_xu",
  "name": "需",
  "symbol": "☵☰",
  "sequence": 5,
  "pinyin": "xu",
  "strokes": 8,
  "type": "basic",
  "core_mechanism": {
    "name": "云中之需",
    "description": "跳过解读，在下轮归整时获得奖励。",
    "variants": {
      "di": {
        "name": "静待",
        "effect": {
          "actions": [
            { "action": "SKIP_PHASE", "params": { "phase": "INTERPRETATION" } },
            { "action": "APPLY_STATUS", "params": { "target": "SELF", "status_id": "IMMUNITY_GENERAL_NEGATIVE", "value": 1, "duration": 1 } },
            { "action": "EXECUTE_LATER", "params": { "delay": "NEXT_UPKEEP_PHASE", "expiry_time": "1 ROUND", "effect": { "actions": [ { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "gold", "value": 10 } }, { "action": "DRAW_CARD", "params": { "target": "SELF", "deck": "basic", "count": 2 } } ] } } }
          ]
        }
      },
      "ren": {
        "name": "险待",
        "effect": {
          "actions": [
            { "action": "SKIP_PHASE", "params": { "phase": "INTERPRETATION" } },
            { "action": "EXECUTE_LATER", "params": { "delay": "NEXT_UPKEEP_PHASE", "expiry_time": "1 ROUND", "condition": { "op": "PLAYER_HAS_NOT_TAKEN_DAMAGE_SINCE", "params": { "timestamp": "NOW" } }, "effect": { "actions": [ { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "gold", "value": 15 } }, { "action": "DRAW_CARD", "params": { "target": "SELF", "deck": "basic", "count": 3 } } ] } } }
          ]
        }
      },
      "tian": {
        "name": "宴待",
        "effect": {
          "actions": [
            { "action": "SKIP_PHASE", "params": { "phase": "INTERPRETATION" } },
            { "action": "EXECUTE_LATER", "params": { "delay": "NEXT_UPKEEP_PHASE", "expiry_time": "1 ROUND", "effect": { "actions": [ { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "gold", "value": 10 } }, { "action": "CHOICE", "params": { "target": "SELF", "options": [ { "description": "将10金币赠予盟友", "effect": { "action": "TRANSFER_RESOURCE", "params": { "from": "SELF", "to": "ALLY_FORMAL_SINGLE", "resource": "gold", "value": 10 } } } ] } } ] } } }
          ]
        }
      }
    }
  }
}
```

---

### **第六卦：《讼》 ☰☵ - 争**
**核心机制：【天理仲裁】**
- **效果：** 指定一名其他玩家，触发“争讼”事件。双方各从手中选一张【基础牌】同时亮出，比较“笔画数”，少者胜。胜诉方从败诉方**夺取**10金币，败诉方额外**损失**5点生命值。
- **爻辞变量：**
  - **地部 (退让):** 若你败诉，你被夺取的金币减半（5金币）。
  - **人部 (和解):** 你可以提议“庭外和解”：双方各**支付**5金币给游戏基金，然后各自抽一张基础牌。
  - **天部 (终审):** 若你胜诉，你额外获得一枚永久的【威望】状态（“论道”或“争讼”时笔画数-2）。

```json
{
  "id": "basic_06_song",
  "name": "讼",
  "symbol": "☰☵",
  "sequence": 6,
  "pinyin": "song",
  "strokes": 8,
  "type": "basic",
  "core_mechanism": {
    "name": "天理仲裁",
    "description": "与其他玩家通过比拼卡牌笔画数来决定胜负，并产生奖惩。",
    "variants": {
      "di": {
        "name": "退让",
        "effect": {
          "actions": [
            { "action": "TRIGGER_EVENT", "params": { "event_id": "EVENT_SONG", "participants": ["SELF", "OPPONENT_CHOICE_SINGLE"], "modifications": { "SELF_LOSS_MODIFIER": {"op": "MULTIPLY", "value": 0.5} } } }
          ]
        }
      },
      "ren": {
        "name": "和解",
        "effect": {
          "actions": [
            { "action": "CHOICE", "params": { "target": "OPPONENT_CHOICE_SINGLE", "options": [ { "description": "接受和解", "effect": { "actions": [ { "action": "PAY_COST", "params": { "target": "SELF", "resource": "gold", "value": 5 } }, { "action": "PAY_COST", "params": { "target": "EVENT_TARGET_PLAYER", "resource": "gold", "value": 5 } }, { "action": "DRAW_CARD", "params": { "target": "SELF", "deck": "basic", "count": 1 } }, { "action": "DRAW_CARD", "params": { "target": "EVENT_TARGET_PLAYER", "deck": "basic", "count": 1 } } ] } }, { "description": "拒绝和解，开始争讼", "effect": { "action": "TRIGGER_EVENT", "params": { "event_id": "EVENT_SONG", "participants": ["SELF", "EVENT_TARGET_PLAYER"] } } } ] } }
          ]
        }
      },
      "tian": {
        "name": "终审",
        "effect": {
          "actions": [
            { "action": "TRIGGER_EVENT", "params": { "event_id": "EVENT_SONG", "participants": ["SELF", "OPPONENT_CHOICE_SINGLE"], "modifications": { "SELF_WIN_EFFECT": { "action": "APPLY_STATUS", "params": { "target": "SELF", "status_id": "PRESTIGE", "is_permanent": true } } } } }
          ]
        }
      }
    }
  }
}
```

---

### **第七卦：《师》 ☷☵ - 众**
**核心机制：【王师出征】**
- **效果：** 你可以对你所在**宫位**的所有**正式盟友**（包括你自己）施加【军阵】状态，持续一轮（攻击力+3，但受到的任何**伤害**+1）。
- **爻辞变量：**
  - **地部 (纪律):** 发动此效果需**支付**5金币作为**代价**。
  - **人部 (兵法):** 你可以改为让所有目标获得【急行军】状态（本轮结束后，可以立即额外移动一格）。
  - **天部 (将帅):** 你可以将【军阵】状态的效果集中赋予一名**正式盟友**，使其获得【主帅】状态（攻击力+8，且获得【IMMUNE_COMBAT_DAMAGE (1)】）。

```json
{
  "id": "basic_07_shi",
  "name": "师",
  "symbol": "☷☵",
  "sequence": 7,
  "pinyin": "shi",
  "strokes": 8,
  "type": "basic",
  "core_mechanism": {
    "name": "王师出征",
    "description": "为你和盟友施加增益状态。",
    "variants": {
      "di": {
        "name": "纪律",
        "effect": {
          "cost": [{ "resource": "gold", "value": 5 }],
          "actions": [
            { "action": "APPLY_STATUS", "params": { "target": "ALLY_FORMAL_IN_PALACE", "status_id": "WAR_FORMATION", "duration": 1 } }
          ]
        }
      },
      "ren": {
        "name": "兵法",
        "effect": {
          "actions": [
            { "action": "APPLY_STATUS", "params": { "target": "ALLY_FORMAL_IN_PALACE", "status_id": "RAPID_MARCH", "duration": 1 } }
          ]
        }
      },
      "tian": {
        "name": "将帅",
        "effect": {
          "actions": [
            { "action": "APPLY_STATUS", "params": { "target": "ALLY_FORMAL_SINGLE_CHOICE", "status_id": "GENERAL", "duration": 1 } }
          ]
        }
      }
    }
  }
}
```

---

### **第八卦：《比》 ☵☷ - 附**
**核心机制：【同心之盟】**
- **效果：** 选择一名其他玩家，邀请其结盟。若对方同意，你们双方获得【ALLY_FORMAL】状态，持续3轮。
- **【ALLY_FORMAL】状态效果：** 1. 你们不能成为彼此攻击或偷窃效果的目标。2. 你们可以共享彼此所在区域的【奇门八门】效果。
- **爻辞变量：**
  - **地部 (信赖):** 缔结盟约时，你和你的盟友立即各恢复5点生命值。
  - **人部 (外交):** 缔结盟约时，你可以**支付**5金币，让一名**非盟友**玩家抽2张基础牌。
  - **天部 (王道):** 【ALLY_FORMAL】状态持续时间延长至5轮，且期间你们共享彼此金币总收益的10%（向下取整）。

```json
{
  "id": "basic_08_bi",
  "name": "比",
  "symbol": "☵☷",
  "sequence": 8,
  "pinyin": "bi",
  "strokes": 8,
  "type": "basic",
  "core_mechanism": {
    "name": "同心之盟",
    "description": "与其他玩家结盟。",
    "variants": {
      "di": {
        "name": "信赖",
        "effect": {
          "actions": [
            { "action": "PROPOSE_ALLIANCE", "params": { "target": "OPPONENT_CHOICE_SINGLE", "duration": 3, "on_accept_effect": { "actions": [ { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "health", "value": 5 } }, { "action": "GAIN_RESOURCE", "params": { "target": "EVENT_TARGET_PLAYER", "resource": "health", "value": 5 } } ] } } }
          ]
        }
      },
      "ren": {
        "name": "外交",
        "effect": {
          "actions": [
            { "action": "PROPOSE_ALLIANCE", "params": { "target": "OPPONENT_CHOICE_SINGLE", "duration": 3, "on_accept_effect": { "cost": [{ "resource": "gold", "value": 5 }], "actions": [ { "action": "DRAW_CARD", "params": { "target": "PLAYER_CHOICE_ANY_NON_ALLY", "deck": "basic", "count": 2 } } ] } } }
          ]
        }
      },
      "tian": {
        "name": "王道",
        "effect": {
          "actions": [
            { "action": "PROPOSE_ALLIANCE", "params": { "target": "OPPONENT_CHOICE_SINGLE", "duration": 5, "alliance_properties": { "share_gold_gain_percentage": 10 } } }
          ]
        }
      }
    }
  }
}
```

---
### **第九卦：《小畜》 ☴☰ - 密云**
**核心机制：【密云不雨】**
- **效果：** 风行天上，聚云成势，但雨未降。此卦代表小有积蓄，但尚未形成大的突破。效果偏向于小额的获取与限制。
- **爻辞变量：**
  - **地部 (种德):** 小有积蓄。你获得3金币，并抽一张基础牌。
  - **人部 (牵连):** 与他人产生小的交互。你指定一名其他玩家，你们各弃一张手牌。
  - **天部 (节制):** 施加小的限制。指定一名其他玩家，在本轮的【结算阶段】，该玩家不能通过区域效果获得金币。
```json
{
  "id": "basic_09_xiao_chu",
  "name": "小畜",
  "symbol": "☴☰",
  "sequence": 9,
  "pinyin": "xiao_chu",
  "strokes": 9,
  "type": "basic",
  "core_mechanism": {
    "name": "密云不雨",
    "description": "小有积蓄，但尚未形成大的突破。效果偏向于小额的获取与限制。",
    "variants": {
      "di": {
        "name": "种德",
        "effect": {
          "actions": [
            {
              "action": "GAIN_RESOURCE",
              "params": {
                "target": "SELF",
                "resource": "gold",
                "value": 3
              }
            },
            {
              "action": "DRAW_CARD",
              "params": {
                "target": "SELF",
                "deck": "basic",
                "count": 1
              }
            }
          ]
        }
      },
      "ren": {
        "name": "牵连",
        "effect": {
          "actions": [
            {
              "action": "DISCARD_CARD",
              "params": {
                "target": "SELF",
                "count": 1
              }
            },
            {
              "action": "DISCARD_CARD",
              "params": {
                "target": "OPPONENT_CHOICE_SINGLE",
                "count": 1
              }
            }
          ]
        }
      },
      "tian": {
        "name": "节制",
        "effect": {
          "actions": [
            {
              "action": "APPLY_STATUS",
              "params": {
                "target": "OPPONENT_CHOICE_SINGLE",
                "status_id": "CANNOT_GAIN_GOLD_FROM_ZONE",
                "duration": 1
              }
            }
          ]
        }
      }
    }
  }
}
```

---
### **第10卦：《履》 ☰☱ - 践行**
**核心机制：【如履薄冰】**
- **效果：** 小心翼翼地前进或采取行动。
- **爻辞变量：**
  - **地部 (安履):** 你可以安全地移动1格，且不受任何地形的负面惩罚。
  - **人部 (眇能视):** 你可以查看一名玩家的手牌。
  - **天部 (履虎尾):** 你对一名玩家造成3点伤害，但你自己也损失3点生命值。
```json
{
  "id": "basic_10_li",
  "name": "履",
  "symbol": "☰☱",
  "sequence": 10,
  "pinyin": "li",
  "strokes": 10,
  "type": "basic",
  "core_mechanism": {
    "name": "如履薄冰",
    "description": "小心翼翼地前进或采取行动。",
    "variants": {
      "di": {
        "name": "安履",
        "effect": {
          "actions": [
            {
              "action": "MOVE",
              "params": {
                "target": "SELF",
                "value": 1,
                "move_type": "NORMAL_IGNORE_PENALTY"
              }
            }
          ]
        }
      },
      "ren": {
        "name": "眇能视",
        "effect": {
          "actions": [
            {
              "action": "LOOKUP",
              "params": {
                "target": "OPPONENT_CHOICE_SINGLE",
                "info_type": "hand_cards"
              }
            }
          ]
        }
      },
      "tian": {
        "name": "履虎尾",
        "effect": {
          "actions": [
            {
              "action": "DEAL_DAMAGE",
              "params": {
                "target": "OPPONENT_CHOICE_SINGLE",
                "value": 3
              }
            },
            {
              "action": "LOSE_RESOURCE",
              "params": {
                "target": "SELF",
                "resource": "health",
                "value": 3
              }
            }
          ]
        }
      }
    }
  }
}
```

---
### **第11卦：《泰》 ☷☰ - 通达**
**核心机制：【否极泰来】**
- **效果：** 天地交感，万物通泰。带来和平与丰盛。
- **爻辞变量：**
  - **地部 (拔茅茹):** 你获得5金币。
  - **人部 (包荒):** 你恢复5点生命值。
  - **天部 (泰重来):** 你获得3金币并抽一张基础牌。
```json
{
  "id": "basic_11_tai",
  "name": "泰",
  "symbol": "☷☰",
  "sequence": 11,
  "pinyin": "tai",
  "strokes": 11,
  "type": "basic",
  "core_mechanism": {
    "name": "否极泰来",
    "description": "天地交感，万物通泰。带来和平与丰盛。",
    "variants": {
      "di": {
        "name": "拔茅茹",
        "effect": {
          "actions": [
            {
              "action": "GAIN_RESOURCE",
              "params": {
                "target": "SELF",
                "resource": "gold",
                "value": 5
              }
            }
          ]
        }
      },
      "ren": {
        "name": "包荒",
        "effect": {
          "actions": [
            {
              "action": "GAIN_RESOURCE",
              "params": {
                "target": "SELF",
                "resource": "health",
                "value": 5
              }
            }
          ]
        }
      },
      "tian": {
        "name": "泰重来",
        "effect": {
          "actions": [
            {
              "action": "GAIN_RESOURCE",
              "params": {
                "target": "SELF",
                "resource": "gold",
                "value": 3
              }
            },
            {
              "action": "DRAW_CARD",
              "params": {
                "target": "SELF",
                "deck": "basic",
                "count": 1
              }
            }
          ]
        }
      }
    }
  }
}
```

---
### **第12卦：《否》 ☰☷ - 闭塞**
**核心机制：【天地不交】**
- **效果：** 天地闭塞，万物不通。带来阻碍与停滞。
- **爻辞变量：**
  - **地部 (包羞):** 你弃一张手牌。
  - **人部 (休否):** 指定一名玩家，该玩家本回合不能移动。
  - **天部 (倾否):** 指定一名玩家，该玩家失去5金币。
```json
{
  "id": "basic_12_pi",
  "name": "否",
  "symbol": "☰☷",
  "sequence": 12,
  "pinyin": "pi",
  "strokes": 12,
  "type": "basic",
  "core_mechanism": {
    "name": "天地不交",
    "description": "天地闭塞，万物不通。带来阻碍与停滞。",
    "variants": {
      "di": {
        "name": "包羞",
        "effect": {
          "actions": [
            {
              "action": "DISCARD_CARD",
              "params": {
                "target": "SELF",
                "count": 1
              }
            }
          ]
        }
      },
      "ren": {
        "name": "休否",
        "effect": {
          "actions": [
            {
              "action": "APPLY_STATUS",
              "params": {
                "target": "OPPONENT_CHOICE_SINGLE",
                "status_id": "CANNOT_MOVE",
                "duration": 1
              }
            }
          ]
        }
      },
      "tian": {
        "name": "倾否",
        "effect": {
          "actions": [
            {
              "action": "LOSE_RESOURCE",
              "params": {
                "target": "OPPONENT_CHOICE_SINGLE",
                "resource": "gold",
                "value": 5
              }
            }
          ]
        }
      }
    }
  }
}
```

---
### **第13卦：《同人》 ☰☲ - 和同**
**核心机制：【与人偕行】**
- **效果：** 与人同心，其利断金。
- **爻辞变量：**
  - **地部 (同人于野):** 若你有盟友，你和你所有的盟友各获得2金币。
  - **人部 (同人于宗):** 指定一名玩家，你与其交换一张手牌。
  - **天部 (大师克相遇):** 你对一名玩家造成4点伤害。若你有盟友，改为造成6点伤害。
```json
{
  "id": "basic_13_tong_ren",
  "name": "同人",
  "symbol": "☰☲",
  "sequence": 13,
  "pinyin": "tong_ren",
  "strokes": 13,
  "type": "basic",
  "core_mechanism": {
    "name": "与人偕行",
    "description": "与人同心，其利断金。",
    "variants": {
      "di": {
        "name": "同人于野",
        "effect": {
          "condition": { "op": "PLAYER_HAS_ALLY" },
          "actions": [
            { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "gold", "value": 2 } },
            { "action": "GAIN_RESOURCE", "params": { "target": "ALLY_FORMAL_ALL", "resource": "gold", "value": 2 } }
          ]
        }
      },
      "ren": {
        "name": "同人于宗",
        "effect": {
          "actions": [
            { "action": "SWAP_HAND_CARDS", "params": { "target": "SELF", "other_player": "OPPONENT_CHOICE_SINGLE", "count": 1, "atomic": true } }
          ]
        }
      },
      "tian": {
        "name": "大师克相遇",
        "effect": {
          "actions": [
            {
              "action": "CHOICE",
              "params": {
                "target": "SELF",
                "options": [
                  {
                    "description": "造成6点伤害（需要盟友）",
                    "condition": { "op": "PLAYER_HAS_ALLY" },
                    "effect": { "actions": [ { "action": "DEAL_DAMAGE", "params": { "target": "OPPONENT_CHOICE_SINGLE", "value": 6 } } ] }
                  },
                  {
                    "description": "造成4点伤害",
                    "effect": { "actions": [ { "action": "DEAL_DAMAGE", "params": { "target": "OPPONENT_CHOICE_SINGLE", "value": 4 } } ] }
                  }
                ]
              }
            }
          ]
        }
      }
    }
  }
}
```

---
### **第14卦：《大有》 ☲☰ - 大获**
**核心机制：【大有斩获】**
- **效果：** 象征大丰收，获得大量资源。
- **爻辞变量：**
  - **地部 (交相利):** 你获得8金币。
  - **人部 (公用亨于天子):** 你获得5金币并抽2张基础牌。
  - **天部 (自天祐之):** 你获得12金币，但必须展示给所有玩家看。
```json
{
  "id": "basic_14_da_you",
  "name": "大有",
  "symbol": "☲☰",
  "sequence": 14,
  "pinyin": "da_you",
  "strokes": 14,
  "type": "basic",
  "core_mechanism": {
    "name": "大有斩获",
    "description": "象征大丰收，获得大量资源。",
    "variants": {
      "di": {
        "name": "交相利",
        "effect": {
          "actions": [
            { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "gold", "value": 8 } }
          ]
        }
      },
      "ren": {
        "name": "公用亨于天子",
        "effect": {
          "actions": [
            { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "gold", "value": 5 } },
            { "action": "DRAW_CARD", "params": { "target": "SELF", "deck": "basic", "count": 2 } }
          ]
        }
      },
      "tian": {
        "name": "自天祐之",
        "effect": {
          "actions": [
            { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "gold", "value": 10 } }
          ]
        }
      }
    }
  }
}
```

---
### **第15卦：《谦》 ☷☶ - 谦逊**
**核心机制：【谦谦君子】**
- **效果：** 谦虚退让，获得他人的尊敬或小利。
- **爻辞变量：**
  - **地部 (谦谦君子):** 抽一张基础牌。
  - **人部 (鸣谦):** 所有其他玩家给你1金币。
  - **天部 (劳谦):** 恢复4点生命值。
```json
{
  "id": "basic_15_qian",
  "name": "谦",
  "symbol": "☷☶",
  "sequence": 15,
  "pinyin": "qian",
  "strokes": 15,
  "type": "basic",
  "core_mechanism": {
    "name": "谦谦君子",
    "description": "谦虚退让，获得他人的尊敬或小利。",
    "variants": {
      "di": {
        "name": "谦谦君子",
        "effect": {
          "actions": [
            { "action": "DRAW_CARD", "params": { "target": "SELF", "deck": "basic", "count": 1 } }
          ]
        }
      },
      "ren": {
        "name": "鸣谦",
        "effect": {
          "actions": [
            { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "gold", "value": 1, "source": "OPPONENT_ALL" } }
          ]
        }
      },
      "tian": {
        "name": "劳谦",
        "effect": {
          "actions": [
            { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "health", "value": 4 } }
          ]
        }
      }
    }
  }
}
```

---
### **第16卦：《豫》 ☳☷ - 豫乐**
**核心机制：【其乐融融】**
- **效果：** 带来愉悦和顺畅。
- **爻辞变量：**
  - **地部 (介于石):** 你获得【守护】状态，可抵挡2点伤害。
  - **人部 (盱豫):** 你可以立即额外移动2格。
  - **天部 (冥豫):** 你和所有盟友各抽一张牌。
```json
{
  "id": "basic_16_yu",
  "name": "豫",
  "symbol": "☳☷",
  "sequence": 16,
  "pinyin": "yu",
  "strokes": 16,
  "type": "basic",
  "core_mechanism": {
    "name": "其乐融融",
    "description": "带来愉悦和顺畅。",
    "variants": {
      "di": {
        "name": "介于石",
        "effect": {
          "actions": [
            { "action": "APPLY_STATUS", "params": { "target": "SELF", "status_id": "GUARD", "value": 2, "duration": 1 } }
          ]
        }
      },
      "ren": {
        "name": "盱豫",
        "effect": {
          "actions": [
            { "action": "MOVE", "params": { "target": "SELF", "value": 2, "move_type": "NORMAL" } }
          ]
        }
      },
      "tian": {
        "name": "冥豫",
        "effect": {
          "actions": [
            { "action": "DRAW_CARD", "params": { "target": "SELF", "deck": "basic", "count": 1 } },
            { "action": "DRAW_CARD", "params": { "target": "ALLY_FORMAL_ALL", "deck": "basic", "count": 1 } }
          ]
        }
      }
    }
  }
}
```

---
### **第17卦：《随》 ☱☳ - 跟随**
**核心机制：【随行逐队】**
- **效果：** 跟随他人的行动。
- **爻辞变量：**
  - **地部 (出门交):** 移动到与上一位行动玩家相邻的格子。
  - **人部 (系小子):** 弃一张牌，然后抽两张牌。
  - **天部 (随有获):** 上一位行动的玩家获得3金币，你也获得3金币。
```json
{
  "id": "basic_17_sui",
  "name": "随",
  "symbol": "☱☳",
  "sequence": 17,
  "pinyin": "sui",
  "strokes": 17,
  "type": "basic",
  "core_mechanism": {
    "name": "随行逐队",
    "description": "跟随他人的行动。",
    "variants": {
      "di": {
        "name": "出门交",
        "effect": {
          "actions": [
            { "action": "MOVE", "params": { "target": "SELF", "destination": "ADJACENT_TO_PLAYER", "player": "LAST_ACTED_PLAYER" } }
          ]
        }
      },
      "ren": {
        "name": "系小子",
        "effect": {
          "actions": [
            { "action": "DISCARD_CARD", "params": { "target": "SELF", "count": 1 } },
            { "action": "DRAW_CARD", "params": { "target": "SELF", "deck": "basic", "count": 2 } }
          ]
        }
      },
      "tian": {
        "name": "随有获",
        "effect": {
          "actions": [
            { "action": "GAIN_RESOURCE", "params": { "target": "LAST_ACTED_PLAYER", "resource": "gold", "value": 3 } },
            { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "gold", "value": 3 } }
          ]
        }
      }
    }
  }
}
```

---
### **第18卦：《蛊》 ☶☴ - 整饬**
**核心机制：【拨乱反正】**
- **效果：** 整治混乱，去除弊病。
- **爻辞变量：**
  - **地部 (干父之蛊):** 移除你身上的一个负面状态。
  - **人部 (干母之蛊):** 指定一名玩家，移除其身上的一个正面状态。
  - **天部 (不事王侯):** 你获得【免疫负面效果】状态，持续一轮。
```json
{
  "id": "basic_18_gu",
  "name": "蛊",
  "symbol": "☶☴",
  "sequence": 18,
  "pinyin": "gu",
  "strokes": 18,
  "type": "basic",
  "core_mechanism": {
    "name": "拨乱反正",
    "description": "整治混乱，去除弊病。",
    "variants": {
      "di": {
        "name": "干父之蛊",
        "effect": {
          "actions": [
            { "action": "REMOVE_STATUS", "params": { "target": "SELF", "status_id": "ALL_NEGATIVE", "count": 1 } }
          ]
        }
      },
      "ren": {
        "name": "干母之蛊",
        "effect": {
          "actions": [
            { "action": "REMOVE_STATUS", "params": { "target": "OPPONENT_CHOICE_SINGLE", "status_id": "ALL_POSITIVE", "count": 1 } }
          ]
        }
      },
      "tian": {
        "name": "不事王侯",
        "effect": {
          "actions": [
            { "action": "APPLY_STATUS", "params": { "target": "SELF", "status_id": "IMMUNITY_GENERAL_NEGATIVE", "duration": 1 } }
          ]
        }
      }
    }
  }
}
```

---
### **第19卦：《临》 ☷☱ - 亲临**
**核心机制：【君子之临】**
- **效果：** 亲自到达，产生影响。
- **爻辞变量：**
  - **地部 (咸临):** 你所在区域的所有玩家（包括你）各获得2金币。
  - **人部 (甘临):** 你恢复你所在区域玩家数量的生命值。
  - **天部 (知临):** 对你所在区域的所有其他玩家造成2点伤害。
```json
{
  "id": "basic_19_lin",
  "name": "临",
  "symbol": "☷☱",
  "sequence": 19,
  "pinyin": "lin",
  "strokes": 19,
  "type": "basic",
  "core_mechanism": {
    "name": "君子之临",
    "description": "亲自到达，产生影响。",
    "variants": {
      "di": {
        "name": "咸临",
        "effect": {
          "actions": [
            { "action": "GAIN_RESOURCE", "params": { "target": "PLAYERS_IN_SAME_ZONE", "resource": "gold", "value": 2 } }
          ]
        }
      },
      "ren": {
        "name": "甘临",
        "effect": {
          "actions": [
            { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "health", "value": { "op": "COUNT", "target": "PLAYERS_IN_SAME_ZONE" } } }
          ]
        }
      },
      "tian": {
        "name": "知临",
        "effect": {
          "actions": [
            { "action": "DEAL_DAMAGE", "params": { "target": "OTHER_PLAYERS_IN_SAME_ZONE", "value": 2 } }
          ]
        }
      }
    }
  }
}
```

---
### **第20卦：《观》 ☴☷ - 观察**
**核心机制：【洞察观瞻】**
- **效果：** 观察局势，获取信息。
- **爻辞变量：**
  - **地部 (童观):** 查看牌库顶3张牌，然后放回。
  - **人部 (窥观):** 查看一名玩家的天命牌。
  - **天部 (观我生):** 查看所有玩家的阴阳值和手牌数量。
```json
{
  "id": "basic_20_guan",
  "name": "观",
  "symbol": "☴☷",
  "sequence": 20,
  "pinyin": "guan",
  "strokes": 20,
  "type": "basic",
  "core_mechanism": {
    "name": "洞察观瞻",
    "description": "观察局势，获取信息。",
    "variants": {
      "di": {
        "name": "童观",
        "effect": {
          "actions": [
            { "action": "LOOKUP", "params": { "target": "SELF", "info_type": "DECK_TOP", "deck": "basic", "count": 3 } }
          ]
        }
      },
      "ren": {
        "name": "窥观",
        "effect": {
          "actions": [
            { "action": "LOOKUP", "params": { "target": "OPPONENT_CHOICE_SINGLE", "info_type": "destiny_card" } }
          ]
        }
      },
      "tian": {
        "name": "观我生",
        "effect": {
          "actions": [
            { "action": "LOOKUP", "params": { "target": "ALL_PLAYERS", "info_type": "PUBLIC_INFO" } }
          ]
        }
      }
    }
  }
}
```

---
### **第21卦：《噬嗑》 ☲☳ - 咬合**
**核心机制：【惩奸除恶】**
- **效果：** 采取强硬手段解决问题。
- **爻辞变量：**
  - **地部 (噬肤):** 对一名玩家造成3点伤害。
  - **人部 (噬干肉):** 支付3金币，对一名玩家造成5点伤害。
  - **天部 (何校灭耳):** 对一名玩家造成2点伤害，并使其弃一张牌。
```json
{
  "id": "basic_21_shi_he",
  "name": "噬嗑",
  "symbol": "☲☳",
  "sequence": 21,
  "pinyin": "shi_he",
  "strokes": 21,
  "type": "basic",
  "core_mechanism": {
    "name": "惩奸除恶",
    "description": "采取强硬手段解决问题。",
    "variants": {
      "di": {
        "name": "噬肤",
        "effect": {
          "actions": [
            { "action": "DEAL_DAMAGE", "params": { "target": "OPPONENT_CHOICE_SINGLE", "value": 3 } }
          ]
        }
      },
      "ren": {
        "name": "噬干肉",
        "effect": {
          "cost": [{ "resource": "gold", "value": 3 }],
          "actions": [
            { "action": "DEAL_DAMAGE", "params": { "target": "OPPONENT_CHOICE_SINGLE", "value": 5 } }
          ]
        }
      },
      "tian": {
        "name": "何校灭耳",
        "effect": {
          "actions": [
            { "action": "DEAL_DAMAGE", "params": { "target": "OPPONENT_CHOICE_SINGLE", "value": 2 } },
            { "action": "DISCARD_CARD", "params": { "target": "OPPONENT_CHOICE_SINGLE", "count": 1 } }
          ]
        }
      }
    }
  }
}
```

---
### **第22卦：《贲》 ☶☲ - 装饰**
**核心机制：【文饰之美】**
- **效果：** 华美的装饰，实际作用不大。
- **爻辞变量：**
  - **地部 (贲其趾):** 获得1金币。
  - **人部 (贲其须):** 抽一张牌，然后弃一张牌。
  - **天部 (白贲):** 什么也不发生。
```json
{
  "id": "basic_22_ben",
  "name": "贲",
  "symbol": "☶☲",
  "sequence": 22,
  "pinyin": "ben",
  "strokes": 22,
  "type": "basic",
  "core_mechanism": {
    "name": "文饰之美",
    "description": "华美的装饰，实际作用不大。",
    "variants": {
      "di": {
        "name": "贲其趾",
        "effect": {
          "actions": [
            { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "gold", "value": 1 } }
          ]
        }
      },
      "ren": {
        "name": "贲其须",
        "effect": {
          "actions": [
            { "action": "DRAW_CARD", "params": { "target": "SELF", "deck": "basic", "count": 1 } },
            { "action": "DISCARD_CARD", "params": { "target": "SELF", "count": 1 } }
          ]
        }
      },
      "tian": {
        "name": "白贲",
        "effect": {
          "actions": []
        }
      }
    }
  }
}
```

---
### **第23卦：《剥》 ☶☷ - 剥落**
**核心机制：【剥蚀殆尽】**
- **效果：** 事物被腐蚀，根基动摇。
- **爻辞变量：**
  - **地部 (剥床以足):** 指定一名玩家，其失去3金币。
  - **人部 (剥床以肤):** 指定一名玩家，其失去5生命值。
  - **天部 (硕果不食):** 所有其他玩家失去3金币。
```json
{
  "id": "basic_23_bo",
  "name": "剥",
  "symbol": "☶☷",
  "sequence": 23,
  "pinyin": "bo",
  "strokes": 23,
  "type": "basic",
  "core_mechanism": {
    "name": "剥蚀殆尽",
    "description": "事物被腐蚀，根基动摇。",
    "variants": {
      "di": {
        "name": "剥床以足",
        "effect": {
          "actions": [
            { "action": "LOSE_RESOURCE", "params": { "target": "OPPONENT_CHOICE_SINGLE", "resource": "gold", "value": 3 } }
          ]
        }
      },
      "ren": {
        "name": "剥床以肤",
        "effect": {
          "actions": [
            { "action": "LOSE_RESOURCE", "params": { "target": "OPPONENT_CHOICE_SINGLE", "resource": "health", "value": 5 } }
          ]
        }
      },
      "tian": {
        "name": "硕果不食",
        "effect": {
          "actions": [
            { "action": "LOSE_RESOURCE", "params": { "target": "OPPONENT_ALL", "resource": "gold", "value": 3 } }
          ]
        }
      }
    }
  }
}
```

---
### **第24卦：《复》 ☷☳ - 回复**
**核心机制：【一阳来复】**
- **效果：** 从终点回到起点，重新开始。
- **爻辞变量：**
  - **地部 (不远复):** 移动到你出发时的格子。
  - **人部 (休复):** 从你的弃牌堆中将一张基础牌移回你的手牌。
  - **天部 (敦复):** 你的阴阳值变为0。
```json
{
  "id": "basic_24_fu",
  "name": "复",
  "symbol": "☷☳",
  "sequence": 24,
  "pinyin": "fu",
  "strokes": 24,
  "type": "basic",
  "core_mechanism": {
    "name": "一阳来复",
    "description": "从终点回到起点，重新开始。",
    "variants": {
      "di": {
        "name": "不远复",
        "effect": {
          "actions": [
            { "action": "MOVE", "params": { "target": "SELF", "destination": "START_OF_TURN_POSITION" } }
          ]
        }
      },
      "ren": {
        "name": "休复",
        "effect": {
          "actions": [
            { "action": "RECOVER_CARD_FROM_DISCARD", "params": { "target": "SELF", "deck": "basic", "count": 1 } }
          ]
        }
      },
      "tian": {
        "name": "敦复",
        "effect": {
          "actions": [
            { "action": "SET_RESOURCE", "params": { "target": "SELF", "resource": "YIN_YANG_GAUGE", "value": 0 } }
          ]
        }
      }
    }
  }
}
```

---
### **第25卦：《无妄》 ☰☳ - 无妄**
**核心机制：【无妄之灾】**
- **效果：** 意料之外的事件，可能好可能坏。
- **爻辞变量：**
  - **地部 (无妄之行):** 随机移动1-3格。
  - **人部 (无妄之药):** 随机一名玩家（包括你）恢复5点生命值。
  - **天部 (无妄之灾):** 随机一名玩家失去5金币。
```json
{
  "id": "basic_25_wu_wang",
  "name": "无妄",
  "symbol": "☰☳",
  "sequence": 25,
  "pinyin": "wu_wang",
  "strokes": 25,
  "type": "basic",
  "core_mechanism": {
    "name": "无妄之灾",
    "description": "意料之外的事件，可能好可能坏。",
    "variants": {
      "di": {
        "name": "无妄之行",
        "effect": {
          "actions": [
            { "action": "MOVE", "params": { "target": "SELF", "value": { "op": "RANDOM", "min": 1, "max": 3 }, "move_type": "NORMAL" } }
          ]
        }
      },
      "ren": {
        "name": "无妄之药",
        "effect": {
          "actions": [
            { "action": "GAIN_RESOURCE", "params": { "target": "PLAYER_CHOICE_RANDOM", "resource": "health", "value": 5 } }
          ]
        }
      },
      "tian": {
        "name": "无妄之灾",
        "effect": {
          "actions": [
            { "action": "LOSE_RESOURCE", "params": { "target": "PLAYER_CHOICE_RANDOM", "resource": "gold", "value": 5 } }
          ]
        }
      }
    }
  }
}
```

---
### **第26卦：《大畜》 ☶☰ - 大蓄**
**核心机制：【积蓄力量】**
- **效果：** 积蓄资源或限制他人。
- **爻辞变量：**
  - **地部 (舆说辐):** 跳过你的【移动阶段】，在下一轮开始时获得5金币。
  - **人部 (良马逐):** 指定一名玩家，该玩家本轮只能移动1格。
  - **天部 (何天之衢):** 你获得【蓄力】状态，你的下一次伤害+3。
```json
{
  "id": "basic_26_da_chu",
  "name": "大畜",
  "symbol": "☶☰",
  "sequence": 26,
  "pinyin": "da_chu",
  "strokes": 26,
  "type": "basic",
  "core_mechanism": {
    "name": "积蓄力量",
    "description": "积蓄资源或限制他人。",
    "variants": {
      "di": {
        "name": "舆说辐",
        "effect": {
          "actions": [
            { "action": "SKIP_PHASE", "params": { "phase": "MOVEMENT" } },
            { "action": "EXECUTE_LATER", "params": { "delay": "NEXT_TURN_START", "expiry_time": "1 ROUND", "effect": { "actions": [ { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "gold", "value": 5 } } ] } } }
          ]
        }
      },
      "ren": {
        "name": "良马逐",
        "effect": {
          "actions": [
            { "action": "APPLY_STATUS", "params": { "target": "OPPONENT_CHOICE_SINGLE", "status_id": "MOVE_LIMIT", "value": 1, "duration": 1 } }
          ]
        }
      },
      "tian": {
        "name": "何天之衢",
        "effect": {
          "actions": [
            { "action": "APPLY_STATUS", "params": { "target": "SELF", "status_id": "DAMAGE_BOOST", "value": 3, "duration": "NEXT_ATTACK" } }
          ]
        }
      }
    }
  }
}
```

---
### **第27卦：《颐》 ☶☳ - 颐养**
**核心机制：【修身养性】**
- **效果：** 颐养天年，获得补给。
- **爻辞变量：**
  - **地部 (舍尔灵龟):** 你恢复3点生命值。
  - **人部 (拂经):** 你可以弃掉所有手牌，然后抽取等量的牌。
  - **天部 (由颐):** 你和所有盟友各恢复3点生命值。
```json
{
  "id": "basic_27_yi",
  "name": "颐",
  "symbol": "☶☳",
  "sequence": 27,
  "pinyin": "yi",
  "strokes": 27,
  "type": "basic",
  "core_mechanism": {
    "name": "修身养性",
    "description": "颐养天年，获得补给。",
    "variants": {
      "di": {
        "name": "舍尔灵龟",
        "effect": {
          "actions": [
            { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "health", "value": 3 } }
          ]
        }
      },
      "ren": {
        "name": "拂经",
        "effect": {
          "actions": [
            { "action": "DISCARD_CARD", "params": { "target": "SELF", "count": "ALL" } },
            { "action": "DRAW_CARD", "params": { "target": "SELF", "deck": "basic", "count": { "op": "COUNT", "target": "DISCARDED_THIS_TURN" } } }
          ]
        }
      },
      "tian": {
        "name": "由颐",
        "effect": {
          "actions": [
            { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "health", "value": 3 } },
            { "action": "GAIN_RESOURCE", "params": { "target": "ALLY_FORMAL_ALL", "resource": "health", "value": 3 } }
          ]
        }
      }
    }
  }
}
```

---
### **第28卦：《大过》 ☱☴ - 大过**
**核心机制：【矫枉过正】**
- **效果：** 行事过当，带来极端后果。
- **爻辞变量：**
  - **地部 (枯杨生华):** 弃一张牌，获得10金币。
  - **人部 (栋桡):** 对一名玩家造成8点伤害，你自己也损失4点生命值。
  - **天部 (过涉灭顶):** 弃掉3张手牌，对所有其他玩家造成5点伤害。
```json
{
  "id": "basic_28_da_guo",
  "name": "大过",
  "symbol": "☱☴",
  "sequence": 28,
  "pinyin": "da_guo",
  "strokes": 28,
  "type": "basic",
  "core_mechanism": {
    "name": "矫枉过正",
    "description": "行事过当，带来极端后果。",
    "variants": {
      "di": {
        "name": "枯杨生华",
        "effect": {
          "cost": [{ "action": "DISCARD_CARD", "params": { "target": "SELF", "count": 1 } }],
          "actions": [
            { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "gold", "value": 10 } }
          ]
        }
      },
      "ren": {
        "name": "栋桡",
        "effect": {
          "actions": [
            { "action": "DEAL_DAMAGE", "params": { "target": "OPPONENT_CHOICE_SINGLE", "value": 8 } },
            { "action": "LOSE_RESOURCE", "params": { "target": "SELF", "resource": "health", "value": 4 } }
          ]
        }
      },
      "tian": {
        "name": "过涉灭顶",
        "effect": {
          "cost": [
            { "action": "DISCARD_CARD", "params": { "target": "SELF", "count": 3 } }
          ],
          "actions": [
            { "action": "DEAL_DAMAGE", "params": { "target": "OPPONENT_ALL", "value": 5 } }
          ]
        }
      }
    }
  }
}
```

---
### **第29卦：《坎》 ☵☵ - 坎险**
**核心机制：【习坎之险】**
- **效果：** 重重险难，陷入困境。
- **爻辞变量：**
  - **地部 (习坎):** 你失去3金币和3生命值。
  - **人部 (求小得):** 弃一张牌。
  - **天部 (系用徽纆):** 你获得【禁锢】状态，下一轮不能移动或抽牌。
```json
{
  "id": "basic_29_kan",
  "name": "坎",
  "symbol": "☵☵",
  "sequence": 29,
  "pinyin": "kan",
  "strokes": 29,
  "type": "basic",
  "core_mechanism": {
    "name": "习坎之险",
    "description": "重重险难，陷入困境。",
    "variants": {
      "di": {
        "name": "习坎",
        "effect": {
          "actions": [
            { "action": "LOSE_RESOURCE", "params": { "target": "SELF", "resource": "gold", "value": 3 } },
            { "action": "LOSE_RESOURCE", "params": { "target": "SELF", "resource": "health", "value": 3 } }
          ]
        }
      },
      "ren": {
        "name": "求小得",
        "effect": {
          "actions": [
            { "action": "DISCARD_CARD", "params": { "target": "SELF", "count": 1 } }
          ]
        }
      },
      "tian": {
        "name": "系用徽纆",
        "effect": {
          "actions": [
            { "action": "APPLY_STATUS", "params": { "target": "SELF", "status_id": "IMPRISONED", "duration": 1 } }
          ]
        }
      }
    }
  }
}
```

---
### **第30卦：《离》 ☲☲ - 附丽**
**核心机制：【日月丽天】**
- **效果：** 如同光明附着于物，带来清晰和洞察。
- **爻辞变量：**
  - **地部 (黄离):** 查看一名玩家的所有手牌。
  - **人部 (日昃之离):** 支付2金币，抽2张牌。
  - **天部 (突如其来):** 对一名玩家造成4点伤害。
```json
{
  "id": "basic_30_li",
  "name": "离",
  "symbol": "☲☲",
  "sequence": 30,
  "pinyin": "li",
  "strokes": 30,
  "type": "basic",
  "core_mechanism": {
    "name": "日月丽天",
    "description": "如同光明附着于物，带来清晰和洞察。",
    "variants": {
      "di": {
        "name": "黄离",
        "effect": {
          "actions": [
            { "action": "LOOKUP", "params": { "target": "OPPONENT_CHOICE_SINGLE", "info_type": "hand_cards" } }
          ]
        }
      },
      "ren": {
        "name": "日昃之离",
        "effect": {
          "cost": [{ "resource": "gold", "value": 2 }],
          "actions": [
            { "action": "DRAW_CARD", "params": { "target": "SELF", "deck": "basic", "count": 2 } }
          ]
        }
      },
      "tian": {
        "name": "突如其来",
        "effect": {
          "actions": [
            { "action": "DEAL_DAMAGE", "params": { "target": "OPPONENT_CHOICE_SINGLE", "value": 4 } }
          ]
        }
      }
    }
  }
}
```

---
### **第31卦：《咸》 ☱☶ - 感应**
**核心机制：【心心相印】**
- **效果：** 双方产生感应，进行互动。
- **爻辞变量：**
  - **地部 (咸其拇):** 你和指定的一名玩家各抽一张牌。
  - **人部 (咸其股):** 你和指定的一名玩家各恢复3点生命值。
  - **天部 (咸其辅颊舌):** 你和指定的一名玩家各失去2金币。
```json
{
  "id": "basic_31_xian",
  "name": "咸",
  "symbol": "☱☶",
  "sequence": 31,
  "pinyin": "xian",
  "strokes": 31,
  "type": "basic",
  "core_mechanism": {
    "name": "心心相印",
    "description": "双方产生感应，进行互动。",
    "variants": {
      "di": {
        "name": "咸其拇",
        "effect": {
          "actions": [
            { "action": "DRAW_CARD", "params": { "target": "SELF", "deck": "basic", "count": 1 } },
            { "action": "DRAW_CARD", "params": { "target": "PLAYER_CHOICE_ANY", "deck": "basic", "count": 1 } }
          ]
        }
      },
      "ren": {
        "name": "咸其股",
        "effect": {
          "actions": [
            { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "health", "value": 3 } },
            { "action": "GAIN_RESOURCE", "params": { "target": "PLAYER_CHOICE_ANY", "resource": "health", "value": 3 } }
          ]
        }
      },
      "tian": {
        "name": "咸其辅颊舌",
        "effect": {
          "actions": [
            { "action": "LOSE_RESOURCE", "params": { "target": "SELF", "resource": "gold", "value": 2 } },
            { "action": "LOSE_RESOURCE", "params": { "target": "PLAYER_CHOICE_ANY", "resource": "gold", "value": 2 } }
          ]
        }
      }
    }
  }
}
```

---
### **第32卦：《恒》 ☳☴ - 持久**
**核心机制：【恒久之道】**
- **效果：** 持之以恒，产生持续性的效果。
- **爻辞变量：**
  - **地部 (浚恒):** 在接下来的3个回合开始时，你获得1金币。
  - **人部 (振恒):** 你获得一个持续2轮的【守护】状态，每轮抵挡1点伤害。
  - **天部 (不恒其德):** 你获得5金币，但弃一张牌。
```json
{
  "id": "basic_32_heng",
  "name": "恒",
  "symbol": "☳☴",
  "sequence": 32,
  "pinyin": "heng",
  "strokes": 32,
  "type": "basic",
  "core_mechanism": {
    "name": "恒久之道",
    "description": "持之以恒，产生持续性的效果。",
    "variants": {
      "di": {
        "name": "浚恒",
        "effect": {
          "actions": [
            { "action": "EXECUTE_LATER", "params": { "delay": "NEXT_TURN_START", "repeat": 3, "expiry_time": "3 ROUNDS", "effect": { "actions": [ { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "gold", "value": 1 } } ] } } }
          ]
        }
      },
      "ren": {
        "name": "振恒",
        "effect": {
          "actions": [
            { "action": "APPLY_STATUS", "params": { "target": "SELF", "status_id": "GUARD", "value": 1, "duration": 2 } }
          ]
        }
      },
      "tian": {
        "name": "不恒其德",
        "effect": {
          "actions": [
            { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "gold", "value": 5 } },
            { "action": "DISCARD_CARD", "params": { "target": "SELF", "count": 1 } }
          ]
        }
      }
    }
  }
}
```

---
### **第33卦：《遁》 ☰☶ - 退避**
**核心机制：【君子以远小人】**
- **效果：** 主动退避，以防灾祸。
- **爻辞变量：**
  - **地部 (好遁):** 你向后移动2格。
  - **人部 (嘉遁):** 弃一张牌，然后移动到你当前所在“部”的任意一个空格。
  - **天部 (肥遁):** 指定一名玩家，使其向远离你的方向移动1格。
```json
{
  "id": "basic_33_dun",
  "name": "遁",
  "symbol": "☰☶",
  "sequence": 33,
  "pinyin": "dun",
  "strokes": 33,
  "type": "basic",
  "core_mechanism": {
    "name": "君子以远小人",
    "description": "主动退避，以防灾祸。",
    "variants": {
      "di": {
        "name": "好遁",
        "effect": {
          "actions": [
            { "action": "MOVE", "params": { "target": "SELF", "move_type": "RETREAT", "value": 2 } }
          ]
        }
      },
      "ren": {
        "name": "嘉遁",
        "effect": {
          "cost": [{ "action": "DISCARD_CARD", "params": { "target": "SELF", "count": 1 } }],
          "actions": [
            { "action": "MOVE", "params": { "target": "SELF", "destination": "EMPTY_IN_SAME_DEPARTMENT" } }
          ]
        }
      },
      "tian": {
        "name": "肥遁",
        "effect": {
          "actions": [
            { "action": "MOVE", "params": { "target": "OPPONENT_CHOICE_SINGLE", "move_type": "AWAY_FROM_PLAYER", "player": "SELF", "value": 1 } }
          ]
        }
      }
    }
  }
}
```

---
### **第34卦：《大壮》 ☳☰ - 强盛**
**核心机制：【声势浩大】**
- **效果：** 力量强盛，势不可挡。
- **爻辞变量：**
  - **地部 (壮于趾):** 你本轮的下一次攻击额外造成2点伤害。
  - **人部 (藩决不羸):** 对一名玩家造成4点伤害。
  - **天部 (羝羊触藩):** 对所有其他玩家造成2点伤害。
```json
{
  "id": "basic_34_da_zhuang",
  "name": "大壮",
  "symbol": "☳☰",
  "sequence": 34,
  "pinyin": "da_zhuang",
  "strokes": 34,
  "type": "basic",
  "core_mechanism": {
    "name": "声势浩大",
    "description": "力量强盛，势不可挡。",
    "variants": {
      "di": {
        "name": "壮于趾",
        "effect": {
          "actions": [
            { "action": "APPLY_STATUS", "params": { "target": "SELF", "status_id": "DAMAGE_BOOST", "value": 2, "duration": "NEXT_ATTACK" } }
          ]
        }
      },
      "ren": {
        "name": "藩决不羸",
        "effect": {
          "actions": [
            { "action": "DEAL_DAMAGE", "params": { "target": "OPPONENT_CHOICE_SINGLE", "value": 4 } }
          ]
        }
      },
      "tian": {
        "name": "羝羊触藩",
        "effect": {
          "actions": [
            { "action": "DEAL_DAMAGE", "params": { "target": "OPPONENT_ALL", "value": 2 } }
          ]
        }
      }
    }
  }
}
```

---
### **第35卦：《晋》 ☲☷ - 前进**
**核心机制：【晋升之道】**
- **效果：** 不断前进，获得奖赏。
- **爻辞变量：**
  - **地部 (晋如):** 你向前移动2格。
  - **人部 (受兹介福):** 移动1格，然后抽一张牌。
  - **天部 (维用伐邑):** 移动1格，然后对新区域的一名玩家造成2点伤害。
```json
{
  "id": "basic_35_jin",
  "name": "晋",
  "symbol": "☲☷",
  "sequence": 35,
  "pinyin": "jin",
  "strokes": 35,
  "type": "basic",
  "core_mechanism": {
    "name": "晋升之道",
    "description": "不断前进，获得奖赏。",
    "variants": {
      "di": {
        "name": "晋如",
        "effect": {
          "actions": [
            { "action": "MOVE", "params": { "target": "SELF", "move_type": "NORMAL", "value": 2 } }
          ]
        }
      },
      "ren": {
        "name": "受兹介福",
        "effect": {
          "actions": [
            { "action": "MOVE", "params": { "target": "SELF", "move_type": "NORMAL", "value": 1 } },
            { "action": "DRAW_CARD", "params": { "target": "SELF", "deck": "basic", "count": 1 } }
          ]
        }
      },
      "tian": {
        "name": "维用伐邑",
        "effect": {
          "actions": [
            { "action": "MOVE", "params": { "target": "SELF", "move_type": "NORMAL", "value": 1 } },
            { "action": "DEAL_DAMAGE", "params": { "target": "PLAYER_IN_NEW_ZONE", "value": 2 } }
          ]
        }
      }
    }
  }
}
```

---
### **第36卦：《明夷》 ☷☲ - 光晦**
**核心机制：【晦暗之时】**
- **效果：** 光明受损，形势不利。
- **爻辞变量：**
  - **地部 (明夷于飞):** 指定一名玩家，其弃一张牌。
  - **人部 (入于左腹):** 查看一名玩家的手牌，并选择一张令其弃掉。
  - **天部 (不明晦):** 指定一名玩家，其下一轮不能使用卡牌的核心机制。
```json
{
  "id": "basic_36_ming_yi",
  "name": "明夷",
  "symbol": "☷☲",
  "sequence": 36,
  "pinyin": "ming_yi",
  "strokes": 36,
  "type": "basic",
  "core_mechanism": {
    "name": "晦暗之时",
    "description": "光明受损，形势不利。",
    "variants": {
      "di": {
        "name": "明夷于飞",
        "effect": {
          "actions": [
            { "action": "DISCARD_CARD", "params": { "target": "OPPONENT_CHOICE_SINGLE", "count": 1 } }
          ]
        }
      },
      "ren": {
        "name": "入于左腹",
        "effect": {
          "actions": [
            { "action": "DISCARD_CARD", "params": { "target": "OPPONENT_CHOICE_SINGLE", "source": "CHOICE_FROM_HAND" } }
          ]
        }
      },
      "tian": {
        "name": "不明晦",
        "effect": {
          "actions": [
            { "action": "APPLY_STATUS", "params": { "target": "OPPONENT_CHOICE_SINGLE", "status_id": "EFFECTS_LOCKED", "duration": 1 } }
          ]
        }
      }
    }
  }
}
```

---
### **第37卦：《家人》 ☴☲ - 家庭**
**核心机制：【家人之道】**
- **效果：** 强调家庭、盟友关系。
- **爻辞变量：**
  - **地部 (闲有家):** 若你有盟友，你和所有盟友各恢复3点生命值。
  - **人部 (妇子嘻嘻):** 选择一名盟友，你们各抽一张牌。
  - **天部 (富家):** 将你一半的金币（向上取整）转移给一名盟友。
```json
{
  "id": "basic_37_jia_ren",
  "name": "家人",
  "symbol": "☴☲",
  "sequence": 37,
  "pinyin": "jia_ren",
  "strokes": 37,
  "type": "basic",
  "core_mechanism": {
    "name": "家人之道",
    "description": "强调家庭、盟友关系。",
    "variants": {
      "di": {
        "name": "闲有家",
        "effect": {
          "condition": { "op": "PLAYER_HAS_ALLY" },
          "actions": [
            { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "health", "value": 3 } },
            { "action": "GAIN_RESOURCE", "params": { "target": "ALLY_FORMAL_ALL", "resource": "health", "value": 3 } }
          ]
        }
      },
      "ren": {
        "name": "妇子嘻嘻",
        "effect": {
          "actions": [
            { "action": "DRAW_CARD", "params": { "target": "SELF", "deck": "basic", "count": 1 } },
            { "action": "DRAW_CARD", "params": { "target": "ALLY_FORMAL_SINGLE_CHOICE", "deck": "basic", "count": 1 } }
          ]
        }
      },
      "tian": {
        "name": "富家",
        "effect": {
          "actions": [
            { "action": "TRANSFER_RESOURCE", "params": { "from": "SELF", "to": "ALLY_FORMAL_SINGLE_CHOICE", "resource": "gold", "value": { "op": "DIVIDE", "a": "VAR_SELF_GOLD", "b": 2, "round": "UP" } } }
          ]
        }
      }
    }
  }
}
```

---
### **第38卦：《睽》 ☲☱ - 对立**
**核心机制：【睽孤之象】**
- **效果：** 彼此对立，互相削弱。
- **爻辞变量：**
  - **地部 (见豕负涂):** 你和指定的一名玩家各失去3金币。
  - **人部 (睽孤):** 你和指定的一名玩家各弃一张随机手牌。
  - **天部 (交孚):** 你和指定的一名玩家交换彼此的阴阳值。
```json
{
  "id": "basic_38_kui",
  "name": "睽",
  "symbol": "☲☱",
  "sequence": 38,
  "pinyin": "kui",
  "strokes": 38,
  "type": "basic",
  "core_mechanism": {
    "name": "睽孤之象",
    "description": "彼此对立，互相削弱。",
    "variants": {
      "di": {
        "name": "见豕负涂",
        "effect": {
          "actions": [
            { "action": "LOSE_RESOURCE", "params": { "target": "SELF", "resource": "gold", "value": 3 } },
            { "action": "LOSE_RESOURCE", "params": { "target": "OPPONENT_CHOICE_SINGLE", "resource": "gold", "value": 3 } }
          ]
        }
      },
      "ren": {
        "name": "睽孤",
        "effect": {
          "actions": [
            { "action": "DISCARD_CARD", "params": { "target": "SELF", "count": 1, "source": "RANDOM" } },
            { "action": "DISCARD_CARD", "params": { "target": "OPPONENT_CHOICE_SINGLE", "count": 1, "source": "RANDOM" } }
          ]
        }
      },
      "tian": {
        "name": "交孚",
        "effect": {
          "actions": [
            { "action": "SWAP_RESOURCES", "params": { "target_a": "SELF", "target_b": "OPPONENT_CHOICE_SINGLE", "resource": "YIN_YANG_GAUGE", "atomic": true } }
          ]
        }
      }
    }
  }
}
```

---
### **第39卦：《蹇》 ☵☶ - 艰难**
**核心机制：【进退维谷】**
- **效果：** 行动艰难，充满阻碍。
- **爻辞变量：**
  - **地部 (往蹇来誉):** 在你当前位置创造一个【障碍】实体，持续1轮，任何玩家不能进入。
  - **人部 (王臣蹇蹇):** 指定一名玩家，其下一个行动的代价增加2金币。
  - **天部 (利见大人):** 指定一名玩家，其下一轮不能移动。
```json
{
  "id": "basic_39_jian",
  "name": "蹇",
  "symbol": "☵☶",
  "sequence": 39,
  "pinyin": "jian",
  "strokes": 39,
  "type": "basic",
  "core_mechanism": {
    "name": "进退维谷",
    "description": "行动艰难，充满阻碍。",
    "variants": {
      "di": {
        "name": "往蹇来誉",
        "effect": {
          "actions": [
            { "action": "CREATE_ENTITY", "params": { "entity_type": "HINDRANCE", "position": "SELF", "duration": 1, "properties": { "blocks_movement": { "for": "ALL_PLAYERS" } } } }
          ]
        }
      },
      "ren": {
        "name": "王臣蹇蹇",
        "effect": {
          "actions": [
            { "action": "APPLY_STATUS", "params": { "target": "OPPONENT_CHOICE_SINGLE", "status_id": "ACTION_COST_INCREASED", "value": 2, "duration": "NEXT_ACTION" } }
          ]
        }
      },
      "tian": {
        "name": "利见大人",
        "effect": {
          "actions": [
            { "action": "APPLY_STATUS", "params": { "target": "OPPONENT_CHOICE_SINGLE", "status_id": "CANNOT_MOVE", "duration": 1 } }
          ]
        }
      }
    }
  }
}
```

---
### **第40卦：《解》 ☳☵ - 解脱**
**核心机制：【解脱困境】**
- **效果：** 从困境中解脱出来。
- **爻辞变量：**
  - **地部 (田获三狐):** 移除你身上的一个负面状态。
  - **人部 (解而拇):** 移除任意一名玩家的一个负面状态。
  - **天部 (公用射隼):** 所有玩家各移除一个负面状态。
```json
{
  "id": "basic_40_xie",
  "name": "解",
  "symbol": "☳☵",
  "sequence": 40,
  "pinyin": "xie",
  "strokes": 40,
  "type": "basic",
  "core_mechanism": {
    "name": "解脱困境",
    "description": "从困境中解脱出来。",
    "variants": {
      "di": {
        "name": "田获三狐",
        "effect": {
          "actions": [
            { "action": "REMOVE_STATUS", "params": { "target": "SELF", "status_id": "ALL_NEGATIVE", "count": 1 } }
          ]
        }
      },
      "ren": {
        "name": "解而拇",
        "effect": {
          "actions": [
            { "action": "REMOVE_STATUS", "params": { "target": "PLAYER_CHOICE_ANY", "status_id": "ALL_NEGATIVE", "count": 1 } }
          ]
        }
      },
      "tian": {
        "name": "公用射隼",
        "effect": {
          "actions": [
            { "action": "REMOVE_STATUS", "params": { "target": "ALL_PLAYERS", "status_id": "ALL_NEGATIVE", "count": 1 } }
          ]
        }
      }
    }
  }
}
```

---
### **第41卦：《损》 ☶☱ - 减损**
**核心机制：【损有余】**
- **效果：** 减损一部分以求得平衡。
- **爻辞变量：**
  - **地部 (遄事):** 指定一名玩家，其失去4金币。
  - **人部 (损其疾):** 指定一名玩家，其失去4生命值。
  - **天部 (三人行):** 所有其他玩家各失去2金币。
```json
{
  "id": "basic_41_sun",
  "name": "损",
  "symbol": "☶☱",
  "sequence": 41,
  "pinyin": "sun",
  "strokes": 41,
  "type": "basic",
  "core_mechanism": {
    "name": "损有余",
    "description": "减损一部分以求得平衡。",
    "variants": {
      "di": {
        "name": "遄事",
        "effect": {
          "actions": [
            { "action": "LOSE_RESOURCE", "params": { "target": "OPPONENT_CHOICE_SINGLE", "resource": "gold", "value": 4 } }
          ]
        }
      },
      "ren": {
        "name": "损其疾",
        "effect": {
          "actions": [
            { "action": "LOSE_RESOURCE", "params": { "target": "OPPONENT_CHOICE_SINGLE", "resource": "health", "value": 4 } }
          ]
        }
      },
      "tian": {
        "name": "三人行",
        "effect": {
          "actions": [
            { "action": "LOSE_RESOURCE", "params": { "target": "OPPONENT_ALL", "resource": "gold", "value": 2 } }
          ]
        }
      }
    }
  }
}
```

---
### **第42卦：《益》 ☴☳ - 增益**
**核心机制：【益不足】**
- **效果：** 增益自己以求发展。
- **爻辞变量：**
  - **地部 (元吉):** 你获得4金币。
  - **人部 (有孚惠心):** 你恢复4点生命值。
  - **天部 (立心勿恒):** 你和你所有的盟友各获得2金币。
```json
{
  "id": "basic_42_yi",
  "name": "益",
  "symbol": "☴☳",
  "sequence": 42,
  "pinyin": "yi",
  "strokes": 42,
  "type": "basic",
  "core_mechanism": {
    "name": "益不足",
    "description": "增益自己以求发展。",
    "variants": {
      "di": {
        "name": "元吉",
        "effect": {
          "actions": [
            { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "gold", "value": 4 } }
          ]
        }
      },
      "ren": {
        "name": "有孚惠心",
        "effect": {
          "actions": [
            { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "health", "value": 4 } }
          ]
        }
      },
      "tian": {
        "name": "立心勿恒",
        "effect": {
          "actions": [
            { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "gold", "value": 2 } },
            { "action": "GAIN_RESOURCE", "params": { "target": "ALLY_FORMAL_ALL", "resource": "gold", "value": 2 } }
          ]
        }
      }
    }
  }
}
```

---
### **第43卦：《夬》 ☱☰ - 决断**
**核心机制：【刚决柔也】**
- **效果：** 以强硬手段做出决断。
- **爻辞变量：**
  - **地部 (壮于前趾):** 摧毁场上的一个实体。
  - **人部 (扬于王庭):** 弃3张牌，对一名玩家造成10点伤害。
  - **天部 (无号):** 你本轮的下一个行动无法被响应或无效。
```json
{
  "id": "basic_43_guai",
  "name": "夬",
  "symbol": "☱☰",
  "sequence": 43,
  "pinyin": "guai",
  "strokes": 43,
  "type": "basic",
  "core_mechanism": {
    "name": "刚决柔也",
    "description": "以强硬手段做出决断。",
    "variants": {
      "di": {
        "name": "壮于前趾",
        "effect": {
          "actions": [
            { "action": "DESTROY_ENTITY", "params": { "target_entity_id": "CHOICE" } }
          ]
        }
      },
      "ren": {
        "name": "扬于王庭",
        "effect": {
          "cost": [{ "action": "DISCARD_CARD", "params": { "target": "SELF", "count": 3 } }],
          "actions": [
            { "action": "DEAL_DAMAGE", "params": { "target": "OPPONENT_CHOICE_SINGLE", "value": 10 } }
          ]
        }
      },
      "tian": {
        "name": "无号",
        "effect": {
          "actions": [
            { "action": "APPLY_STATUS", "params": { "target": "SELF", "status_id": "UNSTOPPABLE", "duration": "NEXT_ACTION" } }
          ]
        }
      }
    }
  }
}
```

---
### **第44卦：《姤》 ☰☴ - 相遇**
**核心机制：【不期而遇】**
- **效果：** 意想不到的相遇。
- **爻辞变量：**
  - **地部 (系于金柅):** 移动到随机一名其他玩家所在的格子。
  - **人部 (包有鱼):** 你抽一张牌，随机一名其他玩家也抽一张牌。
  - **天部 (以杞包瓜):** 你和随机一名其他玩家互相查看对方的手牌。
```json
{
  "id": "basic_44_gou",
  "name": "姤",
  "symbol": "☰☴",
  "sequence": 44,
  "pinyin": "gou",
  "strokes": 44,
  "type": "basic",
  "core_mechanism": {
    "name": "不期而遇",
    "description": "意想不到的相遇。",
    "variants": {
      "di": {
        "name": "系于金柅",
        "effect": {
          "actions": [
            { "action": "MOVE", "params": { "target": "SELF", "destination": "PLAYER_ZONE", "player": "OPPONENT_RANDOM" } }
          ]
        }
      },
      "ren": {
        "name": "包有鱼",
        "effect": {
          "actions": [
            { "action": "DRAW_CARD", "params": { "target": "SELF", "deck": "basic", "count": 1 } },
            { "action": "DRAW_CARD", "params": { "target": "OPPONENT_RANDOM", "deck": "basic", "count": 1 } }
          ]
        }
      },
      "tian": {
        "name": "以杞包瓜",
        "effect": {
          "actions": [
            { "action": "LOOKUP", "params": { "target": "SELF", "info_type": "hand_cards", "other_player": "OPPONENT_RANDOM" } },
            { "action": "LOOKUP", "params": { "target": "OPPONENT_RANDOM", "info_type": "hand_cards", "other_player": "SELF" } }
          ]
        }
      }
    }
  }
}
```

---
### **第45卦：《萃》 ☱☷ - 聚集**
**核心机制：【荟萃一堂】**
- **效果：** 将力量或人员聚集起来。
- **爻辞变量：**
  - **地部 (引吉):** 所有其他玩家向你的位置移动一格。
  - **人部 (萃如):** 你获得等同于场上玩家数量的金币。
  - **天部 (王假有庙):** 将你所有的盟友移动到你所在的格子。
```json
{
  "id": "basic_45_cui",
  "name": "萃",
  "symbol": "☱☷",
  "sequence": 45,
  "pinyin": "cui",
  "strokes": 45,
  "type": "basic",
  "core_mechanism": {
    "name": "荟萃一堂",
    "description": "将力量或人员聚集起来。",
    "variants": {
      "di": {
        "name": "引吉",
        "effect": {
          "actions": [
            { "action": "MOVE", "params": { "target": "OPPONENT_ALL", "move_type": "TOWARDS_PLAYER", "player": "SELF", "value": 1 } }
          ]
        }
      },
      "ren": {
        "name": "萃如",
        "effect": {
          "actions": [
            { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "gold", "value": { "op": "COUNT", "target": "ALL_PLAYERS" } } }
          ]
        }
      },
      "tian": {
        "name": "王假有庙",
        "effect": {
          "condition": { "op": "PLAYER_HAS_ALLY" },
          "actions": [
            { "action": "MOVE", "params": { "target": "ALLY_FORMAL_ALL", "destination": "PLAYER_ZONE", "player": "SELF" } }
          ]
        }
      }
    }
  }
}
```

---
### **第46卦：《升》 ☷☴ - 上升**
**核心机制：【步步高升】**
- **效果：** 地位或力量的上升。
- **爻辞变量：**
  - **地部 (允升):** 若你在【地部】，移动到【人部】的一个随机空格。
  - **人部 (升阶):** 若你在【人部】，移动到【天部】的一个随机空格。
  - **天部 (冥升):** 你获得5金币。
```json
{
  "id": "basic_46_sheng",
  "name": "升",
  "symbol": "☷☴",
  "sequence": 46,
  "pinyin": "sheng",
  "strokes": 46,
  "type": "basic",
  "core_mechanism": {
    "name": "步步高升",
    "description": "地位或力量的上升。",
    "variants": {
      "di": {
        "name": "允升",
        "effect": {
          "condition": { "op": "IS_IN_DEPARTMENT", "params": { "target": "SELF", "department": "di" } },
          "actions": [
            { "action": "MOVE", "params": { "target": "SELF", "destination": "RANDOM_EMPTY_IN_DEPARTMENT", "department": "ren" } }
          ]
        }
      },
      "ren": {
        "name": "升阶",
        "effect": {
          "condition": { "op": "IS_IN_DEPARTMENT", "params": { "target": "SELF", "department": "ren" } },
          "actions": [
            { "action": "MOVE", "params": { "target": "SELF", "destination": "RANDOM_EMPTY_IN_DEPARTMENT", "department": "tian" } }
          ]
        }
      },
      "tian": {
        "name": "冥升",
        "effect": {
          "actions": [
            { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "gold", "value": 5 } }
          ]
        }
      }
    }
  }
}
```

---
### **第47卦：《困》 ☱☵ - 困顿**
**核心机制：【身陷困境】**
- **效果：** 资源被耗尽，行动受限。
- **爻辞变量：**
  - **地部 (臀困于株木):** 你失去2金币。
  - **人部 (困于酒食):** 你弃一张牌。
  - **天部 (困于葛藟):** 你失去2生命值。
```json
{
  "id": "basic_47_kun",
  "name": "困",
  "symbol": "☱☵",
  "sequence": 47,
  "pinyin": "kun",
  "strokes": 47,
  "type": "basic",
  "core_mechanism": {
    "name": "身陷困境",
    "description": "资源被耗尽，行动受限。",
    "variants": {
      "di": {
        "name": "臀困于株木",
        "effect": {
          "actions": [
            { "action": "LOSE_RESOURCE", "params": { "target": "SELF", "resource": "gold", "value": 2 } }
          ]
        }
      },
      "ren": {
        "name": "困于酒食",
        "effect": {
          "actions": [
            { "action": "DISCARD_CARD", "params": { "target": "SELF", "count": 1 } }
          ]
        }
      },
      "tian": {
        "name": "困于葛藟",
        "effect": {
          "actions": [
            { "action": "LOSE_RESOURCE", "params": { "target": "SELF", "resource": "health", "value": 2 } }
          ]
        }
      }
    }
  }
}
```

---
### **第48卦：《井》 ☵☴ - 水井**
**核心机制：【井养不穷】**
- **效果：** 如同水井，提供源源不断的资源。
- **爻辞变量：**
  - **地部 (井渫不食):** 在你当前位置创造一个【甘泉井】实体，任何结束回合在此的玩家获得2金币。
  - **人部 (井谷射鲋):** 抽2张基础牌。
  - **天部 (井收勿幕):** 恢复5点生命值。
```json
{
  "id": "basic_48_jing",
  "name": "井",
  "symbol": "☵☴",
  "sequence": 48,
  "pinyin": "jing",
  "strokes": 48,
  "type": "basic",
  "core_mechanism": {
    "name": "井养不穷",
    "description": "如同水井，提供源源不断的资源。",
    "variants": {
      "di": {
        "name": "井渫不食",
        "effect": {
          "actions": [
            { "action": "CREATE_ENTITY", "params": { "entity_type": "WELLSPRING", "position": "SELF", "is_permanent": true, "properties": { "name": "甘泉井", "on_turn_end_effect": { "actions": [ { "action": "GAIN_RESOURCE", "params": { "target": "EVENT_SOURCE_PLAYER", "resource": "gold", "value": 2 } } ] } } } }
          ]
        }
      },
      "ren": {
        "name": "井谷射鲋",
        "effect": {
          "actions": [
            { "action": "DRAW_CARD", "params": { "target": "SELF", "deck": "basic", "count": 2 } }
          ]
        }
      },
      "tian": {
        "name": "井收勿幕",
        "effect": {
          "actions": [
            { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "health", "value": 5 } }
          ]
        }
      }
    }
  }
}
```

---
### **第49卦：《革》 ☱☲ - 变革**
**核心机制：【顺天应人】**
- **效果：** 带来巨大的变革。
- **爻辞变量：**
  - **地部 (巳日乃孚):** 交换场上两名指定玩家的位置（非盟友）。
  - **人部 (大人虎变):** 所有玩家弃掉所有手牌，然后各抽3张。
  - **天部 (君子豹变):** 从下一轮开始，回合顺序反转。
```json
{
  "id": "basic_49_ge",
  "name": "革",
  "symbol": "☱☲",
  "sequence": 49,
  "pinyin": "ge",
  "strokes": 49,
  "type": "basic",
  "core_mechanism": {
    "name": "顺天应人",
    "description": "带来巨大的变革。",
    "variants": {
      "di": {
        "name": "巳日乃孚",
        "effect": {
          "actions": [
            { "action": "SWAP_POSITION", "params": { "target_a": "PLAYER_CHOICE_ANY_NON_ALLY", "target_b": "PLAYER_CHOICE_ANY_NON_ALLY", "atomic": true } }
          ]
        }
      },
      "ren": {
        "name": "大人虎变",
        "effect": {
          "actions": [
            { "action": "DISCARD_CARD", "params": { "target": "ALL_PLAYERS", "count": "ALL" } },
            { "action": "DRAW_CARD", "params": { "target": "ALL_PLAYERS", "deck": "basic", "count": 3 } }
          ]
        }
      },
      "tian": {
        "name": "君子豹变",
        "effect": {
          "actions": [
            { "action": "MODIFY_RULE", "params": { "rule_id": "TURN_ORDER_REVERSED", "scope": "GLOBAL", "mutation": { "type": "SET_BOOLEAN", "value": true }, "duration": "PERMANENT" } }
          ]
        }
      }
    }
  }
}
```

---
### **第50卦：《鼎》 ☲☴ - 宝鼎**
**核心机制：【鼎鼐调和】**
- **效果：** 烹饪食物，凝聚力量。
- **爻辞变量：**
  - **地部 (鼎颠趾):** 弃掉最多3张牌，每弃一张，便获得2金币。
  - **人部 (鼎耳革):** 支付5金币，抽3张牌。
  - **天部 (玉铉大吉):** 选择一名其他玩家，你们各恢复5点生命值。
```json
{
  "id": "basic_50_ding",
  "name": "鼎",
  "symbol": "☲☴",
  "sequence": 50,
  "pinyin": "ding",
  "strokes": 50,
  "type": "basic",
  "core_mechanism": {
    "name": "鼎鼐调和",
    "description": "烹饪食物，凝聚力量。",
    "variants": {
      "di": {
        "name": "鼎颠趾",
        "effect": {
          "actions": [
            { "action": "CHOICE", "params": { "target": "SELF", "options": [
              { "description": "弃1张换2金币", "cost": [{"action":"DISCARD_CARD", "params":{"count":1}}], "effect": {"actions":[{"action":"GAIN_RESOURCE","params":{"resource":"gold","value":2}}]}},
              { "description": "弃2张换4金币", "cost": [{"action":"DISCARD_CARD", "params":{"count":2}}], "effect": {"actions":[{"action":"GAIN_RESOURCE","params":{"resource":"gold","value":4}}]}},
              { "description": "弃3张换6金币", "cost": [{"action":"DISCARD_CARD", "params":{"count":3}}], "effect": {"actions":[{"action":"GAIN_RESOURCE","params":{"resource":"gold","value":6}}]}}
            ]}}
          ]
        }
      },
      "ren": {
        "name": "鼎耳革",
        "effect": {
          "cost": [{ "resource": "gold", "value": 5 }],
          "actions": [
            { "action": "DRAW_CARD", "params": { "target": "SELF", "deck": "basic", "count": 3 } }
          ]
        }
      },
      "tian": {
        "name": "玉铉大吉",
        "effect": {
          "actions": [
            { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "health", "value": 5 } },
            { "action": "GAIN_RESOURCE", "params": { "target": "PLAYER_CHOICE_ANY", "resource": "health", "value": 5 } }
          ]
        }
      }
    }
  }
}
```

---
### **第51卦：《震》 ☳☳ - 震动**
**核心机制：【震惊百里】**
- **效果：** 带来突发的震动和混乱。
- **爻辞变量：**
  - **地部 (震索索):** 你所在区域的所有玩家（包括你）各失去2点生命值。
  - **人部 (震遂泥):** 所有玩家各弃一张随机手牌。
  - **天部 (震惊百里):** 所有其他玩家向随机方向移动1格。
```json
{
  "id": "basic_51_zhen",
  "name": "震",
  "symbol": "☳☳",
  "sequence": 51,
  "pinyin": "zhen",
  "strokes": 51,
  "type": "basic",
  "core_mechanism": {
    "name": "震惊百里",
    "description": "带来突发的震动和混乱。",
    "variants": {
      "di": {
        "name": "震索索",
        "effect": {
          "actions": [
            { "action": "LOSE_RESOURCE", "params": { "target": "PLAYERS_IN_SAME_ZONE", "resource": "health", "value": 2 } }
          ]
        }
      },
      "ren": {
        "name": "震遂泥",
        "effect": {
          "actions": [
            { "action": "DISCARD_CARD", "params": { "target": "ALL_PLAYERS", "count": 1, "source": "RANDOM" } }
          ]
        }
      },
      "tian": {
        "name": "震惊百里",
        "effect": {
          "actions": [
            { "action": "MOVE", "params": { "target": "OPPONENT_ALL", "move_type": "RANDOM_DIRECTION", "value": 1 } }
          ]
        }
      }
    }
  }
}
```

---
### **第52卦：《艮》 ☶☶ - 停止**
**核心机制：【艮止之道】**
- **效果：** 停止行动，保持静止。
- **爻辞变量：**
  - **地部 (艮其背):** 你下一轮不能移动，但在下一轮开始时获得5金币。
  - **人部 (不获其身):** 指定一名玩家，其下一轮不能打出卡牌。
  - **天部 (时行则行):** 本轮内，所有玩家都不能被卡牌效果移动。
```json
{
  "id": "basic_52_gen",
  "name": "艮",
  "symbol": "☶☶",
  "sequence": 52,
  "pinyin": "gen",
  "strokes": 52,
  "type": "basic",
  "core_mechanism": {
    "name": "艮止之道",
    "description": "停止行动，保持静止。",
    "variants": {
      "di": {
        "name": "艮其背",
        "effect": {
          "actions": [
            { "action": "APPLY_STATUS", "params": { "target": "SELF", "status_id": "CANNOT_MOVE", "duration": 1 } },
            { "action": "EXECUTE_LATER", "params": { "delay": "NEXT_TURN_START", "expiry_time": "1 ROUND", "effect": { "actions": [ { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "gold", "value": 5 } } ] } } }
          ]
        }
      },
      "ren": {
        "name": "不获其身",
        "effect": {
          "actions": [
            { "action": "APPLY_STATUS", "params": { "target": "OPPONENT_CHOICE_SINGLE", "status_id": "CARDS_LOCKED", "duration": 1 } }
          ]
        }
      },
      "tian": {
        "name": "时行则行",
        "effect": {
          "actions": [
            { "action": "MODIFY_RULE", "params": { "rule_id": "CARD_EFFECT_MOVEMENT_BLOCKED", "scope": "GLOBAL", "mutation": { "type": "SET_BOOLEAN", "value": true }, "duration": 1 } }
          ]
        }
      }
    }
  }
}
```

---
### **第53卦：《渐》 ☴☶ - 渐进**
**核心机制：【循序渐进】**
- **效果：** 逐步发展，最终成功。
- **爻辞变量：**
  - **地部 (鸿渐于干):** 获得2金币。
  - **人部 (鸿渐于磐):** 获得4金币。
  - **天部 (鸿渐于陆):** 获得6金币。
```json
{
  "id": "basic_53_jian",
  "name": "渐",
  "symbol": "☴☶",
  "sequence": 53,
  "pinyin": "jian",
  "strokes": 53,
  "type": "basic",
  "core_mechanism": {
    "name": "循序渐进",
    "description": "逐步发展，最终成功。",
    "variants": {
      "di": {
        "name": "鸿渐于干",
        "effect": {
          "actions": [
            { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "gold", "value": 2 } }
          ]
        }
      },
      "ren": {
        "name": "鸿渐于磐",
        "effect": {
          "actions": [
            { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "gold", "value": 4 } }
          ]
        }
      },
      "tian": {
        "name": "鸿渐于陆",
        "effect": {
          "actions": [
            { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "gold", "value": 6 } }
          ]
        }
      }
    }
  }
}
```

---
### **第54卦：《归妹》 ☳☱ - 归妹**
**核心机制：【以祉元吉】**
- **效果：** 少女出嫁，有不正之象，但亦有福祉。
- **爻辞变量：**
  - **地部 (归妹以娣):** 你和指定的一名玩家各抽一张牌。
  - **人部 (帝乙归妹):** 你失去3金币，但恢复6生命值。
  - **天部 (月几望):** 指定一名玩家，你们交换手牌。
```json
{
  "id": "basic_54_gui_mei",
  "name": "归妹",
  "symbol": "☳☱",
  "sequence": 54,
  "pinyin": "gui_mei",
  "strokes": 54,
  "type": "basic",
  "core_mechanism": {
    "name": "以祉元吉",
    "description": "少女出嫁，有不正之象，但亦有福祉。",
    "variants": {
      "di": {
        "name": "归妹以娣",
        "effect": {
          "actions": [
            { "action": "DRAW_CARD", "params": { "target": "SELF", "deck": "basic", "count": 1 } },
            { "action": "DRAW_CARD", "params": { "target": "PLAYER_CHOICE_ANY", "deck": "basic", "count": 1 } }
          ]
        }
      },
      "ren": {
        "name": "帝乙归妹",
        "effect": {
          "actions": [
            { "action": "LOSE_RESOURCE", "params": { "target": "SELF", "resource": "gold", "value": 3 } },
            { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "health", "value": 6 } }
          ]
        }
      },
      "tian": {
        "name": "月几望",
        "effect": {
          "actions": [
            { "action": "SWAP_HAND_CARDS", "params": { "target": "SELF", "other_player": "OPPONENT_CHOICE_SINGLE", "count": "ALL", "atomic": true } }
          ]
        }
      }
    }
  }
}
```

---
### **第55卦：《丰》 ☳☲ - 丰盛**
**核心机制：【丰功伟业】**
- **效果：** 日中见斗，象征极盛之时。
- **爻辞变量：**
  - **地部 (丰其沛):** 你获得10金币。
  - **人部 (丰其屋):** 你获得一个【宝鼎】实体，每轮开始时产出1金币。
  - **天部 (天际翔也):** 获得5金币，并可立即额外移动3格。
```json
{
  "id": "basic_55_feng",
  "name": "丰",
  "symbol": "☳☲",
  "sequence": 55,
  "pinyin": "feng",
  "strokes": 55,
  "type": "basic",
  "core_mechanism": {
    "name": "丰功伟业",
    "description": "日中见斗，象征极盛之时。",
    "variants": {
      "di": {
        "name": "丰其沛",
        "effect": {
          "actions": [
            { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "gold", "value": 10 } }
          ]
        }
      },
      "ren": {
        "name": "丰其屋",
        "effect": {
          "actions": [
            { "action": "CREATE_ENTITY", "params": { "entity_type": "TREASURE_CAULDRON", "position": "SELF", "is_permanent": true, "properties": { "name": "宝鼎", "on_turn_start_effect": { "actions": [ { "action": "GAIN_RESOURCE", "params": { "target": "OWNER", "resource": "gold", "value": 1 } } ] } } } }
          ]
        }
      },
      "tian": {
        "name": "天际翔也",
        "effect": {
          "actions": [
            { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "gold", "value": 5 } },
            { "action": "MOVE", "params": { "target": "SELF", "move_type": "NORMAL", "value": 3 } }
          ]
        }
      }
    }
  }
}
```

---
### **第56卦：《旅》 ☲☶ - 旅人**
**核心机制：【行旅之道】**
- **效果：** 旅途中的见闻与得失。
- **爻辞变量：**
  - **地部 (旅琐琐):** 失去1金币。
  - **人部 (得其资斧):** 获得3金币。
  - **天部 (终誉命):** 获得5金币和1点声望。
```json
{
  "id": "basic_56_lv",
  "name": "旅",
  "symbol": "☲☶",
  "sequence": 56,
  "pinyin": "lv",
  "strokes": 56,
  "type": "basic",
  "core_mechanism": {
    "name": "行旅之道",
    "description": "旅途中的见闻与得失。",
    "variants": {
      "di": {
        "name": "旅琐琐",
        "effect": {
          "actions": [
            { "action": "LOSE_RESOURCE", "params": { "target": "SELF", "resource": "gold", "value": 1 } }
          ]
        }
      },
      "ren": {
        "name": "得其资斧",
        "effect": {
          "actions": [
            { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "gold", "value": 3 } }
          ]
        }
      },
      "tian": {
        "name": "终誉命",
        "effect": {
          "actions": [
            { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "gold", "value": 5 } },
            { "action": "APPLY_STATUS", "params": { "target": "SELF", "status_id": "PRESTIGE", "value": 1, "is_permanent": true } }
          ]
        }
      }
    }
  }
}
```

---
### **第57卦：《巽》 ☴☴ - 顺从**
**核心机制：【随风而入】**
- **效果：** 顺势而为，悄无声息地渗透。
- **爻辞变量：**
  - **地部 (进退):** 你可以向前或向后移动1格。
  - **人部 (纷若):** 查看一名玩家的手牌。
  - **天部 (巽在床下):** 指定一名玩家，其失去3点生命值。
```json
{
  "id": "basic_57_xun",
  "name": "巽",
  "symbol": "☴☴",
  "sequence": 57,
  "pinyin": "xun",
  "strokes": 57,
  "type": "basic",
  "core_mechanism": {
    "name": "随风而入",
    "description": "顺势而为，悄无声息地渗透。",
    "variants": {
      "di": {
        "name": "进退",
        "effect": {
          "actions": [
            { "action": "CHOICE", "params": { "target": "SELF", "options": [
              { "description": "前进1格", "effect": {"actions":[{"action":"MOVE", "params":{"target":"SELF", "move_type":"NORMAL", "value":1}}]}},
              { "description": "后退1格", "effect": {"actions":[{"action":"MOVE", "params":{"target":"SELF", "move_type":"RETREAT", "value":1}}]}}
            ]}}
          ]
        }
      },
      "ren": {
        "name": "纷若",
        "effect": {
          "actions": [
            { "action": "LOOKUP", "params": { "target": "OPPONENT_CHOICE_SINGLE", "info_type": "hand_cards" } }
          ]
        }
      },
      "tian": {
        "name": "巽在床下",
        "effect": {
          "actions": [
            { "action": "LOSE_RESOURCE", "params": { "target": "OPPONENT_CHOICE_SINGLE", "resource": "health", "value": 3 } }
          ]
        }
      }
    }
  }
}
```

---
### **第58卦：《兑》 ☱☱ - 喜悦**
**核心机制：【和悦之道】**
- **效果：** 带来喜悦与和睦。
- **爻辞变量：**
  - **地部 (和兑):** 你获得3金币。
  - **人部 (孚兑):** 你和一名指定的玩家各抽一张牌。
  - **天部 (引兑):** 你和所有盟友各恢复3点生命值。
```json
{
  "id": "basic_58_dui",
  "name": "兑",
  "symbol": "☱☱",
  "sequence": 58,
  "pinyin": "dui",
  "strokes": 58,
  "type": "basic",
  "core_mechanism": {
    "name": "和悦之道",
    "description": "带来喜悦与和睦。",
    "variants": {
      "di": {
        "name": "和兑",
        "effect": {
          "actions": [
            { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "gold", "value": 3 } }
          ]
        }
      },
      "ren": {
        "name": "孚兑",
        "effect": {
          "actions": [
            { "action": "DRAW_CARD", "params": { "target": "SELF", "deck": "basic", "count": 1 } },
            { "action": "DRAW_CARD", "params": { "target": "PLAYER_CHOICE_ANY", "deck": "basic", "count": 1 } }
          ]
        }
      },
      "tian": {
        "name": "引兑",
        "effect": {
          "actions": [
            { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "health", "value": 3 } },
            { "action": "GAIN_RESOURCE", "params": { "target": "ALLY_FORMAL_ALL", "resource": "health", "value": 3 } }
          ]
        }
      }
    }
  }
}
```

---
### **第59卦：《涣》 ☴☵ - 涣散**
**核心机制：【风行水上】**
- **效果：** 离散，化解。
- **爻辞变量：**
  - **地部 (涣奔其机):** 移除场上的一个非永久性实体。
  - **人部 (涣其群):** 所有玩家弃一张牌。
  - **天部 (涣其血):** 所有玩家失去2点生命值。
```json
{
  "id": "basic_59_huan",
  "name": "涣",
  "symbol": "☴☵",
  "sequence": 59,
  "pinyin": "huan",
  "strokes": 59,
  "type": "basic",
  "core_mechanism": {
    "name": "风行水上",
    "description": "离散，化解。",
    "variants": {
      "di": {
        "name": "涣奔其机",
        "effect": {
          "actions": [
            { "action": "DESTROY_ENTITY", "params": { "target_entity_id": "CHOICE_NON_PERMANENT" } }
          ]
        }
      },
      "ren": {
        "name": "涣其群",
        "effect": {
          "actions": [
            { "action": "DISCARD_CARD", "params": { "target": "ALL_PLAYERS", "count": 1 } }
          ]
        }
      },
      "tian": {
        "name": "涣其血",
        "effect": {
          "actions": [
            { "action": "LOSE_RESOURCE", "params": { "target": "ALL_PLAYERS", "resource": "health", "value": 2 } }
          ]
        }
      }
    }
  }
}
```

---
### **第60卦：《节》 ☵☱ - 节制**
**核心机制：【节制之道】**
- **效果：** 限制行为，有度则吉。
- **爻辞变量：**
  - **地部 (不出户庭):** 你本回合不能移动。
  - **人部 (不节):** 你失去3金币。
  - **天部 (甘节):** 本轮内，所有玩家抽牌上限-1。
```json
{
  "id": "basic_60_jie",
  "name": "节",
  "symbol": "☵☱",
  "sequence": 60,
  "pinyin": "jie",
  "strokes": 60,
  "type": "basic",
  "core_mechanism": {
    "name": "节制之道",
    "description": "限制行为，有度则吉。",
    "variants": {
      "di": {
        "name": "不出户庭",
        "effect": {
          "actions": [
            { "action": "APPLY_STATUS", "params": { "target": "SELF", "status_id": "CANNOT_MOVE", "duration": 1 } }
          ]
        }
      },
      "ren": {
        "name": "不节",
        "effect": {
          "actions": [
            { "action": "LOSE_RESOURCE", "params": { "target": "SELF", "resource": "gold", "value": 3 } }
          ]
        }
      },
      "tian": {
        "name": "甘节",
        "effect": {
          "actions": [
            { "action": "MODIFY_RULE", "params": { "rule_id": "HAND_LIMIT_DRAW", "scope": "GLOBAL", "mutation": { "type": "ADD_MODIFIER", "value": -1 }, "duration": 1 } }
          ]
        }
      }
    }
  }
}
```

---
### **第61卦：《中孚》 ☴☱ - 诚信**
**核心机制：【诚信之德】**
- **效果：** 以诚信感化万物。
- **爻辞变量：**
  - **地部 (得敌):** 若你有盟友，你获得5金币。
  - **人部 (月几望):** 指定一名玩家，若其阴阳值与你同号（均为正或均为负），你们各抽一张牌。
  - **天部 (翰音登于天):** 你获得【威望】状态。
```json
{
  "id": "basic_61_zhong_fu",
  "name": "中孚",
  "symbol": "☴☱",
  "sequence": 61,
  "pinyin": "zhong_fu",
  "strokes": 61,
  "type": "basic",
  "core_mechanism": {
    "name": "诚信之德",
    "description": "以诚信感化万物。",
    "variants": {
      "di": {
        "name": "得敌",
        "effect": {
          "condition": { "op": "PLAYER_HAS_ALLY" },
          "actions": [
            { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "gold", "value": 5 } }
          ]
        }
      },
      "ren": {
        "name": "月几望",
        "effect": {
          "condition": { "op": "COMPARE_YIN_YANG_SIGN", "params": { "target_a": "SELF", "target_b": "PLAYER_CHOICE_ANY" } },
          "actions": [
            { "action": "DRAW_CARD", "params": { "target": "SELF", "deck": "basic", "count": 1 } },
            { "action": "DRAW_CARD", "params": { "target": "EVENT_TARGET_PLAYER", "deck": "basic", "count": 1 } }
          ]
        }
      },
      "tian": {
        "name": "翰音登于天",
        "effect": {
          "actions": [
            { "action": "APPLY_STATUS", "params": { "target": "SELF", "status_id": "PRESTIGE", "is_permanent": true } }
          ]
        }
      }
    }
  }
}
```

---
### **第62卦：《小过》 ☳☶ - 小过**
**核心机制：【小有过失】**
- **效果：** 可以做小事，不宜做大事。
- **爻辞变量：**
  - **地部 (弗过):** 你失去1金币。
  - **人部 (遇其妣):** 你失去1点生命值。
  - **天部 (弗遇):** 抽一张牌，但对所有其他玩家展示它。
```json
{
  "id": "basic_62_xiao_guo",
  "name": "小过",
  "symbol": "☳☶",
  "sequence": 62,
  "pinyin": "xiao_guo",
  "strokes": 62,
  "type": "basic",
  "core_mechanism": {
    "name": "小有过失",
    "description": "可以做小事，不宜做大事。",
    "variants": {
      "di": {
        "name": "弗过",
        "effect": {
          "actions": [
            { "action": "LOSE_RESOURCE", "params": { "target": "SELF", "resource": "gold", "value": 1 } }
          ]
        }
      },
      "ren": {
        "name": "遇其妣",
        "effect": {
          "actions": [
            { "action": "LOSE_RESOURCE", "params": { "target": "SELF", "resource": "health", "value": 1 } }
          ]
        }
      },
      "tian": {
        "name": "弗遇",
        "effect": {
          "actions": [
            { "action": "DRAW_CARD", "params": { "target": "SELF", "deck": "basic", "count": 1, "reveal": true } }
          ]
        }
      }
    }
  }
}
```

---
### **第六十三卦：《既济》 ☵☲ - 功成**
**核心机制：【水火既济】**
- **效果：** 若你的阴阳指示条为0且五行资源平衡，你获得100胜利点。每场游戏只能成功宣告一次。
- **爻辞变量：**
  - **地部:** 宣告成功时，额外获得30金币。
  - **人部:** 宣告成功时，额外获得30金币。
  - **天部:** 宣告成功时，额外获得30金币。
```json
{
  "id": "basic_63_jiji",
  "name": "既济",
  "symbol": "☵☲",
  "sequence": 63,
  "pinyin": "jiji",
  "type": "basic",
  "usage_limit": {
    "scope": "GAME",
    "count": 1,
    "reset_timing": "NEVER"
  },
  "core_mechanism": {
    "name": "水火既济",
    "description": "在满足特定条件下获得大量胜利点数。",
    "variants": {
      "di": {
        "name": "地",
        "effect": {
          "condition": { "op": "AND", "conditions": [ { "op": "PLAYER_HAS_FLAG", "params": { "flag": "YIN_YANG_IS_ZERO" } }, { "op": "PLAYER_HAS_FLAG", "params": { "flag": "FIVE_ELEMENTS_BALANCED" } } ] },
          "actions": [ { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "VICTORY_POINTS", "value": 100 } }, { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "gold", "value": 30 } } ]
        }
      },
      "ren": {
        "name": "人",
        "effect": {
          "condition": { "op": "AND", "conditions": [ { "op": "PLAYER_HAS_FLAG", "params": { "flag": "YIN_YANG_IS_ZERO" } }, { "op": "PLAYER_HAS_FLAG", "params": { "flag": "FIVE_ELEMENTS_BALANCED" } } ] },
          "actions": [ { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "VICTORY_POINTS", "value": 100 } }, { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "gold", "value": 30 } } ]
        }
      },
      "tian": {
        "name": "天",
        "effect": {
          "condition": { "op": "AND", "conditions": [ { "op": "PLAYER_HAS_FLAG", "params": { "flag": "YIN_YANG_IS_ZERO" } }, { "op": "PLAYER_HAS_FLAG", "params": { "flag": "FIVE_ELEMENTS_BALANCED" } } ] },
          "actions": [ { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "VICTORY_POINTS", "value": 100 } }, { "action": "GAIN_RESOURCE", "params": { "target": "SELF", "resource": "gold", "value": 30 } } ]
        }
      }
    }
  }
}
```

---

### **第六十四卦：《未济》 ☲☵ - 未完**
**核心机制：【火水未济】**
- **效果：** 颠倒阴阳或交换资源。
- **爻辞变量：**
  - **地部:** 你的阴阳指示条的数值翻转（例如，-3变为+3）。
  - **人部 (震用伐鬼方):** 你可以改变用法：指定一名其他玩家，你们双方**交换彼此的弃牌堆**。此效果**每场游戏只能发动一次**。
  - **天部:** 你与指定的一名其他玩家交换所有金币。
```json
{
  "id": "basic_64_weiji",
  "name": "未济",
  "symbol": "☲☵",
  "sequence": 64,
  "pinyin": "weiji",
  "type": "basic",
  "core_mechanism": {
    "name": "火水未济",
    "description": "颠倒阴阳或交换资源。",
    "variants": {
      "di": {
        "name": "倒置",
        "effect": {
          "actions": [{ "action": "MODIFY_RULE", "params": { "rule_id": "YIN_YANG_SYSTEM_REVERSED", "scope": "SELF", "mutation": { "type": "SET_BOOLEAN", "value": true }, "duration": 1 } }]
        }
      },
      "ren": {
        "name": "震用伐鬼方",
        "usage_limit": {
          "scope": "GAME",
          "count": 1,
          "reset_timing": "NEVER"
        },
        "effect": {
          "actions": [
            {
              "action": "SWAP_DISCARD_PILES",
              "params": {
                "target_a": "SELF",
                "target_b": "OPPONENT_CHOICE_SINGLE",
                "atomic": true
              }
            }
          ]
        }
      },
      "tian": {
        "name": "易位",
        "effect": {
          "actions": [{ "action": "SWAP_RESOURCES", "params": { "target_a": "SELF", "target_b": "OPPONENT_CHOICE_SINGLE", "resource": "gold", "atomic": true } }]
        }
      }
    }
  }
}
```
---
---
**修订总结:**
所有卡牌描述都已更新，以符合新的规则和逻辑架构。关键漏洞（如《谦》的无限循环）已被堵上，模糊的描述（如《坤》的复制）已被澄清，无法实现的效果（如《蹇》）已通过新系统重构。现在的卡牌描述文档是清晰、平衡且可实现的。