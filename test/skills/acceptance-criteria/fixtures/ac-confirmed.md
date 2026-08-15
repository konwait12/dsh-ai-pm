## 7. 验收依据

| ID | 验收标准（Given/When/Then） | 量化阈值 | 来源目标 G | 所属 FUN | 优先级 |
|---|---|---|---|---|---|
| AC-001 | Given 用户已登录, when 提交, then 成功 | ≤3s | G2 | FUN-001 | P0 |
| AC-002 | Given 网络异常, when 提交, then 重试提示 | — | G2 | FUN-001 | P1 |
| AC-003 | Given 字段为空, when 提交, then 校验错误 | — | G2 | FUN-001 | P1 |
