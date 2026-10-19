# AGENTS.md

给在这个仓库里工作的 AI 助手看的说明。

## 这是什么

一个 Claude Code Skill：在 BOSS 直聘上按固定规则筛选并投递 AI 产品 / FDE / Agent 类岗位。入口是 `SKILL.md`，防风控复盘和规则在 `docs/防风控规则.md`，脚本在 `scripts/`。

## 最高优先级

**防风控优先于投递数量。** 不得放宽 `scripts/limits.py` 的上限、不得删除异常即停逻辑、不得绕过 `scripts/run.py` 直接操作 BOSS 页面。要改上限，必须先得到用户明确同意，并在 `docs/防风控规则.md` 里写明原因。

## Git 版本管理（必须遵守）

- 本目录是 Git 仓库，远端是 GitHub 公开仓库 `origin`。
- **每一次修改（脚本、规则、文档）都要同步完成两步：本地 `git commit`，然后 `git push` 到远端。** 不允许只改不提交，也不允许只在本地提交不推送。
- 提交信息用中文写清楚改了什么、为什么改。
- 推送前检查：`git status` 干净、`git diff --cached` 里没有个人信息。

## 公开仓库的隐私边界

以下内容**只能留在本地，绝不能提交**（已写进 `.gitignore`）：

- `config.local.json`：浏览器空间编号、本地数据路径、过往公司名单
- 所有投递数据：已看岗位、读取记录、决策记录、当日报告、用量记录
- 姓名、简历内容、联系方式、账号信息

新增文件前先确认它不属于以上内容；如果不确定，先问用户。

## 目录

- `SKILL.md`：Skill 本体（流程、筛选规则、停止条件）
- `docs/防风控规则.md`：10-19 账号受限事故复盘与硬性规则
- `scripts/`：浏览器脚本和辅助工具
  - `run.py`：唯一的浏览器入口，负责限流和异常即停
  - `limits.py`：每日 / 每小时 / 每段时长上限、冷却期、当日停止标记
  - `guard.js`：页面状态检查（掉线、验证、受限）
  - `msearch.js` / `pread.js` / `psend.js`：搜索、右侧面板读 JD、发起沟通
  - `nx.sh` / `go.py` / `rej.py` / `log.py` / `show2.py` / `filt.py` / `verify.py`：队列、发送、记录、展示、预筛、核验
- `config.example.json`：配置模板（复制为 `config.local.json` 后填写）
