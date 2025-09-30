## 天机变 — 卡牌数据风险分析与修复建议

更新时间: 2025-09-28

概要
- 本文档对仓库内卡牌数据中可能导致运行时逻辑冲突、不自洽或难以稳定实现的构造进行了归类、优先级评估，并给出可执行的引擎约定、linter 检测建议、以及优先修复步骤。

高阶结论（简短）
- 已完成静态一致性校验（所有 JSON 通过 `tools/lint_card_data.py`）。
- 静态合规不等于运行时安全：存在若干高危数据模式需要引擎层合同与额外检测（linter/单元测试）。
- 优先级（高->低）：全局规则修改（MODIFY_RULE）与回滚；延迟执行（EXECUTE_LATER）和超时/取消语义；中断/复制效果（INTERRUPT/COPY_EFFECT）与快照语义；实体创建/自引用导致的无限/递归循环；资源交换原子性；使用次数/恢复语义不明确。

1. 风险汇总（按严重性排序）

1.1 全局规则修改 (MODIFY_RULE) — 高
- 描述：卡牌/效果能修改游戏规则或基础行为（例如改变优先级、改变阶段定义、修改标记生命周期）。
- 典型文件例子：`assets/data/cards/basic/basic_64_weiji.json`（出现 MODIFY_RULE / rule-change 动作）
- 为什么危险：一旦规则被修改，后续所有效果的语义可能不再成立；若没有回滚/快照机制，极易导致不可预测、不可复现的状态。
- 引擎合同建议：
  - 所有规则修改必须产生可回滚的“规则事务”（RuleTransaction），并记录触发源与生存期（scope：turn/phase/duration）。
  - 修改前必须生成规则快照（差异形式），并在生效期结束或发生显式回滚时恢复。若多个规则修改并发，使用序列化合并策略并在日志中记录合并顺序。
  - 禁止在规则修改期间执行不确定的副作用（例如 EXECUTE_LATER 的回调）除非明确标注为“跨规则变更可执行”。
- Linter 建议：检测 `MODIFY_RULE` 的使用，确保：
  - 附带 `scope` 字段（turn/phase/persistent）和 `rollback_condition` 或 `duration`。
  - 不允许无 scope 的全局永久修改，除非在 card metadata 中有 `experimental: true` 标志。
- 建议优先级：修复/保护（高）。实现 ETA：引擎端 2-4 天（prototype），完整测试 1-2 周。

1.2 延迟执行 / 定时事件 (EXECUTE_LATER) — 高
- 描述：效果注册未来执行的动作（例如在某一阶段/回合后执行），但缺少超时、取消或失败语义。
- 典型文件例子：`assets/data/cards/basic/basic_01_qian.json`, `basic_05_xu.json`。
- 为什么危险：如果触发条件消失、相关实体不存在或规则已修改，延迟动作可能悬而未决或执行产生不合法操作，导致状态崩塌或死锁。
- 引擎合同建议：
  - 为所有延迟事件建立明确生命周期：trigger_time、expiry_time、cancel_conditions（例如实体死亡、zone 变更、rule rollback）。
  - 延迟事件在排队时进行参数快照（snapshot），以避免执行时引用已变的可变结构（除非效果被明确标注为“late-resolve”）。
  - 必须提供安全回退：当执行失败，应记录原因并按策略（no-op / compensate / revert）处理。
- Linter 建议：
  - 标记使用 `EXECUTE_LATER` 的卡牌，并要求 `expiry_time` 或 `max_turns` 字段存在。
  - 检测回调引用的外部标识（entity_id, card_id），并至少要求 `optional: true` 或 `snapshot_args` 字段。
- 建议优先级：修复/保护（高）。实现 ETA：1-3 天（引擎支持基本超时与快照）。

