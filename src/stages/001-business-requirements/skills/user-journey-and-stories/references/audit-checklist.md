# 审计清单 · user-journey-and-stories

每次人工交接前先自审。先运行确定性校验器，再应用本清单。

## 1. 结构闸门（Structural Gate）

- [ ] Frontmatter：全部 11 个字段齐全（10 个标准字段 + `upstream_artifact_id`）
- [ ] 全部 12 个必需章节存在（§0–§12）
- [ ] 上游产物 ID 是一个合法的已确认 background-goal 产物
- [ ] 状态是 6 种合法状态之一
- [ ] §9 中至少有一个 SRC-* 引用映射到某个上游来源
- [ ] 如果状态是 `confirmed`，所有确认字段都已填写

## 2. 上游可追溯闸门（Upstream Traceability Gate）

- [ ] §0 核验上游产物存在且已确认
- [ ] §1 生命周期阶段可追溯到上游 §13 生命周期线索
- [ ] §2 旅程角色与上游 §6 已确认角色一致
- [ ] §2 痛点引用上游 §4 核心问题
- [ ] §6 事实引用上游来源 ID
- [ ] §9 来源表映射到上游 §12 来源追溯

## 3. 旅程图质量闸门（Journey Map Quality Gate）

- [ ] 旅程按生命周期阶段（行）× 角色（列）组织，而不是按页面/屏幕
- [ ] 每个有内容的（阶段 × 角色）单元格都包含：触发、动作、触点、痛点、期望结果、路径类型、来源、知识状态
- [ ] 背景未暗示但逻辑上必要的生命周期阶段被标记为 UNKNOWN
- [ ] 旅程图中至少出现一个角色
- [ ] 没有凭空发明、无上游证据的角色——若为推导所得则标注 AI_INFERENCE

## 4. 故事卡片质量闸门（Story Card Quality Gate）

- [ ] 每条故事卡片使用规范格式：`在〈前提/场景〉下，作为〈角色〉，我希望〈动作〉，以便〈目标/价值〉`
- [ ] 每条故事卡片都有来源旅程条目引用
- [ ] 故事卡片按角色或史诗主题分组
- [ ] 优先级提示受上游 §5 目标启发
- [ ] 故事 ID 顺序连续（ST-001, ST-002, ...）且唯一

## 5. 覆盖闸门（Coverage Gate）

- [ ] §4 覆盖矩阵把每个非空旅程条目映射到 ≥ 1 张故事卡片
- [ ] §5 路径类型覆盖检查全部 6 种类型（normal/alt/exception/failure/handoff/recovery）
- [ ] 无解释的缺口都标了原因
- [ ] 孤儿故事卡片（无来源旅程条目）被标记并说明理由

## 6. 知识状态闸门（Knowledge State Gate）

- [ ] §6 FACT 条目有来源证据
- [ ] §7 ASSUMPTION 条目有依据和负责人
- [ ] §7 AI_INFERENCE 条目被如实标注（不被冒充为 FACT）
- [ ] §7 CONFLICT 条目保留双方——不静默解决
- [ ] §7 UNKNOWN 条目有指定负责人与影响评估

## 7. 语义红旗（Semantic Red Flags，与 `project-background-goal` 同一精神）

检查：

1. 显示"可评审"但旅程图 < 2 个生命周期阶段 → 很可能分解不足
2. 有故事卡片但没有旅程条目 → 缺少上游可追溯
3. 旅程图提到了上游 §6 之外的角色 → 凭空内容
4. 所有故事都是 normal 路径 → 缺少 exception/failure/recovery 覆盖
5. 故事卡片描述 UI 交互（"点按钮"、"打开页面"）→ 过早的 UX 设计
6. 覆盖矩阵有缺口却不带原因 → 审计不完整

## 8. 人工闸门（Human Gate）

- [ ] 所有阻断性 Clarify Session 都有被接受的答案
- [ ] Clarify Session 不超过 5 个；若 6 个以上，则 `needs_user_input`
- [ ] 正文中的 `待确认` 都是有意的非阻断项
- [ ] Constitution Compliance §11 的 4 条原则都已评估（不是 `待确认`）
- [ ] 下游交接摘要（§10）足够完整，product-ux 可直接消费

## 9. 回归闸门（Regression Gate）

- [ ] `python3 scripts/validate_artifact.py <artifact.md> --json` 返回 `"ok": true`
- [ ] 模板本身通过校验器
- [ ] 至少一个 fixture 覆盖充足模式
- [ ] 至少一个 fixture 覆盖降级模式
