# Contributing

感谢你考虑为 PM Scaffold 做贡献。这是一个 PRD-only 产品经理 AI 脚手架，核心原则是**业务真相由人类拥有、证据与不确定性可见、AI 不伪造人工确认**。

## 快速上手

```bash
git clone https://github.com/konwait12/pm-scaffold.git
cd pm-scaffold
bash run_tests_mac.sh                      # 全量回归（应全绿）
python3 src/scripts/consistency_check.py   # 跨文档一致性（应 0 errors）
```

核心脚本仅依赖 Python 3.10+ 标准库，无需 pip install。

## 目录约定

- `src/framework/workflow-registry.json` 是**唯一机器真相源**——新增/删除 skill 必须先改这里，不要硬编码路径。
- 每个 skill 必须保持统一丰富度：`SKILL.md`（统一执行协议）+ `references/`（7 类知识库）+ `agents/openai.yaml` + `scripts/validate_artifact.py` + `README.md`。
- 产物模板统一放 `src/templates/`，不要在 skill 内部重复存放。
- 历史文件不进 VCS（git 历史即归档），不要新增 `_archive/`。
- 新增/修改 skill 必须通过 `python3 src/scripts/registry_contract_check.py`（schema + 模板↔校验器字段闭环 E3_drift），任何 fail-loud 即不可合并。

## 提交规范

- 遵循 [Conventional Commits](https://www.conventionalcommits.org/)：`feat:` / `fix:` / `docs:` / `refactor:` / `chore:`。
- 每条 PR 必跑项（按序，前项失败即 abort）：
  1. `python3 src/scripts/registry_contract_check.py`（首项 fail-loud：schema + 模板↔校验器闭环 E3_drift，也是 `run_tests_mac.sh` 第一项）
  2. `bash run_tests_mac.sh`（全量回归，应 85/85 PASS）
  3. `python3 src/scripts/consistency_check.py`（跨文档一致性，应 0 errors）

## 行为守则

- 不往仓库提交任何真实姓名、邮箱、密钥、令牌或内部路径（fixtures 一律用占位符）。
- `confirmed` 状态永远不能由 AI 或脚本设置——这是项目的宪法级不变量，PR 不得绕过。
- 新校验器一律使用 `from validation_errors import make_issue` 输出统一错误格式（8+ 字段：severity / blocking / check_id / check_family / location / field_path / message / expectation / actual / repair_hint / source_ref），禁止直接 print stack trace 给用户；意外异常用 `validation_errors.wrap_unexpected` 包装。

## 如何贡献

1. Fork 仓库，基于 `main` 建分支。
2. 修改 + 新增测试（`test/skills/<id>/`）。
3. 跑全量回归，确保 0 failed。
4. 提交 PR，说明改动动机与影响面。
