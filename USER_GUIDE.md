# 代码上传前的凭证风险检查：用户使用指南

## 它能帮你做什么

扫描本地文本、Git待提交版本与有限范围的历史文本，报告可疑位置和类别，不输出命中的凭据值。

## 适合谁

准备公开项目的开发者、使用AI写代码的开源新手。

## 具体解决什么问题

准备上传的文件可能夹带常见凭证格式，工作区干净也不代表待提交版本或历史提交没有问题。

**不适合这些目标：**完整安全审计、证明绝不会泄露、自动吊销凭据或自动清洗全部历史。

## 下载与准备

- [打开独立仓库](https://github.com/miaorrr8888-cloud/github-secret-gated-baseline)
- [直接下载源码ZIP](https://github.com/miaorrr8888-cloud/github-secret-gated-baseline/archive/refs/heads/main.zip)

也可在仓库页面点 Code → Download ZIP。解压后打开包含 SKILL.md、README.md、USER_GUIDE.md 的那层文件夹。不要停在外层目录或只复制一个脚本。

建议使用Windows电脑和Python 3.12；这是本次验证环境。先在该文件夹打开PowerShell，再执行：

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe --version
```

这里直接使用虚拟环境里的Python，不需要运行激活脚本或修改系统执行策略。安装步骤及其他系统说明见[通用安装说明](https://github.com/miaorrr8888-cloud/agent-skills-worklog/blob/main/INSTALLATION.md)。

本指南的基础示例只用Python标准库，无需安装第三方Python包。

## 第一次使用：先跑自带示例

先扫描技能目录本身，理解报告格式；再对自己的明确项目范围选择暂存检查或历史检查。

```powershell
.\.venv\Scripts\python.exe scripts/gate_scan.py
```

## 结果怎么看

输出 SECRET_SCAN=PASS/FAIL/ERROR。FAIL时看 HIT 的相对路径和类别；不要把凭据内容复制到评论或截图。此演示只检查技能目录本身。

## 换成自己的资料

运行命令所在目录就是扫描范围。--staged 检查Git暂存区；历史扫描需一个真正的Git仓库。GitHub下载ZIP不包含Git历史。

进入你自己的项目根目录，用此技能中脚本的完整路径运行；先确认目录范围，再使用 --staged。历史检查用 scan_history.py 项目路径 --limit 100，记录是否被截断或跳过。

## 不想手动敲命令：给AI助手的任务

以下任务适用于能读取所选目录、执行本地命令的助手。WorkBuddy需要先确认当前版本的权限与技能启用状态；本项目未完成WorkBuddy实际导入验收。

```text
请先读取我选定文件夹中的 SKILL.md 和 USER_GUIDE.md，只在该项目范围内处理。
先仅扫描此技能文件夹，解释PASS、FAIL、ERROR和扫描范围。需要检查我的其他项目时，先让我给出明确路径；不要扫描整个电脑、不要读取浏览器凭据、不要打印密钥值或替我推送代码。
缺少依赖时先说明用途，优先放进本项目虚拟环境；不要读取其他目录中的密码、密钥或浏览器登录数据。
```

## 常见问题

**ZIP里不能扫历史**

ZIP没有.git历史。使用你已有的Git仓库，或按自己的权限克隆目标仓库后再扫描。

**空暂存区返回ERROR**

先确认是否已有要提交的文件；空范围不等于已经检查通过。

**找不到文件或脚本**

确认终端当前目录就是包含SKILL.md的技能根目录；路径含空格时加双引号。输出目录已存在时换新名字，不覆盖已有结果。

## 当前能力边界

默认历史扫描最多100个可达提交，超大或二进制文件会跳过。模式扫描可能漏报与误报；发现真实泄露应轮换凭据，删当前文件不能代替处理泄露。

## 验证范围

本指南示例已在Windows独立副本中运行复核，见[命令复核结果](https://github.com/miaorrr8888-cloud/agent-skills-worklog/blob/main/USER_GUIDES_VERIFICATION.md)。已有回归测试只覆盖被测试行为，不证明真实业务结果。WorkBuddy实际运行、手机端使用和所有系统版本均不在本次已验证范围内。

许可证和素材来源分别见 [LICENSE](LICENSE)、[PROVENANCE.md](PROVENANCE.md)。
