# 扬说财经 · 项目复盘报告

**日期：** 2026-06-01
**事件：** `deploy.sh` 因 `pre-deploy-check.sh` 脚本错误阻塞，无法完成自动部署
**影响：** 早报已生产完毕但 deploy.sh 推送失败，手动 git push 替代
**恢复手段：** 手动 `git add . && git commit && git push`

---

## 一、问题清单

### 1A — `elif [ $? -eq 1 ]` 并未捕获预期值

**文件：** `scripts/pre-deploy-check.sh` (审计段)
**根本原因：** Bash 中 `$?` 在 `elif` 上下文中捕获的是上一个命令的退出码，而非 `if` 条件中的命令。

```bash
# 错误写法
if python scripts/audit-article.py ...; then
    echo "通过"
    ((AUDIT_OK++))
elif [ $? -eq 1 ]; then          # ← $? 捕获的是 ((AUDIT_OK++)) 的退出码，不是 python 的！
    echo "警告"
fi
```

`((AUDIT_OK++))` 后增取值 0，`$?` = 1，导致 `elif [ $? -eq 1 ]` 始终为真，`AUDIT_WARN` 被错误增加。

### 1B — `set -e` + `((AUDIT_OK++))` 触发脚本提前退出

**根因：** `set -e` 恢复后，`((AUDIT_OK++))` 中 `AUDIT_OK` 初始为 0，表达式求值为 0，`((0))` 返回退出码 1，触发 `set -e` 中止整个脚本。

```bash
set -e
if [ "$AUDIT_RC" -eq 0 ]; then
    echo "通过"
    ((AUDIT_OK++))         # ← ((0)) → exit code 1, set -e 触发 → 脚本退出
fi
```

### 1C — Shell 脚本难以调试

- 无法通过单元测试验证行为
- 使用 `set -x` 才能发现执行路径
- 错误发生在非显眼的边界条件（`$?` 被消费、`((0))` 的特殊退出码）

### 1D — deploy.sh 无异常重试机制

- `deploy.sh` 使用 `set -e`，任何子脚本非零退出都会阻塞整个流程
- 无 fallback 逻辑或"跳过检查强制部署"选项

---

## 二、修复措施

| 问题 | 修复 |
|------|------|
| `$?` 捕获错误 | 改用独立变量 `AUDIT_RC=$?`，后续基于 `"$AUDIT_RC"` 判断 |
| `set -e` + `((0))` | 将 `set -e` 的恢复移到整个审计 `if/elif/else/fi` 块之后 |
| 审计脚本异常中断 | 用 `set +e` 包围 `python` 调用，防止非零退出传播 |

**修复后的正确模式：**

```bash
set +e
python scripts/audit-article.py --date "$TODAY" --edition morning 2>/dev/null
AUDIT_RC=$?
if [ "$AUDIT_RC" -eq 0 ]; then
    echo "✅ 早报审核通过"
    ((AUDIT_OK++))
elif [ "$AUDIT_RC" -eq 1 ]; then
    echo "⚠️ 早报审核有警告"
    ((AUDIT_WARN++))
else
    echo "❌ 早报审核阻塞"
    ((AUDIT_FAIL++))
fi
set -e    # 在审计块结束后恢复
```

---

## 三、教训与改进措施

### 3A — 立即执行

1. **对所有 shell 脚本中的 `$?` 使用进行审计**
   - 搜索 `elif.*\$?`、`\|\|.*\$?`、`&&.*\$?` 模式
   - 确保 `$?` 只出现在赋值后立即使用的语句中

2. **`((var++))` 在 `set -e` 下的使用规范**
   - 不允许裸 `((counter++))` 在 `set -e` 作用域中
   - 替代方案：`counter=$((counter + 1))` 或 `((counter++)) || true`

### 3B — 中短期改进

3. **deploy.sh 增加 `--force` 跳过检查选项**
   - 当预部署检查卡住时，允许用户绕过
   - 增加超时保护：子脚本超过 N 秒未完成视为失败而非阻塞

4. **shell 脚本关键路径加注释**
   - 对 `$?`、`set -e`、`(( ))` 等容易出错的构造加说明
   - 多行注释说明意图

### 3C — 长期改进

5. **关键 shell 脚本用 bats 或 shunit2 做单元测试**
   - 优先覆盖：退出码判断、`set -e` 交互、算术运算
   - CI 中集成 shell 脚本测试

---

## 四、时间线

```
10:41  git push: 发布早报（成功）
10:49  用户发现 content 标题更新后 deploy.sh 无法自动运行
10:50  排查：pre-deploy-check.sh 退出码 1，审计段 $? bug
10:51  deploy.sh 阻塞 → 手动 git push 部署
10:55  修复 $? bug（set +e/AUDIT_RC/set -e 在 fi 后）
11:00  发现 set -e + ((AUDIT_OK++)) 二次退出
11:05  最终修复：set -e 移出审计块
11:08  提交修复 + 写复盘
```

---

## 五、可迁移原则

1. **Bash 中 `$?` 只能立即赋值** — 跨语句的 `$?` 永远是陷阱
2. **`set -e` 下避免 `((incr++))`** — 值为 0 时 `((0))` 退出码为 1
3. **`set ±e` 的恢复时机要精确** — 括住最小必要范围，而非更多
4. **shell 脚本测试也值得写** — 当条件分支超过 3 路时，手动测试不再可靠
