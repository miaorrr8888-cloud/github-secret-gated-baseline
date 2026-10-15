# github-secret-gated-baseline

> Packaged by the WorkBuddy History Audit (2026-10-14). Source copied verbatim from the
> original location; **no modifications made to the original project**.

## 功能介绍
把一个本地项目做「密钥扫描闸门 → 测试闸门 → Git 基线提交 → 推送到自己的 GitHub 私有仓库 → 回验远端 commit」的可恢复基线。当用户要求「整理后上传到 GitHub」「建基线」「push 到私有仓库」「上传前做 secret scan」时使用。

## 起源与许可
- 类型: 用户原创 Skill (agent_created)
- 许可: MIT (见 LICENSE)
- 是否含密钥/Token: 否 (已通过审计扫描)

## 目录内容
- `SKILL.md` / `README.md` — 技能定义与使用说明
- 脚本与测试 — 见各子目录
- `LICENSE` — MIT

## 发布前检查清单
- [x] 无硬编码密钥 / Cookie / Token
- [x] 依赖清楚 (stdlib-only 或显式声明)
- [x] 含使用说明
- [ ] 作者补充中文/英文双语 README
- [ ] 补充 CI 测试 (如适用)

## 独立仓库

本仓库只包含 github-secret-gated-baseline 一个技能。
源码目录、SKILL.md、许可和相关测试均可独立取得，不依赖其他技能仓库。
工作记录与其他技能入口：[agent-skills-worklog](https://github.com/miaorrr8888-cloud/agent-skills-worklog)。

离线验证：`python -m unittest discover -s tests -v`。
