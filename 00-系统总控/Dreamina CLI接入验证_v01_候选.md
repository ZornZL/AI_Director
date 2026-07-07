# Dreamina CLI接入验证 v01 候选

> 本文件记录即梦 / Dreamina CLI 在 AiBianDao 项目中的首轮接入验证。当前结论为候选能力，不等同于已经建立稳定自动化生产闭环。

## 验证日期

- 日期：2026-06-20
- CLI来源：https://jimeng.jianying.com/cli
- 安装方式：隔离安装到项目内 `.tools/dreamina-cli/`，未写入系统 PATH
- 推荐入口：`.tools/dreamina-cli/dreamina.cmd`
- CLI版本：1.4.8
- 版本发布日期：2026-06-18
- 本地二进制 SHA-256：`4A4E06E80328607AA3203334AED36F306EC5105E88C5193156F5E09671335FBD`

## 已完成验证

1. 已从官方安装脚本确认 CLI 程序名为 `dreamina`。
2. 已下载 Windows 版 `dreamina.exe` 到项目隔离目录。
3. 已保存官方随包 `SKILL.md` 和 `version.json`。
4. 已读取根命令和视频相关子命令帮助。
5. 已完成 OAuth Device Flow 登录。
6. 已确认登录态可复用。
7. 已确认账户额度接口可用。
8. 已确认会话列表接口可用。
9. 已优化 Windows / Codex 沙箱下的日志路径问题：通过 `.tools/dreamina-cli/dreamina.cmd` 将 CLI 的运行态环境指向项目内隔离目录，避免非提权命令写入 `C:\Users\MSI\.dreamina_cli\logs` 时出现 `Access is denied`。
10. 已二次迭代包装入口：除 `USERPROFILE` / `HOME` 外，同时隔离 `APPDATA` / `LOCALAPPDATA`，让日志、元数据和潜在本地状态优先落到 `.tools/dreamina-cli/home/`。
11. 已记录本地二进制 SHA-256。注意：官方安装脚本未提供 Windows 二进制预期哈希，本值只能作为本地升级对比基线，不等同于官方验签。

## 当前账户状态

- user_id：866830490547972
- vip_level：maestro
- total_credit：2382
- 默认会话：0 / default

## 已确认的视频命令能力

### text2video

- 用途：纯文本生成视频。
- 支持模型：`seedance2.0`、`seedance2.0fast`、`seedance2.0_vip`、`seedance2.0fast_vip`、`seedance2.0mini`
- 支持画幅：`1:1`、`3:4`、`16:9`、`4:3`、`9:16`、`21:9`
- 分辨率：`seedance2.0_vip` 支持 `720p` 或 `1080p`；其他模型为 `720p`

### image2video

- 用途：单张图片驱动视频。
- 画幅由输入图片推断。
- 适合单首帧、单产品图、单人物图的镜头测试。

### frames2video

- 用途：首帧 + 尾帧驱动视频。
- 画幅由首帧推断。
- 适合 AiBianDao 的高控制力镜头测试，尤其是动作起止明确的镜头。

### multiframe2video

- 用途：多张图片形成连贯故事视频。
- 输入图片数量：2-20 张。
- 适合多关键帧连贯性测试，但不应在首轮测试中滥用。

### multimodal2video

- 用途：即梦 CLI 当前暴露的最强视频模式，对应“全能参考”。
- 支持输入：图片、视频、音频任意组合。
- 输入限制：图片 <= 9，视频 <= 3，音频 <= 3。
- 音频限制：2-15 秒。
- 支持模型：`seedance2.0`、`seedance2.0fast`、`seedance2.0_vip`、`seedance2.0fast_vip`、`seedance2.0mini`
- 支持画幅：`1:1`、`3:4`、`16:9`、`4:3`、`9:16`、`21:9`
- 时长：4-15 秒。
- 分辨率：`seedance2.0_vip` 支持 `720p` 或 `1080p`；其他模型为 `720p`。
- 备注：部分高内容安全风险模型首次使用前，可能需要在 Dreamina Web 端完成授权确认。

## 对 AiBianDao 当前系统的影响

CLI 接入后，系统可以新增“受控生成测试层”，但不应替代现有主流程。

当前主流程仍然保持：

```text
简单文案 -> 逻辑初审 -> 用户锁定 -> 导演脚本 -> 逐镜 Seedance 任务包
```

CLI 只应接在任务包确认之后：

```text
逐镜任务包确认 -> 高风险镜头 CLI 测试 -> 下载结果 -> 人工验收 -> 失败记录与单变量重试
```

## 当前推荐调用方式

在本项目内调用 Dreamina CLI 时，优先使用：

```powershell
& ".tools/dreamina-cli/dreamina.cmd" <subcommand> <args>
```

不要直接调用 `.tools/dreamina-cli/bin/dreamina.exe` 作为默认方式。直接调用可执行文件时，CLI 会尝试写入用户目录日志；在 Codex 沙箱身份下可能出现日志写入权限噪音。`.cmd` 入口会把 CLI 元数据、日志和潜在本地状态隔离在项目工具目录内，同时不修改系统 PATH。

当前 `.cmd` 入口会设置：

- `USERPROFILE=.tools/dreamina-cli/home`
- `HOME=.tools/dreamina-cli/home`
- `APPDATA=.tools/dreamina-cli/home/AppData/Roaming`
- `LOCALAPPDATA=.tools/dreamina-cli/home/AppData/Local`

涉及登录、查额度、提交生成、查询结果和下载媒体的命令都需要联网。提交生成任务前必须明确告知用户可能消耗额度，并获得确认。

运行态目录 `.tools/dreamina-cli/home/` 只用于本机 CLI 元数据、日志和可能的本地状态，不应进入项目归档或发布包。已在 `.tools/dreamina-cli/.gitignore` 中排除。

## 暂不建议直接全自动生产的原因

1. 当前项目尚未完成首条真实生产闭环。
2. CLI 会消耗账户额度，不能跳过人工确认。
3. 不同命令的模型、时长、画幅和参考素材限制不同，不能写死统一参数。
4. 视频质量不会因 CLI 自动提升，仍取决于资产、首尾帧、提示词和模型随机性。
5. 产品包装、中文文字、人物一致性、手部动作、对白口型仍是高风险点。
6. 如果出现 `AigcComplianceConfirmationRequired`，仍需用户在 Web 端确认。

## 推荐首轮真实测试范围

首轮不要批量生成整片，只做 1 个高风险镜头。

优先级：

1. 人物身份一致性镜头。
2. 最难动作镜头。
3. 产品包装或中文文字镜头。
4. 手部递接镜头。
5. 对白口型镜头。

每次真实生成必须记录：

- 项目 ID
- 镜头 ID
- 使用命令
- 模型版本
- 画幅
- 时长
- 输入资产路径
- prompt
- submit_id
- 初始状态
- 查询结果
- 下载路径
- 人工验收结论
- 失败原因
- 下一次单变量重试建议

## 建议下一步

当前已到 CLI 接入验证完成点。下一步建议由用户确认是否进入第一次真实高风险镜头测试。

确认前不应提交任何会消耗额度的生成任务。
