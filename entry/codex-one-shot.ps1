# Usage: pwsh -File entry/codex-one-shot.ps1 -Rule "tmdb-272118-s1 (小城日常)"
# Prints a one-shot Codex CLI prompt to auto implement+test+push.

param(
  [Parameter(Mandatory = $true)]
  [string]$Rule
)

$prompt = @"
为这部剧生成规则：$Rule
自行完成测试。测试完成以后，diff use all change,根据修改记录生成commit msg.
最后提交修改并完成推送。

要求：
- 严格遵循仓库的“Repository Guidelines”。
- 规则放在 
  Python: 
    - 生成/更新 
      - 移动策略工厂：
        - 源码：src/tools/move/implementations.py（使用 @factory.register("<key>")）
        - 接口：src/tools/move/interfaces.py（Mover 类型）
        - 默认行为：default_move / hardlink
      - 新增/完善 Pytest：tests/test_mover_<key>.py（仿照现有用例）
    - 运行测试：pytest -q
  Git:
    - 基于全部改动生成 Conventional Commits 风格信息（feat(move): ... / fix(move): ... / chore(entry): ...）。
    - 提交和推送到当前分支。

现在开始。
"@

Write-Output $prompt

