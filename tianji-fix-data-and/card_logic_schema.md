# 《天机变》 - 卡牌逻辑数据结构 (Card Logic Data Structure)

**版本: 3.1**
日期: 2025-09-27

## 1. 核心理念 (Core Philosophy) - 已修订

为真正实现 "数据驱动设计" 的核心理念，所有卡牌的逻辑行为都将通过一个结构化的JSON格式来定义。游戏引擎将负责解析这个结构并执行对应的游戏逻辑，而不是将卡牌效果硬编码在程序中。

**V3.1修订核心：** 新增 `COPY_EFFECT` 动作和 `usage_limit` 属性，以支持效果复制和“每场游戏一次”等限制性机制。

---

## 2. 顶层结构 (Top-Level Structure) - 已扩展

```json
{
  "id": "basic_01_qian",
  "name": "乾",
  // ... 其他元数据 ...
  "type": "basic",

  // "usage_limit" can be defined at the top level to apply to the entire card,
  // or within a specific effect/variant to apply only to that part.
  "usage_limit": {
    "scope": "GAME",
    "count": 1
  },

  "effect": {
    // 卡牌打出时立即执行的主动效果
  },

  "triggers": [
    // 卡牌在场时，被动监听并响应游戏事件的触发器
    {
      "condition": "ON_BEING_TARGETED",
      "params": { "source_type": "EFFECT_NEGATIVE" },
      "effect": {
        "action": "CHOICE",
        "params": {
          "target": "SELF",
          "options": [ { "description": "发动【心心相印】", "effect": { /* ... */ } } ]
        }
      }
    }
  ]
}
```

---

## 3. 效果 (Effect) 与 触发器 (Trigger) 详解

### 3.1 效果对象 (`effect`)
`"effect"` 对象定义了一个或一系列将要执行的动作。它可以包含 `cost`, `condition`, 和 `action` 数组。

```json
"effect": {
  "description": "可选的内部描述",
  "cost": [ { "resource": "gold", "value": 10 } ],
  "condition": { "op": "GREATER_THAN", "a": "VAR_SELF_YANG", "b": 3 },
  "actions": [
    { "action": "DEAL_DAMAGE", "params": { "target": "OPPONENT_SINGLE", "value": 5 } }
  ]
}
```

### 3.2 触发器对象 (`triggers`) - **V3.0 新增**
`"triggers"` 是一个数组，定义了卡牌如何被动地响应游戏事件。

**结构:** `{ "condition": "EVENT_TYPE", "params": { ... }, "effect": { ... } }`
- **元数据 (Metadata):** 触发器对象可以包含一个可选的 `"playable_from_hand": true` 键值对。当此值为 `true` 时，表示这张牌可以在满足触发条件时，直接从手牌中打出作为响应（详见 `game_rules.md` 7.3节）。

| 条件 (`EVENT_TYPE`) | 描述 | 示例参数 (`params`) |
| :--- | :--- | :--- |
| `ON_BEING_TARGETED` | 当此牌的拥有者成为一个效果的目标时 | `source_type`: `EFFECT_ALL`, `EFFECT_NEGATIVE`, `ATTACK` |
| `ON_PLAYER_ACTION` | 当任一玩家执行特定动作时 | `action_type`: `MOVE`, `PLAY_CARD_FUNCTION`, `ATTACK` |
| `ON_PHASE_START` | 在某个游戏阶段开始时 | `phase`: `UPKEEP`, `MOVEMENT`, `INTERPRETATION` |
| `ON_RESOURCE_CHANGE`| 当玩家资源变化时 | `resource`: `gold`, `health`; `change_type`: `GAIN`, `LOSS` |

---

## 4. 动作 (Action) - V3.1 大幅扩展

