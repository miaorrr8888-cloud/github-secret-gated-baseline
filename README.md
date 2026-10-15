# GitHub 上传前凭证检查

`github-secret-gated-baseline` · 独立技能仓库 · MIT

适合：准备把本地项目开源的开发者、AI 工具使用者

## 解决什么问题

在提交前尽早发现常见凭证格式和敏感文件，确认检查的确是即将提交的内容。

## 快速开始

Python 3.10+；--tracked/--staged 需要 Git。运行目录就是检查范围。

在本仓库根目录运行：

```sh
python scripts/gate_scan.py
# 暂存后检查：
python scripts/gate_scan.py --staged
```

## 输入与输出

**输入**：当前仓库。无参数扫描本地文件；--tracked 扫描 Git 跟踪文件的工作区内容；--staged 检查待提交内容。空范围会报错。

**输出**：PASS/FAIL/ERROR、路径和类别，不输出凭据值。退出码 0=通过，1=发现问题，2=输入或扫描错误。

## 本次完善

原有缺口：工作区扫描可能与暂存内容不同；部分含 sample 字样或短口令的字面值被误忽略；冻结清单可能读到敏感输入。

已补：新增 --staged 检查 Git 暂存版本；收紧占位符判断；冻结清单跳过凭证、浏览器数据、依赖和符号链接；补对应回归测试。

## 仍然缺什么

仍是启发式模式扫描，可能漏报和误报；不能替代专业秘密扫描器、远程历史审查或已泄露密钥的吊销。

## 验证与使用注意

```sh
python -m unittest discover -s tests -v
```

测试覆盖被断言的离线行为，不等于真实平台、生产模型或业务效果验证。

示例数据和图片均为合成演示，不是真实客户、交易、销量或模型成绩。不要提交真实凭据和私有输入。

## 来源与工作记录

由 miaorrr8888-cloud 在 AI 辅助下积累和维护，来源与边界见 [PROVENANCE.md](PROVENANCE.md)，许可见 [LICENSE](LICENSE)。

[全部独立技能与阶段性工作记录](https://github.com/miaorrr8888-cloud/agent-skills-worklog)