1.3 中断与复制效果 (INTERRUPT / COPY_EFFECT) — 中高
- 描述：中断式效果会在其他效果结算中插入，而复制效果会复制任意效果（可能含延迟或规则修改）。
- 典型文件例子：`assets/data/cards/basic/basic_04_meng.json`（COPY_EFFECT / INTERRUPT）；其他许多卡牌存在 COPY_EFFECT 调用。
- 为什么危险：复制复杂效果（包含 MODIFY_RULE 或 EXECUTE_LATER）会导致被复制的效果以不同上下文运行，若没有“快照语义”会产生意外行为；中断需要严格的优先级与回滚保障。
- 引擎合同建议：
  - 复制时必须决定深浅复制语义：对于 effects 应进行 deep snapshot（包括参数、引用、规则上下文），并标注复制的生存期与责任归属。
  - 中断需要在简化优先级三层模型下明确定义：中断是在哪一层发生？允许的副作用须列明。优先采用 `Cannot -> RulesChange -> Standard` 三层模型（请参照 `AGENTS.md` 指令）。
  - 若复制的效果包含延迟/规则修改，复制动作需被禁止或要求显式声明 `allow_rule_modification`。
- Linter 建议：
  - 标记使用 `COPY_EFFECT` 的文件，检查被复制效果是否含高风险动作（MODIFY_RULE, EXECUTE_LATER）。若是，要求添加 `copy_semantics` 字段（snapshot|reference|forbidden）。
- 建议优先级：中高。实现 ETA：1周（含测试）。

1.4 实体创建 / 递归引用 (CREATE_ENTITY / SELF-REFERENCE) — 中
- 描述：卡牌可以创建新实体（token/creature）或引用自身/同类实体，可能触发无限生成循环。
- 典型文件例子：`assets/data/cards/basic/basic_03_tun.json`（CREATE_ENTITY/DESTROY_ENTITY）；存在自引用模式的 function/natal 卡牌。
- 为什么危险：若存在 create-on-trigger-of-create 的链条，可能导致无限 loop、资源耗尽或卡牌池耗空。
- 引擎合同建议：
  - 对实体创建引入防护：每次触发建立创建深度计数（create_depth）或按回合/堆栈限制总创建次数。
  - 所有由卡牌创建的实体必须携带 provenance（源信息）用于调试与回滚。
  - 检查创建触发条件，新增 linter 规则标记可能的递归触发（例如 create -> on_create triggers create）。
- Linter 建议：
  - 检测 `CREATE_ENTITY` 且同时包含能再次触发 `CREATE_ENTITY` 的 trigger 字段；给出警告并要求 `max_instances` 或 `create_stack_limit`。
- 建议优先级：中。实现 ETA：2-4天（引擎与 linter 小改动）。

1.5 资源交换 / 置换 (SWAP_RESOURCE / SWAP_HAND_CARDS / SWAP_DISCARD_PILES) — 中
- 描述：多实体间交换资源或牌库/弃牌堆互换，若非原子操作可能产生不一致（部分完成的交换）。
- 典型文件例子：`basic_64_weiji.json`, `basic_03_tun.json`。
- 为什么危险：并发或中断导致半完成交换会出现资源丢失或重复。
- 引擎合同建议：
  - 所有交换操作必须是事务性的：先锁定相关实体/zones，执行交换并在成功时提交；若任一步失败则回滚到原始状态。
  - 对交换操作加入 `atomic: true` 标记；默认情况下交互式交换应为 atomic。
- Linter 建议：
  - 检测 `SWAP_*` 行为并要求 `atomic` 或 `fallback_policy` 字段。
- 建议优先级：中。实现 ETA：2-5 天（引擎端事务支持）。

1.6 使用次数 / 再生 (usage_limit semantics) — 低中
- 描述：卡牌含 `usage_limit` 或类似计数字段，但未定义重置时机（是否跨回合/永久/可被改变）。
- 典型文件例子：`assets/data/cards/basic/basic_63_jiji.json`, `basic_64_weiji.json`。
- 为什么危险：不明确的计数重置语义会导致玩家误解或规则漏洞（例如永久禁用某行为）。
- 引擎合同建议：
  - 所有 `usage_limit` 必须带 `reset_timing` 字段（e.g., end_of_turn, start_of_game, on_draw_phase）。
  - 引擎应提供统一 API 管理使用计数并在日志中记录消耗/恢复事件。
