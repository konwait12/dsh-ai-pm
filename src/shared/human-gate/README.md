# Human Gate And Revision Loop

Every main work item stops after Audit. The authorized human chooses `approve` or `changes`; skipping is not approval.

On changes: record added/modified/removed content and downstream impact, update the candidate, rerun Audit, and resubmit. Three repeated failures on the same issue trigger a direction review rather than another blind edit. Ten total revision rounds block the item for owner escalation.

Only `pipeline.py ... review --decision approve --reviewer <name>` may create a confirmed baseline. Non-interactive mode and simulated identities cannot approve.

## 评审修改循环（B1）操作细则

**机器路径（现状，见上文）**：`review --decision changes` → 记录 delta（新增/修改/删除与下游影响）→ 更新候选产物 → 重跑 Audit → 重回 Human Gate 复送。

**人工细则（B1 补充）**：驳回后的修改按 doc-coauthoring 技法（Context Gathering → Refinement & Structure → Reader Testing 三阶段）改写为四步，保证每轮修改有清单、有确认、有终验：

1. **评审驳回 → 修改清单（RevisionListRecord）**：把评审意见逐条转成清单，每条记录「改哪里（产物章节/条目定位）/ 改成什么（目标表述）」。只列可落地条目；「写得更好」类泛泛意见先回问评审者，澄清成可操作表述后再入清单。
2. **逐项确认**：清单逐条与评审者确认——改/跳过/合并，并请其给一句理由（理由用于判断下游影响范围）。确认后的清单才是本轮修改范围，未确认条目不动。
3. **执行修改**：按清单逐条改产物并标记 done；落点对照 `revision-templates/modification-record.md`（Before/After/Reason/Downstream Impact）登记，只动清单内条目，不重印全文。
4. **Reader 视角终验**：以「无上下文新读者」视角重读修改后产物——评审意见是否真正解决？有无新引入的歧义/自相矛盾/缺失引用？（对应 doc-coauthoring 的 Reader Testing：预测读者会问的问题，逐条核对产物能否回答。）终验通过才进入重跑 Audit。

**分工边界**：机器路径负责状态流转与记录（delta、Audit、状态机、`--decision` 语义）；人工细则负责修改过程质量（清单化、逐项确认、Reader 终验）。衔接点：RevisionListRecord 确认并终验后，才触发机器路径的 delta 记录与 Audit 重跑。三次同类驳回触发方向性复盘、十轮封顶转 owner 升级（沿用既有规则，不重复）。