| 类型 | 描述 | 参数 (`params`) |
| :--- | :--- | :--- |
| **资源类** | | |
| `MODIFY_RESOURCE` | **（已废弃，见下）** | |
| `GAIN_RESOURCE` | 目标获得资源。用于奖励。 | `target`, `resource` (gold, health...), `value`, `source` |
| `LOSE_RESOURCE` | 目标失去资源。用于**非伤害性**的生命减少或金币损失。 | `target`, `resource`, `value` |
| `PAY_COST` | 玩家为发动效果支付代价。**与`LOSE_RESOURCE`在规则上严格区分。** | `target`, `resource`, `value` |
| `DEAL_DAMAGE` | 对目标造成伤害。可被防御/免疫。 | `target`, `value`, `damage_type` (physical, magical) |
| `SWAP_RESOURCES` | **(新增)** 交换两个目标指定的资源。 | `target_a`, `target_b`, `resource` |
| `SET_RESOURCE`| **(新增)** 将目标的资源直接设置为一个特定值。 | `target`, `resource`, `value` |
| `TRANSFER_RESOURCE`| **(新增)** 将资源从一个目标转移到另一个目标。 | `from`, `to`, `resource`, `value` |
| **移动与位置** | | |
| `MOVE` | 移动棋子。 | `target`, `destination`, `move_type` (normal, jump, force, retreat, away_from_player, towards_player, random_direction, normal_ignore_penalty) |
| `SWAP_POSITION` | 交换两个棋子的位置。 | `target_a`, `target_b` |
| **状态与规则** | | |
| `APPLY_STATUS` | 对目标施加状态。 | `target`, `status_id`, `duration`, `value`, `is_permanent` |
| `REMOVE_STATUS` | 移除目标状态。 | `target`, `status_id` (或 `ALL_NEGATIVE`, `ALL_POSITIVE`) |
| `MODIFY_RULE` | **(已增强)** 修改全局或玩家规则。 | `rule_id`, `scope` (必须), `mutation`, `duration` (必须), `rollback_condition` |
| **互动与信息** | | |
| `CHOICE` | 给予玩家一个选择。 | `target`, `options` (每个option包含description和effect) |
| `LOOKUP` | 查看隐藏信息。 | `target`, `info_type` (hand_cards, destiny_card) |
| `INTERRUPT` | **(新增)** 中断一个正在结算的动作。 | `target_action`, `interrupt_type` (CANCEL, REDIRECT) |
| `COPY_EFFECT` | **(新增)** 复制另一个效果。 | `target`, `source_effect`, `modifications`, `copy_semantics` (可选) |
| **卡牌与牌库** | | |
| `DRAW_CARD` | **(新增)** 目标从指定牌库抽牌。 | `target`, `deck` (basic, function), `count`, `reveal` (可选) |
| `DISCARD_CARD`| **(新增)** 目标弃牌。 | `target`, `count`, `source` (RANDOM, CHOICE_FROM_HAND) |
| `SWAP_HAND_CARDS`| **(新增)** 两人交换指定数量手牌。 | `target_a`, `target_b`, `count`, `atomic` (必须), `fallback_policy` (可选) |
| `SWAP_DISCARD_PILES`| **(新增)** 两人交换弃牌堆。 | `target_a`, `target_b`, `atomic` (必须), `fallback_policy` (可选) |
| `RECOVER_CARD_FROM_DISCARD`| **(新增)** 从弃牌堆回收牌到手牌。 | `target`, `deck`, `count` |
| **实体与场上效果** | | |
| `CREATE_ENTITY` | **(已增强)** 在棋盘上创建实体。 | `entity_type`, `position`, `owner`, `properties`, `max_instances` (可选) |
| `DESTROY_ENTITY`| **(新增)** 移除一个场上实体。 | `target_entity_id` |
| **游戏流程与规则** | | |
| `SKIP_PHASE` | **(新增)** 跳过一个游戏阶段。 | `phase` (INTERPRETATION, etc.) |
| `PROPOSE_ALLIANCE`| **(新增)** 向另一位玩家提议结盟。 | `target`, `duration`, `on_accept_effect` |
| `EXECUTE_LATER` | 延迟执行效果。 | `delay`, `effect`, `expiry_time` (必须), `max_turns` (可选) |
| `TRIGGER_EVENT` | 触发一个游戏事件（如“论道”）。 | `event_id` (EVENT_SONG, etc.), `participants` |

---

## 5. 参数详解 (Parameter Details) - V3.1 修订与扩充

### 5.1 `target` - 目标

