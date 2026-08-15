# Example 2 · Low-Density Degradation Run

> Reference candidate artifact demonstrating a correct **Low-Density Degradation** run.
> Input: single sentence, no attachments. Status: `needs_user_input`.
> Use as a comparison anchor when your input is under-supplied and you wonder whether you should still "fill the template".

## Input

- **SRC-001 · single user sentence** — "我想要一个按钮，用来点赞" (10 chars, no attachments)

## Run Trace

| Step | Time | Outcome |
|---|---|---|
| Preflight §1.1 | T+00:00 | Input sufficiency = **low-density** (10 chars < 50, no attachments) |
| Intake | T+00:00 | 1 SRC registered; business fact owner / goal decision owner = 待确认 |
| Think (7 lenses) | T+00:00 | **Skipped by rule** (Low-Density Degradation Mode) — density too low to support ideation |
| Clarify | T+00:00 | Output only: input sufficiency assessment + **8 batched clarifying questions** (Q-001..Q-008), each with AI preliminary judgment + options + impact + owner |
| Draft | T+00:01 | **No full 14-section artifact drafted** — by rule, Generate/Audit is skipped |
| Self-Audit | T+00:01 | `validate_artifact.py` returns `{"ok": true, "warnings": []}` |
| Human Gate | T+00:01 | Status = `needs_user_input`, waiting for human answers |

## What The Output Looks Like

```
# 项目背景与目标

## 0. Preflight 输入充分度判定
- 输入长度：10 字（< 50）
- 附件：无
- 判定：低密度退化模式 → 不进入 Generate，仅输出充分度评估 + 批量澄清

## 11. 待确认问题

| ID | 问题 | AI 初步判断与依据 | 选项/影响 | 决策人 | 阻断 | 延后风险 | 回写位置 |
|---|---|---|---|---|---|---|---|
| Q-001 | 谁、通过什么渠道、因为什么事件提出需求？ | 来源决定权威性；当前仅 1 句口语 | 5 个候选渠道 | 需求提出方 | 是 | 无法确认来源权威 | §1 需求来源与触发 |
| Q-002 | 所在产品 / 业务线？ | 偏 C 端内容消费 | 4 个候选领域 | 业务事实所有者 | 是 | 无法定位业务环境 | §2 项目与需求背景 |
| ... (共 8 题) |

## 12. 来源追溯
| SRC-001 | 用户口语输入 | 我想要一个按钮，用来点赞 | 来源为单句，无业务权威 |

## 14. Constitution Compliance
| ① 输入充分度判定 | PASS | §0 明确按 §1.2 低密度退化模式处理 |
| ② 路由回执结构 | PASS | §11.5 三字段（routed_to / routing_reason / routing_target_capability） |
```

## Why This Is A Good Example

1. **It stops.** A "good" answer to a 10-char input is not a 14-section artifact — it is a focused question batch that moves the project forward.
2. **It marks skipped steps.** §0 Preflight documents *what was skipped and why* (lens ideation, drafting) so human reviewers can audit the AI's restraint.
3. **It keeps sources honest.** SRC-001 is a single oral sentence; the artifact does not pretend it is a meeting transcript.
4. **It preserves routing out.** §11.5 holds the 3-field routing receipt even though no routing-out occurred, keeping the format consistent.
5. **Zero warnings.** Low-density artifacts pass `validate_artifact.py` cleanly — under-supplied input is not a failure state.

## Common Traps To Watch

- ❌ **Drafting the full 14 sections anyway** — this is the classic failure: AI "fills the template" with `待确认` everywhere, producing a verbose artifact that says nothing.
- ❌ **Running the 7 lenses** — at 10 chars of input, every lens degenerates into "信息不足", wasting tokens and attention.
- ❌ **Inventing business facts** — guessing "用户是 C 端" without the user saying so, then recording it as `FACT`.
- ❌ **Forgetting the routing receipt** — if the input is actually a UX request ("画个页面"), you must output the 3-field `routed_to / routing_reason / routing_target_capability` receipt instead of proceeding.

## Cross-Reference

- See `SKILL.md` §1.1 (Input Sufficiency Gate) and §1.2 (Low-Density Degradation Path).
- See `references/thinking-framework.md` § Low-Density Degradation Mode.
- See `references/output-contract.md` for status `needs_user_input` semantics.