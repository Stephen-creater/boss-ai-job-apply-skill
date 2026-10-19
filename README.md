# boss-ai-job-apply-skill

一个 Claude Code Skill：用 ego-browser 在 BOSS 直聘上按规则筛选并投递 AI 产品 / FDE / Agent 类岗位（杭州、上海）。

- 用法与筛选规则：见 [SKILL.md](SKILL.md)
- 防风控复盘与硬性规则：见 [docs/防风控规则.md](docs/防风控规则.md)
- 协作与 Git 规范：见 [AGENTS.md](AGENTS.md)

## 快速开始

1. 复制 `config.example.json` 为 `config.local.json`，填写浏览器空间编号、数据目录、当天记录目录名、过往公司名单。
2. 把本目录链接到 Claude Code 的 skills 目录：`ln -s "$(pwd)" ~/.claude/skills/boss-ai-job-apply`
3. 每次操作前运行 `python3 scripts/limits.py` 查看当天用量和是否处于停止状态。

## 安全设计

- 所有浏览器操作经 `scripts/run.py`，自动执行每日 / 每小时 / 每段时长上限。
- 检测到掉线、验证码、访问受限等任何异常，立即写入当日停止标记，当天不再操作。
- 只在搜索页右侧面板读 JD，不直接打开详情页；单标签页串行；随机停顿。
- 不上传简历、附件、电话、邮箱。

个人配置和投递数据不在仓库中（见 `.gitignore`）。