*   **精确化玩家目标:**
    *   `SELF`: 动作的发起者。
    *   `EVENT_SOURCE_PLAYER`: 触发事件的玩家。
    *   `EVENT_TARGET_PLAYER`: 被事件指定的玩家。
    *   `ALLY_FORMAL_SINGLE`: **(新增)** 仅限通过《比》卦结成的单个盟友。
    *   `ALLY_FORMAL_ALL`: **(新增)** 所有正式盟友。
    *   `PLAYER_CHOICE_ANY`: **(新增)** 由发起者在所有玩家中任选一个。
    *   `OPPONENT_CHOICE_SINGLE`: 由发起者在所有敌对玩家中任选一个。
    *   `OPPONENT_ALL`: **(新增)** 所有敌对玩家。
    *   `ALLY_FORMAL_IN_PALACE`: **(新增)** 位于同一宫位的所有正式盟友。
    *   `ALLY_FORMAL_SINGLE_CHOICE`: **(新增)** 由发起者在所有正式盟友中任选一个。
    *   `PLAYER_CHOICE_ANY_NON_ALLY`: **(新增)** 由发起者在所有非盟友玩家中任选一个。
    *   `PLAYERS_IN_SAME_ZONE`: **(新增)** 位于同一区域的所有玩家（包括自己）。
    *   `OTHER_PLAYERS_IN_SAME_ZONE`: **(新增)** 位于同一区域的所有其他玩家。
    *   `PLAYER_CHOICE_RANDOM`: **(新增)** 在所有玩家中随机选择一个（包括自己）。
    *   `PLAYER_IN_NEW_ZONE`: **(新增)** 移动后新区域中的一名玩家。
    *   `OPPONENT_RANDOM`: **(新增)** 在所有敌对玩家中随机选择一个。

### 5.2 `status_id` - 状态效果

*   **精确化免疫状态 (新增):**
    *   `IMMUNE_COMBAT_DAMAGE`: 免疫战斗造成的伤害。
    *   `IMMUNE_EFFECT_DAMAGE`: 免疫卡牌效果造成的伤害。
    *   `IMMUNE_LIFE_LOSS`: 免疫不属于“伤害”的生命值减少。
    *   `IMMUNE_PENALTY`: 免疫【地部】或【奇门】等区域惩罚。
    *   `IMMUNE_THEFT`: 免疫偷窃/夺取金币的效果。
    *   `IMMUNITY_GENERAL_NEGATIVE`: 笼统的负面效果免疫（兜底）。
*   **其他关键状态:**
    *   `CANNOT_MOVE`: **(新增)** 目标不能移动。
    *   `CANNOT_PAY_COSTS`: **(新增)** 目标无法支付任何代价（一个负面状态）。
    *   `CANNOT_GAIN_GOLD_FROM_ZONE`: **(新增)** 目标不能从区域效果中获得金币。
    *   `HEXAGRAM_INVERTED`: 错卦状态。
    *   `POSITIVE_GAIN_DOUBLED`: 乾卦状态。
    *   `WAR_FORMATION`: **(新增)** 军阵状态。
    *   `RAPID_MARCH`: **(新增)** 急行军状态。
    *   `GENERAL`: **(新增)** 将帅状态。
    *   `PRESTIGE`: **(新增)** 威望状态。
    *   `MONTORIAL_FOG`: **(新增)** 启蒙之雾状态。
    *   `EFFECT_MODIFIER_CANCEL_NEGATIVE`: **(新增)** 取消效果负面部分的状态。
    *   `GUARD`: **(新增)** 守护状态，可抵挡固定数值的伤害。
    *   `MOVE_LIMIT`: **(新增)** 移动限制状态，限制目标的最大移动格数。
    *   `DAMAGE_BOOST`: **(新增)** 伤害加成状态，增加下一次造成的伤害。
    *   `IMPRISONED`: **(新增)** 禁锢状态，目标不能移动或抽牌。
    *   `EFFECTS_LOCKED`: **(新增)** 效果锁定状态，目标不能使用卡牌的核心机制。
    *   `ACTION_COST_INCREASED`: **(新增)** 行动代价增加状态。
    *   `UNSTOPPABLE`: **(新增)** 势不可挡状态，行动无法被响应或无效。
    *   `CARDS_LOCKED`: **(新增)** 卡牌锁定状态，目标不能打出卡牌。

### 5.3 `rule_id` & `mutation` - 规则修改 **(V3.0 增强)**

*   **新增 `rule_id`:**
    *   `FIVE_ELEMENTS_SYSTEM_ACTIVE`: 五行系统是否生效。
    *   `INTER_DEPARTMENT_MOVEMENT`: 天人地三部之间是否可移动。
    *   `YIN_YANG_SYSTEM_REVERSED`: 阴阳系统正负效果是否反转。
    *   `ZONE_REWARD_PENALTY_REVERSAL`: 泰/否卦的区域奖惩反转。
    *   `TURN_ORDER_REVERSED`: **(新增)** 回合顺序是否反转。
    *   `CARD_EFFECT_MOVEMENT_BLOCKED`: **(新增)** 卡牌效果导致的移动是否被阻止。
    *   `HAND_LIMIT_DRAW`: **(新增)** 抽牌阶段的手牌上限规则。
