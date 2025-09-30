# 《天机变》 - 卡牌平衡性量化分析报告

> **生成时间:** 2025-09-28 08:29:36

## 1. 总体概览

- **分析卡牌总数:** 118
- **解析动作总数:** 292

## 2. 核心指标分析

### 资源变动
- **总金币产出:** 289
- **总金币消耗/损失:** 55
- **总生命恢复:** 76
- **总生命损失/支付:** 42
- **总伤害输出:** 60

### 卡牌优势与控制
- **总抽牌数:** 44
- **总弃牌数 (控制):** 29

## 3. 高风险动作使用情况

此部分列出了使用了高风险动作的卡牌，需要重点进行代码审查和游戏测试。

- **`MODIFY_RULE`:**
  - `basic_49_ge`
  - `basic_52_gen`
  - `basic_60_jie`
  - `basic_64_weiji`
- **`EXECUTE_LATER`:**
  - `basic_01_qian`
  - `basic_05_xu`
  - `basic_26_da_chu`
  - `basic_32_heng`
  - `basic_52_gen`
- **`COPY_EFFECT`:**
  - `basic_02_kun`
  - `basic_04_meng`

## 4. 动作频率分布

| 动作 (Action) | 使用次数 |
| :--- | :--- |
| `GAIN_RESOURCE` | 70 |
| `APPLY_STATUS` | 33 |
| `DRAW_CARD` | 32 |
| `LOSE_RESOURCE` | 28 |
| `DISCARD_CARD` | 25 |
| `MOVE` | 22 |
| `DEAL_DAMAGE` | 14 |
| `LOOKUP` | 8 |
| `CHOICE` | 8 |
| `EXECUTE_LATER` | 7 |
| `CREATE_ENTITY` | 5 |
| `DESTROY_ENTITY` | 5 |
| `REMOVE_STATUS` | 5 |
| `MODIFY_RULE` | 4 |
| `SKIP_PHASE` | 4 |
| `SWAP_HAND_CARDS` | 3 |
| `TRIGGER_EVENT` | 3 |
| `PROPOSE_ALLIANCE` | 3 |
| `COPY_EFFECT` | 3 |
| `PAY_COST` | 2 |
| `TRANSFER_RESOURCE` | 2 |
| `SWAP_RESOURCES` | 2 |
| `RECOVER_CARD_FROM_DISCARD` | 1 |
| `SET_RESOURCE` | 1 |
| `SWAP_POSITION` | 1 |
| `SWAP_DISCARD_PILES` | 1 |