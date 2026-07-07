# AI_Director

AI_Director 是一个以 Seedance 2.0 为中心的 AI 视频编导与逐镜任务编译系统。它由原本地项目 `AiBianDao` 迁移整理而来，目标是让核心规则、模板、训练知识和项目文档可以通过 GitHub 持续迭代，并在新电脑上通过 `git clone` 快速恢复。

## 当前定位

- 只生产 Seedance 2.0 / 即梦 AI 视频生成工作流，不规划真人拍摄。
- 核心能力是：简单文案 -> 逻辑审稿 -> 用户锁定 -> 导演脚本 -> Seedance 2.0 逐镜任务包。
- 每个生产镜头都应能独立复制到 Seedance 2.0，并包含参考、关键帧、逐秒动作、声音、连续性、验收标准和失败降级方案。
- 参考视频分析、训练入库、创意方向、脚本深化和复盘都需要保留人审确认节点。

## 快速开始

新电脑上克隆仓库：

```powershell
cd D:\
New-Item -ItemType Directory -Force D:\AI_Director
git clone https://github.com/ZornZL/AI_Director.git D:\AI_Director\AI_Director
```

在 Codex 中打开：

```text
D:\AI_Director\AI_Director
```

如果希望使用扁平目录，也可以直接克隆到 `D:\AI_Director`，但后续打开路径必须与实际 Git 根目录一致。

Windows PowerShell 读取中文 Markdown 时，建议先切到 UTF-8 输出，避免把正常文件显示成乱码：

```powershell
$OutputEncoding=[System.Text.Encoding]::UTF8
[Console]::OutputEncoding=[System.Text.Encoding]::UTF8
Get-Content -Raw -Encoding UTF8 .\从这里开始.md
```

新对话建议先发送：

```text
这是 AI_Director 项目的专职任务。
请先读取《START_HERE.md》、《从这里开始.md》、总索引和当前能力地图，
再按本次任务调用相关 Skill。只读取任务需要的资料。
```

## 目录结构

```text
AGENTS.md                         Codex 项目规则
START_HERE.md                     GitHub 友好的入口说明
从这里开始.md                    原中文新手入口
00-系统总控/                      总索引、能力地图、工作流、系统边界
01-品牌与产品库/                  品牌、产品资料与产品卡
02-编导训练库/                    案例、结构、钩子、审美偏好、失败经验
03-创意与选题库/                  创意提案与选题池
04-模板库/                        Seedance 任务包和复盘模板
05-角色与资产库/                  角色、品牌素材、产品素材和授权记录
06-视频制作项目/                  单条视频项目的轻量文档与记录
07-发布与数据复盘/                发布记录与数据复盘模板
08-归档/                          归档资料
.agents/skills/                   项目专属 Codex Skills
tools/                            轻量脚本工具
```

## GitHub 收纳原则

本仓库优先保存可长期迭代的文本知识、模板、规则和轻量记录。以下内容默认不提交到 GitHub：

- 视频、音频、成片、抽帧图片、素材大图。
- `.tools/` 里的本地 ffmpeg、Dreamina CLI、可执行程序。
- `.tmp/`、`.vs/`、`_analysis/` 等临时分析或 IDE 缓存。
- `.env`、Cookie、Token、账号凭据、平台登录态。

大型素材建议单独放在移动硬盘、网盘、NAS、Git LFS 或 GitHub Release 中，并在项目文档里记录引用关系。

## 常用 Git 流程

```powershell
git status
git add .
git commit -m "docs: update director workflow"
git push
```

更新到最新版本：

```powershell
git pull
```

## 版本

当前版本见 `VERSION`。重要变化记录在 `CHANGELOG.md`。