*   **`mutation` 对象:**
    *   `{ "type": "SET_BOOLEAN", "value": false }`: 开关规则。
    *   `{ "type": "SET_VALUE", "value": 0 }`: 设定数值规则（如移动上限）。
    *   `{ "type": "ADD_MODIFIER", "value": { "op": "MULTIPLY", "amount": 0.5 } }`: 增加修正。

### 5.4 `properties` - 实体属性 **(V3.0 新增)**

用于 `CREATE_ENTITY` 动作，定义场上实体的具体规则。
```json
"properties": {
  "name": "迷雾",
  "is_permanent": false,
  "duration": 3, // 回合
  "blocks_movement": { "for": "ALL_PLAYERS" },
  "on_enter_effect": { "actions": [ { "action": "LOSE_RESOURCE", "params": { "target": "EVENT_SOURCE_PLAYER", "resource": "gold", "value": 2 } } ] },
  "on_upkeep_effect": { /* ... */ }
}
```

### 5.5 `usage_limit` - 使用限制 **(V3.1 新增与强化)**
位于卡牌顶层，用于定义那些有使用次数限制的效果（如“每场游戏一次”）。

*   **`scope`**: `GAME`, `ROUND`, `PLAYER_LIFETIME`
*   **`count`**: 整数，表示可用的次数。
*   **`reset_timing` (必须):** 定义计数器何时重置。例如: `END_OF_ROUND`, `ON_STATUS_APPLIED(X)`.

### 5.6 `COPY_EFFECT` 参数 **(V3.1 新增)**
*   **`target`**: 谁来执行这个被复制的效果。
*   **`source_effect`**: 定义要复制哪个效果。这是一个结构化对象，详见 5.7 节。
*   **`modifications`**: 可选，对复制的效果进行调整。例如: `{ "remove_negative_parts": true }`

### 5.7 Contextual Data Sources

To avoid "magic strings," actions that need to reference dynamic game state (like a just-played card or an interrupted effect) must use a structured object.

**`source_effect` Object (for `COPY_EFFECT`)**
*   **Structure:** `{ "type": "SOURCE_TYPE", "player_scope": "PLAYER_SCOPE_VALUE" }`
*   **`SOURCE_TYPE` Values:**
    *   `LAST_BASIC_CARD_EFFECT_PLAYED`: The effect from the last *basic* card that was resolved. Used by 《坤》.
    *   `INTERRUPTED_EFFECT`: The effect that was just cancelled by an `INTERRUPT` action. This is specifically for creating "counter-spell" type effects, like with 《蒙》.
*   **`PLAYER_SCOPE_VALUE` Values:** (Optional) `SELF`, `OPPONENT_SINGLE`, `ANY`, `LAST_ACTED_PLAYER`, etc.

---

## 6. 示例：将《蹇》卦数据化 (新版)

**卡牌意图:** 在被攻击时，可以从手中打出此牌，无效化攻击，并后退一格。

**实现方式:**
1.  《蹇》牌本身没有 `effect`，只有 `triggers`。
2.  引擎规则：玩家可以在满足特定触发条件时，从手中打出带有该触发器的牌。

```json
// jian.json
{
  "id": "basic_39_jian",
  // ...
  "triggers": [
    {
      "condition": "ON_BEING_TARGETED",
      "params": { "source_type": "ATTACK" },
      "playable_from_hand": true, // **新增元数据，表示此牌可作为响应牌打出**
      "effect": {
        "description": "发动【知难而退】",
        "actions": [
          {
            "action": "INTERRUPT",
            "params": {
              // The engine infers the target action from the trigger's context.
              // For "ON_BEING_TARGETED" by an "ATTACK", it interrupts that attack.
              "interrupt_type": "CANCEL"
            }
          },
          {
            "action": "MOVE",
            "params": {
              "target": "SELF",
              "move_type": "RETREAT", // 后退一格
              "value": 1
            }
          }
        ]
      }
    }
  ]
}
```

---

## 7. 结论

V3.1 的数据结构通过引入**触发器**、**实体属性**，并**精确化**已有的动作、状态和目标，极大地增强了逻辑引擎的表达能力。新增的 `COPY_EFFECT` 动作和 `usage_limit` 属性，使得引擎能够以纯粹的数据驱动方式，支持响应式、全局规则修改、效果复制、次数限制等高级卡牌效果，为解决先前发现的逻辑冲突、漏洞和实现难题铺平了道路。