- Linter 建议：
  - 检测 `usage_limit` 并要求 `reset_timing` 与 `visible_counter` 字段。
- 建议优先级：低中。

2. 自动检测（建议加入 linter 的规则）
- A. 禁止无 scope 的 `MODIFY_RULE`（强制要求 scope 与 rollback info）。
- B. `EXECUTE_LATER` 必需附带 `expiry_time` 或 `max_turns`。
- C. `COPY_EFFECT` 当复制高风险动作（MODIFY_RULE/EXECUTE_LATER）时必须声明 `copy_semantics`。
- D. `CREATE_ENTITY` 如果可能触发再次创建（触发链）需声明 `max_instances` 或 `create_stack_limit`。
- E. 所有 `SWAP_*` 操作需声明 `atomic: true|false` 与 `fallback_policy`。
- F. `usage_limit` 必须有 `reset_timing`。

样例 linter 规则伪代码（Python）
```
if action == 'MODIFY_RULE' and not data.get('scope'):
    error('MODIFY_RULE must include scope (turn/phase/persistent)')

if action == 'EXECUTE_LATER' and not (data.get('expiry_time') or data.get('max_turns')):
    warn('EXECUTE_LATER should have an expiry_time or max_turns to avoid dangling events')
```

3. 建议的优先修复路线（可直接执行）
- 短期（立即，1-3 天）
  - 在 `tools/lint_card_data.py` 中加入上文“自动检测”规则 A/B/E/F 的实现并在 CI 中强阻断（错误级别）。
  - 对 `MODIFY_RULE`、`EXECUTE_LATER`、`COPY_EFFECT` 使用的卡牌打上 metadata 标签（例如 `review: required`），并生成一个待审清单。
- 中期（1-2 周）
  - 引擎添加规则事务与回滚 API（RuleTransaction），以及延迟事件的快照/expiry 机制。
  - 为复制效果定义快照语义并实现深拷贝/浅引用的选择。
- 长期（2-6 周）
  - 引擎完成事务/原子交换支持、创建限制与监控、并建立端到端测试（模拟数千局以验证没有无限循环与资源泄露）。

4. 建议的单元与整合测试
- 单元：
  - `MODIFY_RULE` 在 scope 到期、在 rollback 情况下能恢复原始行为。
  - `EXECUTE_LATER` 在实体消失或规则修改后能安全取消/补偿。
  - `COPY_EFFECT` 复制包含延迟/规则修改的效果时触发 error/warn 或按声明行为复制。
- 整合：
  - 编写若干微型对局序列，模拟可能的创建循环、交换竞态与中断插入，统计稳定性指标（无异常/无无限循环）。

5. 下一步（我将为你做的具体动作）
- 1) 把这个 `docs/risk_report.md` 提交到仓库（已完成）。
- 2) 在 `tools/lint_card_data.py` 中实现前述关键 linter 规则（我可以继续替你实现并运行测试）。
- 3) 如你同意，我会把 `MODIFY_RULE` / `EXECUTE_LATER` 使用的卡牌列为优先审查列表，并开始把这些卡牌补充缺失的字段（例如 scope、expiry_time）。

附录：已发现的高风险文件（非穷尽）
- `assets/data/cards/basic/basic_64_weiji.json` — MODIFY_RULE, SWAP_RESOURCE
- `assets/data/cards/basic/basic_03_tun.json` — CREATE_ENTITY / DESTROY_ENTITY
- `assets/data/cards/basic/basic_04_meng.json` — COPY_EFFECT / INTERRUPT
- `assets/data/cards/basic/basic_01_qian.json` — EXECUTE_LATER
- `assets/data/cards/basic/basic_05_xu.json` — EXECUTE_LATER
- `assets/data/cards/basic/basic_63_jiji.json` — usage_limit without reset_timing

若需要，我会继续：
- 实际修改 `tools/lint_card_data.py`（添加规则并在 CI 本地运行），
- 批量在卡牌 JSON 中补充缺失字段与 metadata, 并提交 PR。

结束。
